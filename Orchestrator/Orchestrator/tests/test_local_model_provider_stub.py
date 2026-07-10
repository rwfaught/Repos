import unittest

from orchestrator.local_model_provider_stub import (
    DisabledLocalModelProvider,
    StaticLocalModelProvider,
)
from orchestrator.local_model_reasoning_contract import build_local_model_interpretation_request


class LocalModelProviderStubTests(unittest.TestCase):
    def setUp(self):
        self.request = build_local_model_interpretation_request("prompt-001", "Classify these labels")

    def test_disabled_provider_is_explicitly_non_executing(self):
        result = DisabledLocalModelProvider().interpret(self.request)

        self.assertEqual(result.status, "disabled")
        self.assertEqual(result.provider_key, "local_model_disabled_stub")
        self.assertIsNone(result.response)
        self.assertFalse(result.execution_performed)

    def test_static_provider_returns_caller_supplied_data_without_execution(self):
        response = {"arbitrary": "test data"}
        result = StaticLocalModelProvider(response).interpret(self.request)

        self.assertEqual(result.status, "stub_response")
        self.assertEqual(result.response, response)
        self.assertFalse(result.execution_performed)
        self.assertIn("no model was invoked", result.detail)

    def test_static_provider_preserves_raw_text_for_normalization(self):
        raw = "<think></think>{\"candidate\": true}[end of text]"
        result = StaticLocalModelProvider(raw).interpret(self.request)

        self.assertIsNone(result.response)
        self.assertEqual(result.raw_output, raw)
        self.assertFalse(result.execution_performed)


if __name__ == "__main__":
    unittest.main()
