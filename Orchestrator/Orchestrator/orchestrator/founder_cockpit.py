"""Read-only local Founder Cockpit derived from current repository authority."""
from __future__ import annotations

import argparse
import html
import re
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


EXPECTED_SOURCES = {
    "Roadmap": "PROJECT_TRAJECTORY_AND_ROADMAP_CURRENT.md",
    "Current tracks": "TRACKS_AND_OPEN_THREADS_CURRENT.md",
    "Startup brief": "STARTUP_BRIEF.md",
    "Founder snapshot": "FOUNDER_COMPREHENSION_SNAPSHOT_CURRENT.md",
    "Closeout decision": "GOVERNED_RESEARCH_V1_CLOSEOUT_AUTONOMY_AND_FOUNDER_VISIBILITY_RECONCILIATION_DECISION.md",
}

LABELS = {
    "POST_FOUNDATION_PRE_PRODUCTIZATION_ALPHA": "Post-foundation, pre-productization alpha",
    "BOUNDED_V1_PROOF_STAGE_COMPLETE": "Bounded V1 proof stage complete",
    "BLOCKED_PENDING_PARTICIPANT_OFF_CRITICAL_PATH": "Blocked pending a participant; off the critical path",
    "PENDING_CTO_RERANK_AFTER_FOUNDER_COCKPIT_USEFULNESS_DISPOSITION": "Pending CTO re-ranking after Roger reviews this Cockpit",
    "FOUNDER_COCKPIT_USEFULNESS_AND_COMPREHENSION_REVIEW": "Review this Cockpit’s usefulness and comprehension",
}


def _read(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except OSError as error:
        return None, f"MISSING_SOURCE: {path.name} ({error})"


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _marker(text: str, name: str) -> str | None:
    match = re.search(rf"`?{re.escape(name)}=([^`\n]+)`?", text)
    return match.group(1).strip() if match else None


def _first(text: str, pattern: str, fallback: str) -> str:
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else fallback


def _label(value: str) -> str:
    return LABELS.get(value, value.replace("_", " ").title() if value.isupper() and "_" in value else value)


def _track_groups(text: str) -> dict[str, list[str]]:
    groups = {key: [] for key in ("ACTIVE", "PAUSED", "BLOCKED", "DEFERRED", "COMPLETED", "WATCH")}
    seen: set[tuple[str, str]] = set()
    for line in text.splitlines():
        if not line.startswith("|") or line.count("|") < 3:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"Track", "Thread"} or set(cells[0]) == {"-"}:
            continue
        status = cells[1].upper()
        identity = (cells[0], status)
        if identity in seen:
            continue
        seen.add(identity)
        group = "COMPLETED" if any(token in status for token in ("RETIRED", "RESOLVED", "COMPLETE")) else next((key for key in groups if key in status), "WATCH")
        groups[group].append(f"{cells[0]} — {_label(cells[1])} [{cells[1]}]")
    return groups


def derive_cockpit(root: Path) -> dict[str, Any]:
    """Return a narrow, traceable view model; it never writes repository state."""
    docs = root / "docs"
    texts: dict[str, str] = {}
    warnings: list[str] = []
    sources: list[dict[str, str]] = []
    for label, filename in EXPECTED_SOURCES.items():
        text, error = _read(docs / filename)
        if error:
            warnings.append(error)
            sources.append({"label": label, "path": f"docs/{filename}", "state": "MISSING_SOURCE"})
        else:
            texts[label] = text or ""
            sources.append({"label": label, "path": f"docs/{filename}", "state": "AVAILABLE"})

    decision = texts.get("Closeout decision", "")
    roadmap = texts.get("Roadmap", "")
    tracks = texts.get("Current tracks", "")
    snapshot = texts.get("Founder snapshot", "")
    git_head = _git(root, "rev-parse", "HEAD")
    branch = _git(root, "branch", "--show-current")
    stage = _first(decision + "\n" + roadmap, r"(?:Project stage remains\s+`|Current stage:\s*)([^`\n]+)", "UNKNOWN")
    markers = {value for value in (_marker(text, "NEXT_RANKED_PROJECT_OUTCOME") for text in texts.values()) if value}
    outcome = next(iter(markers), "UNKNOWN") if len(markers) == 1 else "CONFLICT"
    if len(markers) > 1:
        warnings.append("CONFLICT: current sources declare different NEXT_RANKED_PROJECT_OUTCOME values; no automatic resolution is valid.")
    for label, text in texts.items():
        basis = _marker(text, "CURRENT_REPOSITORY_BASIS")
        if basis and basis != git_head:
            warnings.append(f"STALE: {label} declares repository basis {basis}, current Git is {git_head}.")
    proof = "Governed Research V1 fixed historical-record manual and source/test proof stage is completed and CTO-ratified."
    non_proof = "This does not prove generalized research, Phase 5, generalized Phase 6, provider/model behavior, production readiness, or a product wedge."
    dispositions = {value for value in (_marker(text, "PENDING_FOUNDER_DISPOSITION") for text in texts.values()) if value}
    founder_decision = next(iter(dispositions), "UNKNOWN") if len(dispositions) == 1 else "CONFLICT"
    if len(dispositions) > 1:
        warnings.append("CONFLICT: current sources declare different PENDING_FOUNDER_DISPOSITION values; no automatic resolution is valid.")
    health = "CANONICAL_CURRENT_READ" if not warnings else "DEGRADED"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(), "branch": branch, "git_head": git_head,
        "stage": stage, "stage_label": _label(stage), "outcome": outcome, "outcome_label": _label(outcome), "proof": proof, "non_proof": non_proof,
        "founder_decision": founder_decision, "founder_label": _label(founder_decision), "warnings": warnings, "health": health,
        "sources": sources, "tracks": _track_groups(tracks),
        "read_only": "PROVEN_FOR_IMPLEMENTED_SURFACE: generation reads docs and ordinary Git metadata only; the HTTP surface exposes GET only.",
    }


