import unittest

from orchestrator.backbone_control_loop import (
    BACKBONE_REQUIRED_EVIDENCE_CHAIN_FIELDS,
    BACKBONE_STAGE_NAMES,
    BACKBONE_V0_DECLARED,
    BackboneAdapterDescriptor,
    BackboneStageRecord,
    ordered_backbone_stage_names,
    read_backbone_scaffold_status,
    validate_backbone_stage_record,
)


class Phase316BackboneV0AbstractionScaffoldTests(unittest.TestCase):
    def _record(self, **overrides):
        values = {
            "stage_name": "bounded_action_attempt",
            "record_id": "record_phase316",
            "linked_evidence_chain": {
                "source_record_id": "source_phase316",
                "stage_evidence_id": "evidence_phase316",
            },
            "domain_evidence": {"mechanical_status": "source_test_docs_only"},
            "domain_payload": {"code_patching_task_id": "task_phase316"},
            "activity_flags": {
                "adapter_executed": False,
                "semantic_correctness_claimed": False,
            },
        }
        values.update(overrides)
        return BackboneStageRecord(**values)

    def test_ordered_neutral_stage_list_runs_from_intake_to_readback(self):
        self.assertEqual(
            ordered_backbone_stage_names(),
            (
                "intake_result",
                "eligibility_record",
                "candidate_artifact",
                "operator_decision",
                "promotion_record",
                "draft_action_proposal",
                "authorization_eligibility",
                "authorization_record",
                "bounded_action_attempt",
                "action_result_evidence",
                "mechanical_verification",
                "finalization_record",
                "readback",
            ),
        )
        self.assertEqual(BACKBONE_STAGE_NAMES[0], "intake_result")
        self.assertEqual(BACKBONE_STAGE_NAMES[-1], "readback")

    def test_non_proof_fields_are_first_class(self):
        record = self._record()
        validation = validate_backbone_stage_record(record)

        self.assertTrue(validation["complete"])
        self.assertIn(
            "backbone_scaffold_is_not_semantic_correctness",
            validation["non_proofs"],
        )
        self.assertIn(
            "backbone_scaffold_does_not_declare_backbone_v0",
            validation["non_proofs"],
        )

    def test_domain_evidence_is_distinct_from_domain_payload(self):
        validation = validate_backbone_stage_record(self._record())

        self.assertIn("linked_evidence_chain", validation["native_evidence_fields"])
        self.assertEqual(validation["domain_evidence_keys"], ["mechanical_status"])
        self.assertEqual(validation["domain_specific_payload_keys"], ["code_patching_task_id"])

    def test_adapter_descriptor_names_bounded_context_without_execution(self):
        record = self._record(
            bounded_context_adapter=BackboneAdapterDescriptor(
                adapter_name="code_patching_control_loop",
                bounded_context="code_patching",
            )
        )

        serialized = record.as_dict()

        self.assertEqual(
            serialized["bounded_context_adapter"]["adapter_name"],
            "code_patching_control_loop",
        )
        self.assertFalse(serialized["bounded_context_adapter"]["execution_allowed"])

    def test_missing_required_chain_fields_block_deterministically(self):
        missing_chain = validate_backbone_stage_record(
            self._record(linked_evidence_chain={})
        )
        missing_source = validate_backbone_stage_record(
            self._record(
                linked_evidence_chain={"stage_evidence_id": "evidence_phase316"}
            )
        )
        missing_evidence = validate_backbone_stage_record(
            self._record(linked_evidence_chain={"source_record_id": "source_phase316"})
        )

        self.assertEqual(missing_chain["status"], "incomplete")
        self.assertEqual(missing_chain["reason_code"], "linked_evidence_chain_missing")
        self.assertEqual(missing_source["reason_code"], "source_record_id_missing")
        self.assertEqual(missing_evidence["reason_code"], "stage_evidence_id_missing")

    def test_required_native_fields_are_not_patch_file_diff_hash_specific(self):
        forbidden_terms = ("patch", "file", "diff", "hash")
        required_text = " ".join(BACKBONE_REQUIRED_EVIDENCE_CHAIN_FIELDS)

        for term in forbidden_terms:
            self.assertNotIn(term, required_text)

    def test_domain_specific_payload_keys_do_not_become_native_fields(self):
        validation = validate_backbone_stage_record(
            self._record(
                domain_payload={
                    "domain_ticket": "ticket_phase316",
                    "patch_candidate": "payload_only",
                }
            )
        )

        self.assertIn("patch_candidate", validation["domain_specific_payload_keys"])
        self.assertNotIn("patch_candidate", validation["native_evidence_fields"])

    def test_scaffold_explicitly_does_not_declare_backbone_v0(self):
        status = read_backbone_scaffold_status()

        self.assertFalse(BACKBONE_V0_DECLARED)
        self.assertFalse(status["backbone_v0_declared"])
        self.assertEqual(
            status["backbone_scaffold_status"],
            "backbone_v0_not_declared_scaffold_only",
        )

    def test_unknown_stage_and_missing_id_have_deterministic_reason_codes(self):
        unknown = validate_backbone_stage_record(self._record(stage_name="not_a_stage"))
        missing_id = validate_backbone_stage_record(self._record(record_id=""))

        self.assertEqual(unknown["reason_code"], "unknown_stage_name")
        self.assertEqual(missing_id["reason_code"], "record_id_missing")

    def test_activity_flags_are_preserved_without_correctness_claims(self):
        validation = validate_backbone_stage_record(
            self._record(activity_flags={"semantic_correctness_claimed": False})
        )

        self.assertEqual(
            validation["activity_flags"],
            {"semantic_correctness_claimed": False},
        )
        self.assertFalse(validation["backbone_v0_declared"])


if __name__ == "__main__":
    unittest.main()
