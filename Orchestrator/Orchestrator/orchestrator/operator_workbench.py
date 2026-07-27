"""Loopback-only Operator Workbench V1 for one bounded canonical task.

This is deliberately an adapter, not another execution runtime.  It creates a
canonical packet, launches the canonical CLI with a fixed worker selection,
then renders the lifecycle records that CLI persisted.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import secrets
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.alpha_runtime import isolated_data_root
from orchestrator.current_success_acceptance import record_current_success_result_acceptance
from orchestrator.operator_packet_result_decision import record_packet_result_operator_decision

TRUST_POSTURE = "trusted_local_unsandboxed"
ALLOWED_PREFIX = "workbench_fixtures/"
MAX_OUTPUT_CHARS = 12000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    if not value.startswith(ALLOWED_PREFIX) or ".." in value.split("/") or value.endswith("/"):
        raise ValueError(f"Only relative paths below {ALLOWED_PREFIX} are supported by Workbench V1.")
    return value


def _text(value: Any, *, limit: int = 4000) -> str:
    return str(value or "").strip()[:limit]


def packet_from_form(form: dict[str, str], *, authorized: bool = False) -> dict[str, Any]:
    title = _text(form.get("title"), limit=180)
    objective = _text(form.get("objective"), limit=4000)
    path = _safe_path(_text(form.get("path")))
    expected = str(form.get("expected_output") or "")[:4000]
    validation = _text(form.get("validation"), limit=1000) or "Declared output exists and matches the expected output."
    if not title or not objective or not expected.strip():
        raise ValueError("Title, objective, and expected output are required.")
    identifier = uuid4().hex[:12]
    return {
        "packet_id": f"workbench_packet_{identifier}", "run_id": f"workbench_run_{identifier}", "task_id": f"workbench_task_{identifier}",
        "title": title, "files_in_scope": [path], "success_criteria": [validation], "expected_output": expected,
        "provider_name": "subprocess_worker", "execution_policy": "filesystem_mutation", "worker_trust_posture": TRUST_POSTURE,
        "authorization_decision": "authorize_execution" if authorized else "preview_only",
        "authorization_provenance": "workbench_operator_deliberate_action" if authorized else "",
        "authorization_constraints": ["one active Workbench run", f"declared path must remain below {ALLOWED_PREFIX}"],
        "workbench_objective": objective,
        "commit_authorized": form.get("commit_authorized") == "true", "push_authorized": form.get("push_authorized") == "true",
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


class Workbench:
    def __init__(self, root: Path, data_root: Path) -> None:
        self.root, self.data_root = root.resolve(), data_root.resolve()
        self.runtime_root = Path(__file__).resolve().parents[1]
        self.csrf = secrets.token_urlsafe(24)
        self.lock = threading.Lock(); self.active: dict[str, Any] | None = None

    def worker_command(self, selection: str) -> list[str]:
        # The browser selects a named, supported worker only; it never supplies a command.
        if selection == "fixture":
            return [sys.executable, "-m", "orchestrator.operator_workbench_fixture_worker"]
        if selection == "codex":
            # Keep the browser on a named worker.  The adapter owns the fixed
            # native binary path and the canonical worker-JSON translation.
            return [sys.executable, "-m", "orchestrator.operator_workbench_codex_worker"]
        raise ValueError("Select a supported worker.")

    def start(self, form: dict[str, str]) -> dict[str, Any]:
        with self.lock:
            if self.active and self.active.get("state") == "executing":
                raise ValueError("One Workbench run is already executing.")
            packet = packet_from_form(form, authorized=True)
            worker = _text(form.get("worker"))
            command = self.worker_command(worker)
            timeout = _text(form.get("timeout")) or "600"
            packet_dir = self.data_root / "workbench_packets"; packet_dir.mkdir(parents=True, exist_ok=True)
            packet_path = packet_dir / f"{packet['packet_id']}.json"; packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
            argv = [sys.executable, "-m", "orchestrator.operator_coding_task_packet_cli", "--packet-json", str(packet_path), "--data-root", str(self.data_root), "--trusted-worker-posture", TRUST_POSTURE, "--worker-timeout-seconds", timeout, "--worker-command", *command]
            item = {"state": "executing", "started_at": _now(), "packet": packet, "worker": worker, "command": "configured_named_worker", "process_state": "starting", "stdout": "", "stderr": "", "result": None}
            self.active = item
            threading.Thread(target=self._run, args=(item, argv), daemon=True).start()
            return self.status()

    def _run(self, item: dict[str, Any], argv: list[str]) -> None:
        try:
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(self.runtime_root) + (os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else "")
            process = subprocess.run(argv, cwd=self.runtime_root, env=environment, capture_output=True, text=True, timeout=3700)
            item["stdout"], item["stderr"] = process.stdout[-MAX_OUTPUT_CHARS:], process.stderr[-MAX_OUTPUT_CHARS:]
            try: item["result"] = json.loads(process.stdout)
            except json.JSONDecodeError: item["result"] = {"accepted": False, "blocked": True, "detail": "Canonical CLI returned non-JSON output."}
            review_ready = item["result"].get("final_task_status") == "needs_review" or bool(item["result"].get("current_success_review", {}).get("ready_for_operator_review"))
            item["state"] = "awaiting_review" if review_ready else "failed"
            item["process_state"] = f"exited:{process.returncode}"
        except subprocess.TimeoutExpired:
            item.update({"state": "stopped", "process_state": "workbench_launcher_timeout", "result": {"blocked": True, "detail": "Workbench launcher timeout."}})
        finally: item["ended_at"] = _now()

    def disposition(self, decision: str, reason: str) -> dict[str, Any]:
        item = self.active
        if not item or item.get("state") != "awaiting_review": raise ValueError("A completed run awaiting review is required.")
        task_id = item["packet"]["task_id"]
        with isolated_data_root(self.data_root):
            if decision == "accept":
                record = record_current_success_result_acceptance({"task_id": task_id, "accepted": True, "operator_note": reason, "verification_caveat_acknowledged": True, "provider_caveat_acknowledged": True})
                if not record.get("acceptance_record_created"):
                    raise ValueError(record.get("reason") or "Canonical acceptance record was not created.")
                item["state"] = "accepted"
            elif decision in {"reject", "correction_required"}:
                record = record_packet_result_operator_decision({"task_id": task_id, "packet_id": item["packet"]["packet_id"], "operator_decision": "rejected", "operator_note": reason or decision})
                if not record.get("operator_decision_record_created"):
                    raise ValueError(record.get("reason") or "Canonical operator decision record was not created.")
                item["state"] = "rejected" if decision == "reject" else "correction_required"
            else: raise ValueError("Unsupported disposition.")
        item["disposition"] = record; return self.status()

    def _evidence(self, packet: dict[str, Any]) -> dict[str, Any]:
        task = _read_json(self.data_root / "tasks" / f"{packet['task_id']}.json") or {}
        artifact = _read_json(self.data_root / "artifacts" / f"{task.get('execution_artifact_id', '')}.json") or {}
        state = _read_json(self.data_root / "worker_execution_states" / f"{packet['run_id']}__{packet['task_id']}.json") or {}
        verifier = next(iter((self.data_root / "verifier_results").glob(f"{packet['task_id']}_*.json")), None) if (self.data_root / "verifier_results").exists() else None
        return {"task": task, "artifact": artifact, "worker_state": state, "verifier": _read_json(verifier) if verifier else {}, "data_root": str(self.data_root)}

    def status(self) -> dict[str, Any]:
        item = self.active
        if not item: return {"state": "idle", "data_root": str(self.data_root)}
        return {**item, "elapsed_seconds": round(time.time() - datetime.fromisoformat(item["started_at"]).timestamp(), 1), "evidence": self._evidence(item["packet"])}


def render_html(workbench: Workbench) -> str:
    token = html.escape(workbench.csrf, quote=True)
    return f"""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Operator Workbench V1</title><style>body{{font:16px system-ui;max-width:1100px;margin:auto;padding:1rem;background:#f7f8fa;color:#17202a}}section{{background:white;border:1px solid #ccd3db;border-radius:8px;padding:1rem;margin:.8rem 0}}label{{display:block;margin:.5rem 0}}input,textarea,select,button{{font:inherit;width:100%;box-sizing:border-box;padding:.45rem}}textarea{{min-height:5rem}}button{{width:auto;margin:.3rem .3rem .3rem 0}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#17202a;color:#edf2f7;padding:1rem}}.warn{{border-left:5px solid #b45309}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}</style><main><section><strong>LOCAL · ONE OPERATOR · BOUNDED TASKS · NOT A SANDBOX</strong><h1>Operator Workbench V1</h1><p>Creates and runs only the canonical coding-task lifecycle. The trusted local worker can affect systems outside its controlled workspace; review evidence before accepting.</p></section><div class=grid><section><h2>1. Task intake</h2><form id=f><label>Title<input name=title required maxlength=180></label><label>Objective<textarea name=objective required></textarea></label><label>Fixture-relative path<input name=path value='workbench_fixtures/proof.txt' required></label><label>Expected output<textarea name=expected_output required></textarea></label><label>Validation<input name=validation value='Declared output exists and matches expected output.'></label><label>Worker<select name=worker><option value=codex>Configured Codex worker</option><option value=fixture>Deterministic fixture worker (test/proof only)</option></select></label><label>Timeout seconds<input name=timeout type=number min=10 max=3600 value=600></label><label><input type=checkbox name=commit_authorized value=true> Commit authorized</label><label><input type=checkbox name=push_authorized value=true> Push authorized</label><button type=button onclick='preview()'>Preview packet</button><button type=button onclick='authorize()'>Authorize and run</button></form></section><section class=warn><h2>2. Packet preview and authorization</h2><p>Preview does not authorize execution. Authorize and run is the deliberate execution action. The worker command is selected server-side and cannot be entered here.</p><pre id=preview>Fill the form, then preview.</pre></section></div><section><h2>3. Live lifecycle, evidence, and review</h2><p id=summary>Loading…</p><pre id=status></pre><div id=review hidden><button onclick="dispose('accept')">Accept</button><button onclick="dispose('reject')">Reject</button><button onclick="dispose('correction_required')">Correction required</button></div></section><section><h2>Evidence location</h2><p>Canonical persisted records are shown in the status above. Browser refresh and server restart retain canonical records at the displayed data root; a server restart may not retain an in-memory active-process display.</p></section></main><script>const csrf='{token}';const form=()=>Object.fromEntries(new FormData(document.querySelector('#f')).entries());async function api(path,body){{let r=await fetch(path,{{method:'POST',headers:{{'Content-Type':'application/json','X-Workbench-CSRF':csrf}},body:JSON.stringify(body)}});let x=await r.json();if(!r.ok)throw Error(x.error);return x}}async function preview(){{try{{document.querySelector('#preview').textContent=JSON.stringify(await api('/api/preview',form()),null,2)}}catch(e){{alert(e)}}}}async function authorize(){{try{{await api('/api/authorize',form());tick()}}catch(e){{alert(e)}}}}async function dispose(d){{let reason=prompt('Reason (required for acceptance):','');if(reason===null)return;try{{await api('/api/disposition',{{decision:d,reason}});tick()}}catch(e){{alert(e)}}}}async function tick(){{let x=await (await fetch('/api/status')).json();document.querySelector('#summary').textContent=`State: ${{x.state}} · elapsed: ${{x.elapsed_seconds||0}}s · action: ${{x.state==='awaiting_review'?'review required':'inspect evidence'}}`;document.querySelector('#status').textContent=JSON.stringify(x,null,2);document.querySelector('#review').hidden=x.state!=='awaiting_review';}}tick();setInterval(tick,1500);</script>"""


def make_server(root: Path, port: int = 8766, data_root: Path | None = None) -> ThreadingHTTPServer:
    app = Workbench(root, data_root or root / ".operator_workbench_data")
    class Handler(BaseHTTPRequestHandler):
        def _json(self, value: Any, status: int = 200) -> None:
            body = json.dumps(value, indent=2, default=str).encode(); self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/status": self._json(app.status()); return
            if self.path in {"/", "/workbench", "/workbench/"}:
                body = render_html(app).encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            self.send_error(404)
        def do_POST(self) -> None:  # noqa: N802
            if self.path not in {"/api/preview", "/api/authorize", "/api/disposition"}: self._json({"error":"unsupported route"}, 404); return
            if self.headers.get("X-Workbench-CSRF") != app.csrf or self.headers.get("Origin", "").rstrip("/") not in {"", f"http://127.0.0.1:{self.server.server_port}"}: self._json({"error":"local action verification failed"}, 403); return
            try:
                length = int(self.headers.get("Content-Length", "0")); body = json.loads(self.rfile.read(min(length, 20000)) or b"{}")
                if not isinstance(body, dict): raise ValueError("JSON object required")
                if self.path == "/api/preview": value = packet_from_form({str(k): str(v) for k,v in body.items()})
                elif self.path == "/api/authorize": value = app.start({str(k): str(v) for k,v in body.items()})
                else: value = app.disposition(_text(body.get("decision")), _text(body.get("reason")))
                self._json(value)
            except (ValueError, json.JSONDecodeError) as error: self._json({"error": str(error)}, 400)
        def do_PUT(self): self.send_error(405)  # noqa: N802
        def do_DELETE(self): self.send_error(405)  # noqa: N802
        def log_message(self, *_: object) -> None: pass
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1]); parser.add_argument("--port", type=int, default=8766); parser.add_argument("--data-root", type=Path)
    args = parser.parse_args(); server = make_server(args.root, args.port, args.data_root)
    print(f"START_TIME={_now()}"); print(f"Operator Workbench: http://127.0.0.1:{server.server_port}/workbench (Ctrl+C to stop)")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close(); print(f"END_TIME={_now()}")


if __name__ == "__main__": main()