def render_html(model: dict[str, Any]) -> str:
    """Render escaped, static HTML; no repository text is executable."""
    e = lambda value: html.escape(str(value), quote=True)
    warnings = "".join(f"<li>{e(item)}</li>" for item in model["warnings"]) or "<li>No missing, stale, or conflicting source condition detected by this narrow adapter.</li>"
    source_rows = "".join(f"<tr><th scope='row'>{e(item['label'])}</th><td><code>{e(item['path'])}</code></td><td>{e(item['state'])}</td></tr>" for item in model["sources"])
    primary = "".join(f"<section class='track'><h3>{kind.title()}</h3><ul>{''.join(f'<li>{e(row)}</li>' for row in model['tracks'][kind]) or '<li>None recorded</li>'}</ul></section>" for kind in ("ACTIVE", "PAUSED", "BLOCKED"))
    secondary = "".join(f"<section class='track'><h3>{kind.title()} ({len(model['tracks'][kind])})</h3><ul>{''.join(f'<li>{e(row)}</li>' for row in model['tracks'][kind]) or '<li>None recorded</li>'}</ul></section>" for kind in ("WATCH", "DEFERRED", "COMPLETED"))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Founder Cockpit</title><style>
body{{font:16px system-ui,sans-serif;line-height:1.45;max-width:1200px;margin:auto;padding:1rem;background:#f7f8fa;color:#17202a}}header,.card{{background:#fff;border:1px solid #ccd3db;border-radius:8px;padding:1rem;margin:.75rem 0}}header{{font-size:.88rem}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem;align-items:start}}.attention{{border-left:5px solid #7c3aed}}.warning{{border-left:5px solid #b45309;background:#fff7ed}}.track{{margin:.75rem 0}}code{{overflow-wrap:anywhere}}table{{width:100%;border-collapse:collapse;table-layout:fixed}}td,th{{padding:.45rem;border-bottom:1px solid #d7dde3;text-align:left;vertical-align:top;overflow-wrap:anywhere}}td:last-child{{width:18%}}details{{margin-top:.75rem}}@media(max-width:720px){{.grid{{grid-template-columns:1fr}}body{{padding:.5rem}}table,tbody,tr,td,th{{display:block}}thead{{display:none}}tr{{border-bottom:1px solid #d7dde3;padding:.5rem 0}}td:last-child{{width:auto}}}}</style></head><body>
<header><strong>LIVE REPOSITORY-DERIVED · READ ONLY · NON-AUTHORITATIVE DISPLAY</strong><br>Generated {e(model['generated_at'])}; branch <code>{e(model['branch'])}</code>; Git <code>{e(model['git_head'])}</code></header>
<main><div class='grid'><section class='card'><h1>Where the project is</h1><p><strong>{e(model['stage_label'])}</strong><br><code>{e(model['stage'])}</code></p><p><strong>Most recent accepted proof:</strong> {e(model['proof'])}</p><p><strong>Decisive non-proof:</strong> {e(model['non_proof'])}</p></section><section class='card attention'><h2>What needs your attention</h2><p><strong>{e(model['founder_label'])}</strong><br><code>{e(model['founder_decision'])}</code></p><p>Review whether this Cockpit explains position, non-proofs, required decisions, and the next meaningful move without ChatGPT/Codex narration.</p></section></div>
<div class='grid'><section class='card'><h2>What happens next</h2><p><strong>{e(model['outcome_label'])}</strong><br><code>{e(model['outcome'])}</code></p><h2>Current tracks</h2>{primary}<details><summary>Watch, deferred, and completed tracks</summary>{secondary}</details></section><section class='card warning'><h2>Source health: {e(model['health'])}</h2><ul>{warnings}</ul><p>{e(model['read_only'])}</p></section></div>
<section class='card'><h2>Authority details</h2><p>Each displayed claim retains its source identity. This view cannot resolve disagreement or make authority decisions.</p><table><thead><tr><th>Source</th><th>Path</th><th>Availability</th></tr></thead><tbody>{source_rows}</tbody></table></section></main></body></html>"""


def make_server(root: Path, port: int) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path not in {"/", "/index.html"}:
                self.send_error(404); return
            body = render_html(derive_cockpit(root)).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, *_: object) -> None: pass
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(root: Path, port: int) -> None:
    server = make_server(root, port)
    print(f"START_TIME={datetime.now().astimezone().isoformat()}")
    print(f"Founder Cockpit read-only server: http://127.0.0.1:{port}/ (Ctrl+C to stop)")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        server.server_close(); end = datetime.now().astimezone(); print(f"END_TIME={end.isoformat()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render or serve the read-only Founder Cockpit.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--serve", action="store_true"); parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.serve: serve(args.root, args.port)
    else: print(render_html(derive_cockpit(args.root)))


if __name__ == "__main__": main()
