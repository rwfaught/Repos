from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

from orchestrator.founder_cockpit import derive_cockpit, make_server, render_html


class FounderCockpitTests(unittest.TestCase):
    def make_root(self, missing: str | None = None, conflict: bool = False, stale: bool = False) -> Path:
        root = Path(tempfile.mkdtemp()); docs = root / "docs"; docs.mkdir()
        data = {
            "PROJECT_TRAJECTORY_AND_ROADMAP_CURRENT.md": "Project stage remains `POST_FOUNDATION_PRE_PRODUCTIZATION_ALPHA`\n",
            "TRACKS_AND_OPEN_THREADS_CURRENT.md": "| Track | Status | Current posture |\n| --- | --- | --- |\n| Core | ACTIVE | visible |\n| Deferred | DEFERRED | visible |\n",
            "STARTUP_BRIEF.md": "Current authority.\n",
            "FOUNDER_COMPREHENSION_SNAPSHOT_CURRENT.md": "Roger must decide what to ratify before implementation resumes.\nRecommended next outcome:\n`LIVE_READ_ONLY_FOUNDER_COCKPIT_MINIMUM_USEFUL_SURFACE`\n",
            "GOVERNED_RESEARCH_V1_CLOSEOUT_AUTONOMY_AND_FOUNDER_VISIBILITY_RECONCILIATION_DECISION.md": "`NEXT_RANKED_PROJECT_OUTCOME=LIVE_READ_ONLY_FOUNDER_COCKPIT_MINIMUM_USEFUL_SURFACE`\n",
        }
        if conflict: data["STARTUP_BRIEF.md"] += "`NEXT_RANKED_PROJECT_OUTCOME=OTHER_OUTCOME`\n"
        if stale: data["STARTUP_BRIEF.md"] += "`CURRENT_REPOSITORY_BASIS=not-current`\n"
        for name, text in data.items():
            if name != missing: (docs / name).write_text(text, encoding="utf-8")
        return root

    def test_canonical_model_has_live_sources_and_escaped_output(self):
        root = self.make_root(); model = derive_cockpit(root); page = render_html(model)
        self.assertEqual("CANONICAL_CURRENT_READ", model["health"]); self.assertIn("Position", page); self.assertIn("READ ONLY", page)

    def test_missing_source_is_visible(self):
        model = derive_cockpit(self.make_root(missing="STARTUP_BRIEF.md")); self.assertIn("MISSING_SOURCE", " ".join(model["warnings"]))

    def test_stale_marker_is_visible(self):
        model = derive_cockpit(self.make_root(stale=True)); self.assertIn("STALE:", " ".join(model["warnings"]))

    def test_conflicting_marker_is_visible(self):
        model = derive_cockpit(self.make_root(conflict=True)); self.assertIn("CONFLICT:", " ".join(model["warnings"]))

    def test_repository_text_is_escaped(self):
        model = derive_cockpit(self.make_root()); model["stage"] = "<script>alert(1)</script>"
        self.assertIn("&lt;script&gt;", render_html(model))

    def test_track_groups_are_present(self):
        model = derive_cockpit(self.make_root()); self.assertEqual(["Core — ACTIVE"], model["tracks"]["ACTIVE"])

    def test_loopback_server_is_get_only_and_serves_current_view(self):
        server = make_server(self.make_root(), 0); thread = threading.Thread(target=server.serve_forever); thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/") as response:
                self.assertEqual(200, response.status); self.assertIn(b"LIVE REPOSITORY-DERIVED", response.read())
        finally:
            server.shutdown(); thread.join(); server.server_close()


if __name__ == "__main__": unittest.main()
