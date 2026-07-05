from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import NO_FIRST_PRODUCT_WEDGE_SELECTED
from orchestrator.founder_native_setting_fixture import (
    DEMO_CANDIDATE,
    SETTING_TITLE,
    build_human_override_setting_fixture,
)


BOUNDARY = "FOUNDER_NATIVE_SETTING_DOSSIER_OUTPUT_SOURCE_TEST_DOCS"
OUTPUT_NAME = "human_override_setting_consistency_dossier_output"
RECOMMENDED_NEXT_BOUNDARY = "FOUNDER_NATIVE_SETTING_DOSSIER_OUTPUT_REVIEW_READONLY"

NON_PROOFS = (
    "no runtime proof",
    "no provider/model proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no claims/disputes/appeals product implementation",
    "no game/worldbuilding/design wedge selection",
    "no live model generation",
    "no provider calls",
)

DRAFT_REPAIR_OR_RECOMMENDATION = (
    "Clarify whether post-AI sovereignty in The Human Override is real human "
    "control, bureaucratic ritual, or negotiated dependency on quarantined and "
    "restricted machine intelligence."
)


@dataclass(frozen=True)
class FounderNativeSettingDossierOutput:
    output_name: str
    boundary: str
    demo_candidate: str
    setting_title: str
    canon_facts: tuple[dict[str, str], ...]
    contradictions: tuple[str, ...]
    missing_canon: tuple[str, ...]
    open_questions: tuple[str, ...]
    draft_repair_or_recommendation: str
    next_work_items: tuple[str, ...]
    explicit_non_proofs: tuple[str, ...]
    product_wedge_selection: str
    first_product_wedge_selected: bool
    phase_387_implemented: bool
    runtime_required: bool
    provider_model_required: bool
    recommended_next_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_name": self.output_name,
            "boundary": self.boundary,
            "demo_candidate": self.demo_candidate,
            "setting_title": self.setting_title,
            "canon_facts": [dict(fact) for fact in self.canon_facts],
            "contradictions": list(self.contradictions),
            "missing_canon": list(self.missing_canon),
            "open_questions": list(self.open_questions),
            "draft_repair_or_recommendation": self.draft_repair_or_recommendation,
            "next_work_items": list(self.next_work_items),
            "explicit_non_proofs": list(self.explicit_non_proofs),
            "product_wedge_selection": self.product_wedge_selection,
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "phase_387_implemented": self.phase_387_implemented,
            "runtime_required": self.runtime_required,
            "provider_model_required": self.provider_model_required,
            "recommended_next_boundary": self.recommended_next_boundary,
        }


def build_human_override_setting_dossier_output() -> FounderNativeSettingDossierOutput:
    fixture = build_human_override_setting_fixture()
    adapted = fixture.adapted_dossier_case
    readiness = fixture.readiness_report
    canon_facts = []
    for note in fixture.source_notes:
        canon_facts.append({"fact": note["canon_fact"], "source": note["title"]})
        canon_facts.append({"fact": note["conflict"], "source": note["title"]})

    return FounderNativeSettingDossierOutput(
        output_name=OUTPUT_NAME,
        boundary=BOUNDARY,
        demo_candidate=DEMO_CANDIDATE,
        setting_title=SETTING_TITLE,
        canon_facts=tuple(canon_facts),
        contradictions=tuple(adapted["contradictions"]),
        missing_canon=tuple(adapted["missing_canon"]),
        open_questions=tuple(adapted["open_questions"]),
        draft_repair_or_recommendation=DRAFT_REPAIR_OR_RECOMMENDATION,
        next_work_items=tuple(adapted["next_work_items"]),
        explicit_non_proofs=tuple(dict.fromkeys((*fixture.non_proofs, *NON_PROOFS))),
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        first_product_wedge_selected=False,
        phase_387_implemented=False,
        runtime_required=bool(readiness["runtime_required"]),
        provider_model_required=bool(readiness["provider_model_required"]),
        recommended_next_boundary=RECOMMENDED_NEXT_BOUNDARY,
    )


def build_human_override_setting_dossier_output_dict() -> dict[str, Any]:
    return build_human_override_setting_dossier_output().to_dict()


def _render_bullets(items: tuple[Any, ...]) -> list[str]:
    rendered: list[str] = []
    for item in items:
        if isinstance(item, dict):
            fact = item.get("fact", "")
            source = item.get("source", "")
            rendered.append(f"- {fact} [source: {source}]")
        else:
            rendered.append(f"- {item}")
    return rendered


def render_human_override_setting_dossier_markdown(
    output: FounderNativeSettingDossierOutput | None = None,
) -> str:
    dossier = output or build_human_override_setting_dossier_output()
    sections = [
        f"# {dossier.setting_title} Setting Consistency Dossier",
        "",
        f"Boundary: `{dossier.boundary}`",
        f"Output: `{dossier.output_name}`",
        f"Demo candidate: `{dossier.demo_candidate}`",
        "",
        "## Canon Facts",
        *_render_bullets(dossier.canon_facts),
        "",
        "## Contradictions",
        *_render_bullets(dossier.contradictions),
        "",
        "## Missing Canon",
        *_render_bullets(dossier.missing_canon),
        "",
        "## Open Questions",
        *_render_bullets(dossier.open_questions),
        "",
        "## Draft Repair Or Recommendation",
        f"- {dossier.draft_repair_or_recommendation}",
        "",
        "## Next Work Items",
        *_render_bullets(dossier.next_work_items),
        "",
        "## Explicit Non-Proofs",
        *_render_bullets(dossier.explicit_non_proofs),
        "",
        "## Posture",
        f"- product_wedge_selection={dossier.product_wedge_selection}",
        f"- first_product_wedge_selected={str(dossier.first_product_wedge_selected).lower()}",
        f"- phase_387_implemented={str(dossier.phase_387_implemented).lower()}",
        f"- runtime_required={str(dossier.runtime_required).lower()}",
        f"- provider_model_required={str(dossier.provider_model_required).lower()}",
        f"- recommended_next_boundary={dossier.recommended_next_boundary}",
    ]
    return "\n".join(sections)
