# Deterministic local testing

From `Orchestrator/Orchestrator`, run the full deterministic suite with the
checked-in virtual environment:

```text
.venv\Scripts\python.exe -B scripts\run_deterministic_tests.py
```

The runner discovers all `tests/test_*.py` modules, including
`test_canonical_alpha_runtime.py` and `test_trusted_worker_security.py`. It
uses a temporary data root, so tests that exercise persistence, fixtures, and
the local trusted-worker subprocess contract do not write into the checkout.

The suite is standard-library `unittest` only. It contains no provider, model,
network, WSL, bridge, or production-task execution. A nonzero exit status
means one or more tests failed.
