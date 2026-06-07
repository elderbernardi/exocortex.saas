#!/usr/bin/env python3
import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


class OpenRouterFreeModelRouterTest(unittest.TestCase):
    @staticmethod
    def _repo_root() -> Path:
        return Path(__file__).resolve().parents[1]

    @classmethod
    def setUpClass(cls):
        cls.script = cls._repo_root() / "scripts" / "openrouter_free_model_router.py"

    def _write_json(self, path: Path, payload) -> Path:
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def _run(self, *args, env=None, cwd=None):
        cmd = [sys.executable, str(self.script), *args]
        return subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
            cwd=cwd or self._repo_root(),
        )

    def test_json_output_ranks_free_models_by_benchmarked_intelligence(self):
        openrouter_payload = {
            "data": [
                {
                    "id": "moonshotai/kimi-k2.6:free",
                    "canonical_slug": "moonshotai/kimi-k2.6",
                    "name": "MoonshotAI: Kimi K2.6 (free)",
                    "context_length": 262144,
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "openai/gpt-oss-120b:free",
                    "canonical_slug": "openai/gpt-oss-120b",
                    "name": "OpenAI: gpt-oss-120b (free)",
                    "context_length": 131072,
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "meta-llama/llama-3.3-70b-instruct",
                    "canonical_slug": "meta-llama/llama-3.3-70b-instruct",
                    "name": "Meta: Llama 3.3 70B Instruct",
                    "context_length": 131072,
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "google/gemini-2.5-flash",
                    "canonical_slug": "google/gemini-2.5-flash",
                    "name": "Google: Gemini 2.5 Flash",
                    "context_length": 1048576,
                    "pricing": {"prompt": "0.0000003", "completion": "0.0000025"},
                },
            ]
        }
        fox_payload = {
            "moonshotai/kimi-k2.6": {
                "model_id": "moonshotai/kimi-k2.6",
                "model_name": "Kimi K2.6",
                "pass_rate": 92.0,
                "composite_score": 43.25,
                "avg_latency": 24.16,
                "by_category": {
                    "multi_step_tool": {"pass_rate": 100.0},
                    "delegation_reasoning": {"pass_rate": 100.0},
                    "reasoning": {"pass_rate": 80.0},
                    "failure_mode": {"pass_rate": 66.7},
                },
            },
            "openai/gpt-oss-120b": {
                "model_id": "openai/gpt-oss-120b",
                "model_name": "gpt-oss-120b",
                "pass_rate": 84.0,
                "composite_score": 34.13,
                "avg_latency": 7.73,
                "by_category": {
                    "multi_step_tool": {"pass_rate": 85.7},
                    "delegation_reasoning": {"pass_rate": 100.0},
                    "reasoning": {"pass_rate": 100.0},
                    "failure_mode": {"pass_rate": 0.0},
                },
            },
        }

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path = self._write_json(td_path / "openrouter.json", openrouter_payload)
            fox_path = self._write_json(td_path / "fox.json", fox_payload)

            result = self._run(
                "--openrouter-models-source",
                str(openrouter_path),
                "--fox-metrics-source",
                str(fox_path),
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)

            ranked_ids = [item["id"] for item in payload["ranked_free_models"]]
            self.assertEqual(
                ranked_ids,
                [
                    "moonshotai/kimi-k2.6:free",
                    "openai/gpt-oss-120b:free",
                    "meta-llama/llama-3.3-70b-instruct",
                ],
            )
            self.assertEqual(payload["mode"], "report-only")
            self.assertEqual(payload["selected_model"]["id"], "moonshotai/kimi-k2.6:free")
            self.assertAlmostEqual(payload["selected_model"]["intelligence_index"], 92.335, places=3)
            self.assertIsNone(payload["selected_model"]["secondary_index"])
            self.assertFalse(any(item["id"] == "google/gemini-2.5-flash" for item in payload["ranked_free_models"]))

    def test_unbenchmarked_models_use_secondary_openrouter_signal(self):
        openrouter_payload = {
            "data": [
                {
                    "id": "openrouter/owl-alpha",
                    "canonical_slug": "openrouter/owl-alpha",
                    "name": "Owl Alpha",
                    "context_length": 1048756,
                    "created": 1777398589,
                    "description": "High-performance foundation model for agentic workloads and tool use.",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "top_provider": {"max_completion_tokens": 262144},
                    "architecture": {"input_modalities": ["text"]},
                },
                {
                    "id": "google/gemma-4-31b-it:free",
                    "canonical_slug": "google/gemma-4-31b-it-20260402",
                    "name": "Gemma 4 31B",
                    "context_length": 262144,
                    "created": 1775148486,
                    "description": "Multimodal model with configurable reasoning mode and function calling.",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "top_provider": {"max_completion_tokens": 32768},
                    "architecture": {"input_modalities": ["image", "text", "video"]},
                },
                {
                    "id": "qwen/qwen3-coder:free",
                    "canonical_slug": "qwen/qwen3-coder-480b-a35b-07-25",
                    "name": "Qwen3 Coder",
                    "context_length": 1048576,
                    "created": 1753230546,
                    "description": "Optimized for agentic coding tasks such as function calling, tool use, and long-context reasoning.",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "top_provider": {"max_completion_tokens": 262000},
                    "architecture": {"input_modalities": ["text"]},
                },
            ]
        }

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path = self._write_json(td_path / "openrouter.json", openrouter_payload)
            fox_path = self._write_json(td_path / "fox.json", {})

            result = self._run(
                "--openrouter-models-source",
                str(openrouter_path),
                "--fox-metrics-source",
                str(fox_path),
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            ranked_ids = [item["id"] for item in payload["ranked_free_models"]]
            self.assertEqual(
                ranked_ids,
                [
                    "qwen/qwen3-coder:free",
                    "openrouter/owl-alpha",
                    "google/gemma-4-31b-it:free",
                ],
            )
            self.assertEqual(payload["selected_model"]["secondary_source"], "openrouter_catalog_metadata")
            self.assertGreater(payload["selected_model"]["secondary_index"], 0)

    def test_apply_requires_imbroke(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path = self._write_json(td_path / "openrouter.json", {"data": []})
            fox_path = self._write_json(td_path / "fox.json", {})
            result = self._run(
                "--openrouter-models-source",
                str(openrouter_path),
                "--fox-metrics-source",
                str(fox_path),
                "--apply",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--apply exige --imbroke", result.stderr)

    def test_setup_references_imbroke_activation(self):
        setup_text = (self._repo_root() / "setup.sh").read_text(encoding="utf-8")
        self.assertIn("--imbroke", setup_text)
        self.assertIn("configure_openrouter_free_router", setup_text)
        self.assertIn('if [ "$IMBROKE_MODE" = "1" ]', setup_text)

    def test_naive_expiration_timestamp_does_not_crash_filtering(self):
        openrouter_payload = {
            "data": [
                {
                    "id": "moonshotai/kimi-k2.6:free",
                    "canonical_slug": "moonshotai/kimi-k2.6",
                    "name": "MoonshotAI: Kimi K2.6 (free)",
                    "context_length": 262144,
                    "expiration_date": "2099-01-01T00:00:00",
                    "pricing": {"prompt": "0", "completion": "0"},
                }
            ]
        }
        fox_payload = {
            "moonshotai/kimi-k2.6": {
                "model_id": "moonshotai/kimi-k2.6",
                "model_name": "Kimi K2.6",
                "pass_rate": 92.0,
                "composite_score": 43.25,
                "avg_latency": 24.16,
                "by_category": {
                    "multi_step_tool": {"pass_rate": 100.0},
                    "delegation_reasoning": {"pass_rate": 100.0},
                    "reasoning": {"pass_rate": 80.0},
                    "failure_mode": {"pass_rate": 66.7},
                },
            }
        }

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path = self._write_json(td_path / "openrouter.json", openrouter_payload)
            fox_path = self._write_json(td_path / "fox.json", fox_payload)

            result = self._run(
                "--openrouter-models-source",
                str(openrouter_path),
                "--fox-metrics-source",
                str(fox_path),
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["selected_model"]["id"], "moonshotai/kimi-k2.6:free")

    def test_apply_uses_fake_hermes_and_writes_report(self):
        openrouter_payload = {
            "data": [
                {
                    "id": "moonshotai/kimi-k2.6:free",
                    "canonical_slug": "moonshotai/kimi-k2.6",
                    "name": "MoonshotAI: Kimi K2.6 (free)",
                    "context_length": 262144,
                    "pricing": {"prompt": "0", "completion": "0"},
                }
            ]
        }
        fox_payload = {
            "moonshotai/kimi-k2.6": {
                "model_id": "moonshotai/kimi-k2.6",
                "model_name": "Kimi K2.6",
                "pass_rate": 92.0,
                "composite_score": 43.25,
                "avg_latency": 24.16,
                "by_category": {
                    "multi_step_tool": {"pass_rate": 100.0},
                    "delegation_reasoning": {"pass_rate": 100.0},
                    "reasoning": {"pass_rate": 80.0},
                    "failure_mode": {"pass_rate": 66.7},
                },
            }
        }

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path = self._write_json(td_path / "openrouter.json", openrouter_payload)
            fox_path = self._write_json(td_path / "fox.json", fox_payload)
            report_path = td_path / "router-report.json"
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = td_path / "bin"
            fake_bin_dir.mkdir()
            fake_hermes = fake_bin_dir / "hermes"
            fake_hermes.write_text(
                textwrap.dedent(
                    f"""#!/usr/bin/env bash
                    printf '%s\n' \"$*\" >> {str(log_path)!r}
                    exit 0
                    """
                ),
                encoding="utf-8",
            )
            fake_hermes.chmod(fake_hermes.stat().st_mode | stat.S_IEXEC)

            env = os.environ.copy()
            env["PATH"] = f"{fake_bin_dir}:{env['PATH']}"
            env["HERMES_HOME"] = str(td_path / "hermes-home")

            result = self._run(
                "--openrouter-models-source",
                str(openrouter_path),
                "--fox-metrics-source",
                str(fox_path),
                "--imbroke",
                "--apply",
                "--report-path",
                str(report_path),
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(report_path.is_file())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "imbroke")
            self.assertEqual(report["selected_model"]["id"], "moonshotai/kimi-k2.6:free")

            calls = log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                calls,
                [
                    "config set model.provider openrouter",
                    "config set model.default moonshotai/kimi-k2.6:free",
                ],
            )


if __name__ == "__main__":
    unittest.main()
