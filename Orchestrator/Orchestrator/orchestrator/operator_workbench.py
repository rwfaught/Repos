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
LAUNCHER_TEMPLATE = """$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FounderCockpit = Join-Path $ProjectRoot 'scripts\\start_founder_cockpit.ps1'
$Workbench = Join-Path $ProjectRoot 'scripts\\start_orchestrator_workbench.ps1'
Write-Host 'Orchestrator Tools'
Write-Host '1. Start Founder Cockpit'
Write-Host '2. Start Operator Workbench'
Write-Host 'Q. Quit'
$choice = Read-Host 'Select an option'
if ($choice -eq '1') { & powershell.exe -ExecutionPolicy Bypass -File $FounderCockpit }
elseif ($choice -eq '2') { & powershell.exe -ExecutionPolicy Bypass -File $Workbench }
else { Write-Host 'No launcher was started.' }
"""


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


def guided_packet_from_form(form: dict[str, str], *, authorized: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    request = _text(form.get("request"), limit=4000)
    if not request:
        raise ValueError("Describe the small outcome you want in ordinary language.")
    lowered = request.lower()
    known_launcher = "launcher" in lowered and "cockpit" in lowered and "workbench" in lowered
    if known_launcher:
        derived = {"title": "Create an Orchestrator tools launcher", "objective": request, "path": "workbench_fixtures/start_orchestrator_tools.ps1", "expected_output": LAUNCHER_TEMPLATE, "validation": "The declared launcher file exists and exactly matches the proposed launcher.", "worker": "codex", "timeout": "600"}
        assumptions = ["This is the recognized Founder Cockpit and Operator Workbench launcher request.", "The launcher is limited to the dedicated Workbench fixture path."]
    else:
        path = _text(form.get("path"))
        result = str(form.get("result") or "")
        if not path or not result.strip():
            raise ValueError("To keep this task bounded, say where the fixture result should be saved and describe the exact result it should contain.")
        derived = {"title": request[:180], "objective": request, "path": path, "expected_output": result, "validation": "The declared file exists and exactly matches the proposed result.", "worker": "codex", "timeout": "600"}
        assumptions = ["The requested result is limited to the single fixture file you named."]
    packet = packet_from_form({**derived, "commit_authorized": "", "push_authorized": ""}, authorized=authorized)
    proposal = {"understanding": request, "file": packet["files_in_scope"][0], "result": "A Windows launcher for the currently supported operator tools." if known_launcher else "The exact plain-language result you supplied.", "checks": packet["success_criteria"], "will_not": ["change files outside the declared fixture path", "commit or push", "run an arbitrary browser-supplied command"], "commit_authorized": False, "push_authorized": False, "assumptions": assumptions}
    return packet, proposal


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
            packet, proposal = guided_packet_from_form(form, authorized=True)
            worker = _text(form.get("worker")) or "codex"
            command = self.worker_command(worker)
            timeout = _text(form.get("timeout")) or "600"
            packet_dir = self.data_root / "workbench_packets"; packet_dir.mkdir(parents=True, exist_ok=True)
            packet_path = packet_dir / f"{packet['packet_id']}.json"; packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
            argv = [sys.executable, "-m", "orchestrator.operator_coding_task_packet_cli", "--packet-json", str(packet_path), "--data-root", str(self.data_root), "--trusted-worker-posture", TRUST_POSTURE, "--worker-timeout-seconds", timeout, "--worker-command", *command]
            item = {"state": "executing", "started_at": _now(), "packet": packet, "proposal": proposal, "worker": worker, "command": "configured_named_worker", "process_state": "preparing the bounded task", "stdout": "", "stderr": "", "result": None}
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
            item["state"] = "awaiting_review" if item["result"].get("final_task_status") == "completed" else "needs_attention"
            item["process_state"] = "preparing the operator review" if item["state"] == "awaiting_review" else "stopped with a diagnosable failure"
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

    @staticmethod
    def _presentation(item: dict[str, Any], evidence: dict[str, Any], elapsed: float) -> dict[str, Any]:
        task, artifact, verifier = evidence["task"], evidence["artifact"], evidence["verifier"]
        verification = verifier.get("verification_result") if isinstance(verifier.get("verification_result"), dict) else {}
        task_status = _text(task.get("status"))
        changed = (task.get("worker_security") or {}).get("workspace_effect_audit", {}).get("changed_paths", [])
        can_decide = item.get("state") == "awaiting_review" and task_status == "completed" and artifact.get("status") == "success" and verification.get("overall_passed") is True
        if item.get("state") == "executing":
            return {"headline": "Working on the declared task", "keep": "Not ready yet", "explanation": "The worker is still running. No decision can be recorded yet.", "can_decide": False, "elapsed_seconds": elapsed}
        if item.get("state") == "accepted":
            return {"headline": "Accepted and recorded", "keep": "Accepted by the operator", "explanation": "The acceptance record was saved with the reason you provided.", "can_decide": False, "elapsed_seconds": elapsed}
        if can_decide:
            return {"headline": "Declared checks passed", "keep": "Ready for your decision", "explanation": "The declared file changed and the recorded checks passed. You may accept, reject, or request a correction.", "can_decide": True, "elapsed_seconds": elapsed, "changed_paths": changed}
        error = _text(artifact.get("error"))
        explanation = "The result did not complete the declared checks, so it cannot be accepted or otherwise recorded as a decision."
        if error == "worker_nonzero_exit": explanation = "The worker did not produce the exact declared result. Do not accept or keep this result as a completed task."
        elif task_status == "verification_failed": explanation = "The declared verification checks failed. Do not accept or keep this result as a completed task."
        return {"headline": "Needs correction before a decision", "keep": "Do not accept yet", "explanation": explanation, "can_decide": False, "elapsed_seconds": elapsed, "changed_paths": changed, "technical_status": task_status or error or "unknown"}

    def status(self) -> dict[str, Any]:
        item = self.active
        if not item: return {"state": "idle", "data_root": str(self.data_root)}
        ended = datetime.fromisoformat(item["ended_at"]).timestamp() if item.get("ended_at") else time.time()
        elapsed = round(ended - datetime.fromisoformat(item["started_at"]).timestamp(), 1)
        evidence = self._evidence(item["packet"])
        return {**item, "elapsed_seconds": elapsed, "evidence": evidence, "presentation": self._presentation(item, evidence, elapsed)}


def render_html(workbench: Workbench) -> str:
    token = html.escape(workbench.csrf, quote=True)
    return f"""<!doctype html><meta charset=utf-8><title>Operator Workbench V1.1</title><style>body{{font:16px system-ui;max-width:900px;margin:auto;padding:1rem}}section{{border:1px solid #ccd3db;border-radius:8px;padding:1rem;margin:.8rem 0}}textarea,input,button{{font:inherit;width:100%;box-sizing:border-box;padding:.5rem;margin:.3rem 0}}textarea{{min-height:8rem}}button{{width:auto}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style><main><section><h1>Describe the outcome you want</h1><p>Use ordinary language. Orchestrator will show its bounded proposal before anything runs.</p><label>What would you like to accomplish?<textarea name=request form=f required placeholder='Create a Windows PowerShell launcher that starts the supported Orchestrator operator tools.'></textarea></label><details><summary>More detail, only if this is not the standard launcher request</summary><label>Fixture file to create<input name=path form=f placeholder='workbench_fixtures/result.txt'></label><label>What exact result should it contain?<textarea name=result form=f></textarea></label></details><form id=f><button type=button onclick='preview()'>Show proposal</button><button type=button onclick='authorize()'>Authorize this proposal</button></form></section><section><h2>Proposal before authorization</h2><div id=proposal>Describe the outcome, then choose Show proposal.</div><details><summary>Technical packet</summary><pre id=technical></pre></details></section><section><h2>Progress and review</h2><h3 id=headline>No task has been run</h3><p id=explanation></p><p id=elapsed></p><p id=changed></p><div id=review hidden><button onclick="dispose('accept')">Accept result</button><button onclick="dispose('reject')">Reject result</button><button onclick="dispose('correction_required')">Request correction</button></div></section></main><script>const csrf='{token}',form=()=>Object.fromEntries(new FormData(document.querySelector('#f')).entries());async function api(p,b){{let r=await fetch(p,{{method:'POST',headers:{{'Content-Type':'application/json','X-Workbench-CSRF':csrf}},body:JSON.stringify(b)}});let x=await r.json();if(!r.ok)throw Error(x.error);return x}}function proposal(x){{return `I understand: ${{x.understanding}}\n\nIt may change: ${{x.file}}\n\nIt will produce: ${{x.result}}\n\nIt will check: ${{x.checks.join('; ')}}\n\nIt will not: ${{x.will_not.join('; ')}}\n\nAssumptions: ${{x.assumptions.join(' ')}}\n\nCommit: no. Push: no.`}}async function preview(){{try{{let x=await api('/api/preview',form());document.querySelector('#proposal').textContent=proposal(x.proposal);document.querySelector('#technical').textContent=JSON.stringify(x.packet,null,2)}}catch(e){{alert(e)}}}}async function authorize(){{try{{await api('/api/authorize',form());tick()}}catch(e){{alert(e)}}}}async function dispose(d){{let r=prompt('Reason:','');if(r!==null){{try{{await api('/api/disposition',{{decision:d,reason:r}});tick()}}catch(e){{alert(e)}}}}}}async function tick(){{let x=await (await fetch('/api/status')).json(),p=x.presentation||{{headline:'No task has been run',explanation:'Show a proposal before authorizing.',elapsed_seconds:0,can_decide:false}};document.querySelector('#headline').textContent=p.headline;document.querySelector('#explanation').textContent=p.explanation;document.querySelector('#elapsed').textContent=`Elapsed: ${{p.elapsed_seconds||0}} seconds · ${{x.process_state||'waiting'}}`;document.querySelector('#changed').textContent=p.changed_paths?.length?`Changed: ${{p.changed_paths.join(', ')}}`:'';document.querySelector('#review').hidden=!p.can_decide}}tick();setInterval(tick,1500)</script>"""


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
                if self.path == "/api/preview":
                    packet, proposal = guided_packet_from_form({str(k): str(v) for k,v in body.items()})
                    value = {"proposal": proposal, "packet": packet}
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
