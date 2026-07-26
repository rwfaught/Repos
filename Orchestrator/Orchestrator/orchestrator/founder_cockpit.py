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


def _track_groups(text: str) -> dict[str, list[str]]:
    groups = {key: [] for key in ("ACTIVE", "PAUSED", "BLOCKED", "DEFERRED", "COMPLETED", "WATCH")}
    for line in text.splitlines():
        if not line.startswith("|") or line.count("|") < 3:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"Track", "Thread"} or set(cells[0]) == {"-"}:
            continue
        status = cells[1].upper()
        group = "COMPLETED" if any(token in status for token in ("RETIRED", "RESOLVED", "COMPLETE")) else next((key for key in groups if key in status), "WATCH")
        groups[group].append(f"{cells[0]} — {cells[1]}")
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
    outcome = _marker(decision, "NEXT_RANKED_PROJECT_OUTCOME") or _first(snapshot, r"Recommended next outcome:\s*\n+\s*`([^`]+)`", "UNKNOWN")
    markers = {value for value in (_marker(text, "NEXT_RANKED_PROJECT_OUTCOME") for text in texts.values()) if value}
    if len(markers) > 1:
        warnings.append("CONFLICT: current sources declare different NEXT_RANKED_PROJECT_OUTCOME values; no automatic resolution is valid.")
    for label, text in texts.items():
        basis = _marker(text, "CURRENT_REPOSITORY_BASIS")
        if basis and basis != git_head:
            warnings.append(f"STALE: {label} declares repository basis {basis}, current Git is {git_head}.")
    proof = "Governed Research V1 fixed historical-record manual and source/test proof stage is completed and CTO-ratified."
    non_proof = "This does not prove generalized research, Phase 5, generalized Phase 6, provider/model behavior, production readiness, or a product wedge."
    founder_decision = _first(snapshot, r"Roger must decide ([^.]+\.)", "UNKNOWN: no pending founder disposition was parsed.")
    health = "CANONICAL_CURRENT_READ" if not warnings else "DEGRADED"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(), "branch": branch, "git_head": git_head,
        "stage": stage, "outcome": outcome, "proof": proof, "non_proof": non_proof,
        "founder_decision": founder_decision, "warnings": warnings, "health": health,
        "sources": sources, "tracks": _track_groups(tracks),
        "read_only": "PROVEN_FOR_IMPLEMENTED_SURFACE: generation reads docs and ordinary Git metadata only; the HTTP surface exposes GET only.",
    }


def render_html(model: dict[str, Any]) -> str:
    """Render escaped, static HTML; no repository text is executable."""
    e = lambda value: html.escape(str(value), quote=True)
    warnings = "".join(f"<li>{e(item)}</li>" for item in model["warnings"]) or "<li>No missing, stale, or conflicting source condition detected by this narrow adapter.</li>"
    source_rows = "".join(f"<tr><td>{e(item['label'])}</td><td><code>{e(item['path'])}</code></td><td>{e(item['state'])}</td></tr>" for item in model["sources"])
    track_sections = "".join(f"<section><h3>{e(kind.title())}</h3><ul>{''.join(f'<li>{e(row)}</li>' for row in rows) or '<li>NOT_APPLICABLE</li>'}</ul></section>" for kind, rows in model["tracks"].items())
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Founder Cockpit</title><style>
body{{font:16px system-ui,sans-serif;line-height:1.45;max-width:1200px;margin:auto;padding:1rem;background:#f7f8fa;color:#17202a}}header,.card{{background:white;border:1px solid #ccd3db;border-radius:8px;padding:1rem;margin:.75rem 0}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}}.warning{{border-left:5px solid #b45309;background:#fff7ed}}code{{overflow-wrap:anywhere}}table{{width:100%;border-collapse:collapse}}td,th{{padding:.45rem;border-bottom:1px solid #d7dde3;text-align:left;vertical-align:top}}@media(max-width:720px){{.grid{{grid-template-columns:1fr}}body{{padding:.5rem}}}}</style></head><body>
<header><strong>LIVE REPOSITORY-DERIVED · READ ONLY · NON-AUTHORITATIVE DISPLAY</strong><br>Generated {e(model['generated_at'])}; branch <code>{e(model['branch'])}</code>; Git <code>{e(model['git_head'])}</code></header>
<main><div class='grid'><section class='card'><h1>Position</h1><p><strong>Project stage:</strong> {e(model['stage'])}</p><p><strong>Most recent accepted proof:</strong> {e(model['proof'])}</p><p><strong>Decisive non-proof:</strong> {e(model['non_proof'])}</p></section><section class='card'><h2>Decision tension</h2><p><strong>Pending founder disposition:</strong> {e(model['founder_decision'])}</p><p><strong>Current ranked outcome:</strong> <code>{e(model['outcome'])}</code></p><p>No product wedge is currently ratified.</p></section></div>
<div class='grid'><section class='card'><h2>Next move and tracks</h2><p>{e(model['outcome'])}</p>{track_sections}</section><section class='card warning'><h2>Source health: {e(model['health'])}</h2><ul>{warnings}</ul><p>{e(model['read_only'])}</p></section></div>
<section class='card'><h2>Authority and freshness</h2><p>Each displayed claim is derived from the source list below. This view cannot resolve disagreement or make authority decisions.</p><table><thead><tr><th>Source</th><th>Path</th><th>Availability</th></tr></thead><tbody>{source_rows}</tbody></table></section></main></body></html>"""


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
