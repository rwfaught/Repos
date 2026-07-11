# Native Codex GPT-5.5 Advisory Provider

This is the first live-proven online advisory provider adapter. It invokes the
authenticated WSL Codex CLI directly through a provider-neutral advisory seam,
without an API key. Native Codex is not the permanent advisory identity,
automatic default, routing authority, production dependency, or replacement for
local providers. The shared request contract, normalizer, validator,
clarification quarantine, deterministic fallback, and authority membrane remain
in control.

Future local or hosted providers can implement the same advisory-provider
boundary without changing the shared contract or authority system. Provider
selection is explicit configuration or dependency injection; availability does
not select a provider.

## Selected surface

The provider uses `/home/roger/.local/bin/codex` through `wsl.exe` and runs a
fresh `codex exec` invocation with the configured model identifier. The proof
configuration requests `gpt-5.5` (human-facing label `GPT-5.5`). The adapter is
configurable for executable, model, timeout, working directory, sandbox,
approval, output format, and maximum response size.

The invocation uses saved ChatGPT authentication owned by the native client.
The adapter does not read, copy, persist, or print credentials and rejects an
API-key authentication classification.

## Prompt transport repair

The advisory prompt is supplied through the subprocess stdin stream. It is not
placed in the Windows-side `wsl.exe` argument vector. This keeps large bounded
evidence packets out of the Windows command-line transport path.

The prior scenario-12 failure produced `FileNotFoundError: [WinError 206] The
filename or extension is too long` with an approximately 79,891-character
prompt. That condition is classified as `windows_command_line_too_long` and is
not retried as a transient launcher failure. Genuine launcher-not-found errors
retain their separate classification.

## Safety and flow

The invocation uses `--ignore-user-config`, `--ignore-rules`,
`--ask-for-approval never`, `--ephemeral`, `--sandbox read-only`,
`--skip-git-repo-check`, `--json`, and an isolated `/tmp` working directory.
No web search, MCP, plugin, subagent, session continuation, or writable
repository authority is requested.

The flow is:

```text
bounded request
-> native Codex CLI
-> JSONL/process capture
-> final agent-message extraction
-> existing local-model normalizer and validator
-> candidate admission or quarantine
-> deterministic fallback
```

The provider records raw stdout and stderr, process status, timing, model
identity where exposed, extraction classification, hashes, and validation
classification. The canonical prompt permits only `deterministic`,
`local_model`, `frontier`, `external`, and `human` under `matched_signals`.
Facts, hypotheses, interpretations, conclusions, and assumptions belong in
their canonical fields; missing prerequisites use `clarification_needed`.
Non-empty clarification remains quarantined. Invocation evidence is separate from the existing
`execution_performed` authority flag, which remains false so model output cannot
grant route, plan, approval, handoff, dispatch, mutation, or execution power.

## Failure behavior

Authentication failures, API-key paths, Windows launcher absence, WSL absence,
distribution absence, Linux executable absence, permission denial, invalid
invocations, model absence, timeouts, non-zero exits, malformed JSONL, missing
or empty final responses, oversized responses, unauthorized tool activity,
malformed advisory output, authority-shaped output, and validator rejection are
classified separately where direct evidence supports it. At most one
transport retry is permitted for a response-free transient failure; both
attempts remain evidenced. There are no semantic retries, silent substitutions,
or automatic local-to-Codex/API fallback.

## Live-smoke posture

One GPT-5.5 smoke was authorized for this boundary. Its evidence is stored
outside the repository under `C:\Users\accou\LocalModelEvidence` and is not a
claim of production readiness, unlimited usage, API equivalence, cost
equivalence, or long-term allowance economics. The first attempt stopped at
authentication-status classification because Windows routed the redacted login
status to stderr. The one permitted retry confirmed subscription auth but
returned CLI code 2 before model execution because this client version requires
global approval flags before `exec` and config-isolation flags after `exec`.
The adapter now reflects that corrected ordering. The frozen 12-scenario
evaluation retained 11 scorable responses at 15/15, eight correct clarification
quarantines, two schema rejections caused by unsupported categories, and one
repeatable executable-classification transport failure. That prior result is
accepted evidence, not proof of production readiness or automatic selection;
the post-repair frozen rerun remains a separate guarded evaluation artifact.

This prompt-transport repair boundary performed no live WSL, Codex, model, or
provider execution. It provides source, test, and documentation evidence only;
the repaired transport remains unproven until a separately authorized live
evaluation.
