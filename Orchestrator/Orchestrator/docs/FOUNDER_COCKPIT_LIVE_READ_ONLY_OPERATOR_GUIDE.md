# Live Read-Only Founder Cockpit Operator Guide

## Purpose

The Founder Cockpit is a minimal local, read-only view of current repository
authority. It reduces reliance on narrative reports; it does not replace source
authority, approve decisions, or control project state.

## Launch and Refresh

From `Orchestrator/Orchestrator`, run:

```powershell
$Start = Get-Date
"START_TIME=$($Start.ToString('o'))"
python -m orchestrator.founder_cockpit --serve
$End = Get-Date
"END_TIME=$($End.ToString('o'))"
"ELAPSED=$($End - $Start)"
```

Open `http://127.0.0.1:8765/`. The server binds only to loopback, serves GET
requests only, and recomputes the view from current documents and ordinary Git
metadata on each refresh. Press `Ctrl+C` to stop it; the shutdown timestamp is
printed. It creates no authoritative output or cache file.

## Architecture and Source Hierarchy

`orchestrator/founder_cockpit.py` is a narrow deterministic adapter and HTML
renderer using only the Python standard library. It reads the roadmap, current
tracks, startup brief, founder snapshot, closeout decision, and Git branch/HEAD.
Repository documents remain authoritative; the generated HTML is explicitly a
non-authoritative display. Known headings and explicit markers are used; prose
outside those seams is not interpreted as certainty.

## Semantics and Safety

The view shows project position, proof/non-proof, decision tension, ranked
outcome, tracks, source basis, and freshness warnings. Missing sources render
`MISSING_SOURCE`; explicit basis mismatch renders `STALE`; incompatible explicit
outcome markers render `CONFLICT`; unparseable values render `UNKNOWN`.

Repository text is HTML-escaped. The Cockpit has no write routes, controls,
providers, models, task execution, Git mutation, hidden state, or external
network access. Narrow-screen CSS stacks the primary regions below 720px.

## Tests and Limits

Run `python -m unittest tests.test_founder_cockpit` from the project root.
Tests cover canonical, missing, stale, conflict, escaped-text, and track views.
This proves only local source/test/operator-launch behavior. It does not prove
production deployment, accessibility certification, independent-user utility,
complete Markdown understanding, generalized project management, or automatic
authority reconciliation.
