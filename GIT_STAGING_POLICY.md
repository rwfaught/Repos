# Git Staging Policy

Generated ZIPs under Source Files are local/operator transport artifacts, not source-control truth.

Future product phase commits must not use root git add -A by default.

Future product phase commits should stage explicit product files changed by the packet.

The source refresh script may still be run after successful validation, but refreshed ZIPs should normally remain untracked/ignored.

If a ZIP artifact is intentionally committed later, that requires an explicit boundary saying so.

Root Git commits should preserve phase meaning and avoid unrelated generated artifact churn.

git rm --cached of ZIP artifacts is index-only and must not delete local files.

Production readiness is not implied by Git cleanliness or source snapshot creation.

Recommended product-phase staging pattern:

    git add Orchestrator/Orchestrator/orchestrator/<changed_file>.py
    git add Orchestrator/Orchestrator/tests/<changed_test>.py
    git add Orchestrator/Orchestrator/docs/<changed_doc>.md
    git status --short
    git commit -m "<specific phase message>"
    git push

Do not stage Source Files/*.zip unless a future boundary explicitly authorizes committing generated ZIP artifacts.
