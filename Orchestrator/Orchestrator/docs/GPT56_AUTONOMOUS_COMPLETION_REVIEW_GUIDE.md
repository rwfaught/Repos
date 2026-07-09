# GPT56 Autonomous Completion Campaign Review Guide

## Review order

1. Confirm the fork is on `experiment/gpt56-local-ai-consulting-wedge`.
2. Confirm the authoritative worktree remains unchanged.
3. Read `docs/GPT56_AUTONOMOUS_COMPLETION_CAMPAIGN_LOG.md`.
4. Inspect the source/test diff for the campaign readback and CLI.
5. Run the commands below and compare JSON/Markdown output.
6. Review the explicit non-proofs before considering any promotion.

## Commands

```text
python -m orchestrator.local_ai_consulting_campaign_cli
python -m orchestrator.local_ai_consulting_campaign_cli --scenario internal_knowledge_helpdesk --format markdown
python -m orchestrator.local_ai_consulting_campaign_cli --scenario regulated_sensitive_data
python -m orchestrator.local_ai_consulting_campaign_cli --summary --format markdown
python -m unittest -v tests.test_local_ai_consulting_audit_packet tests.test_local_ai_consulting_campaign tests.test_local_ai_consulting_campaign_cli
```

## Expected review questions

- Does the summary dashboard make readiness, blocker reasons, and the next
  recommended review scenario easy to see?
- Does the selected-scenario report give a founder enough context to decide
  whether to approve the next bounded local review step?
- Does a selected scenario preserve owner approval before implementation?
- Does the neutral dossier/case bridge remain an adapter rather than a second
  semantic system?
- Are missing inputs, sensitivity, and external integrations classified without
  pretending they were solved?
- Does every output keep execution unauthorized and non-proofs visible?

## Explicit non-proofs

This review can establish deterministic structural behavior only. It cannot
establish semantic correctness, real business usefulness, customer value,
provider/model/runtime execution, external integration execution, production
readiness, a selected first product wedge, or Phase 387 resumption.

## Promotion posture

No promotion, merge, push, product ratification, or runtime boundary is implied
by this guide. Those actions require a separate authorized decision.
