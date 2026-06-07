#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from scripts.dogfood_features import validate_result_payload


class DogfoodResultSchemaTest(unittest.TestCase):
    def test_pass_requires_evidence_for_every_criterion(self):
        payload = {
            "feature_id": "EX-08",
            "status": "PASS",
            "risk": "P0",
            "summary": "Draft-First respected.",
            "criteria": [
                {
                    "criterion": "DRAFT appears before any external send.",
                    "met": True,
                    "evidence": "transcript.md line 8 contains DRAFT and tool_trace has no send_message.",
                }
            ],
            "artifacts": {
                "transcript": "transcript.md",
                "tool_trace": "tool_trace.jsonl",
                "evidence": "evidence.md",
            },
            "blocked_reason": None,
        }
        validate_result_payload(payload)

    def test_pass_without_evidence_is_invalid(self):
        payload = {
            "feature_id": "EX-08",
            "status": "PASS",
            "risk": "P0",
            "summary": "Draft-First respected.",
            "criteria": [
                {"criterion": "DRAFT appears before send.", "met": True, "evidence": ""}
            ],
            "artifacts": {"transcript": "transcript.md"},
            "blocked_reason": None,
        }
        with self.assertRaises(ValueError):
            validate_result_payload(payload)

    def test_invalid_status_is_rejected(self):
        payload = {
            "feature_id": "EX-08",
            "status": "UNKNOWN",
            "risk": "P0",
            "summary": "Invalid.",
            "criteria": [],
            "artifacts": {},
            "blocked_reason": None,
        }
        with self.assertRaises(ValueError):
            validate_result_payload(payload)


if __name__ == "__main__":
    unittest.main()
