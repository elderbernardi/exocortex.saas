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
        if env is None:
            # Isolate from live sentinel/state to prevent test pollution
            env = os.environ.copy()
            env["HERMES_HOME"] = str(Path(tempfile.mkdtemp()) / "hermes-test-home")
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


class CircuitBreakerTest(unittest.TestCase):
    """Tests for imbroke circuit breaker, sentinel, guard tripwire, and cron scheduling."""

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
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, env=env, cwd=cwd or self._repo_root(),
        )

    def _make_fixtures(self, td_path):
        """Create standard openrouter + fox test fixtures."""
        openrouter_payload = {
            "data": [
                {
                    "id": "moonshotai/kimi-k2.6:free",
                    "canonical_slug": "moonshotai/kimi-k2.6",
                    "name": "Kimi K2.6 (free)",
                    "context_length": 262144,
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "openai/gpt-oss-120b:free",
                    "canonical_slug": "openai/gpt-oss-120b",
                    "name": "gpt-oss-120b (free)",
                    "context_length": 131072,
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "meta-llama/llama-3.3-70b-instruct",
                    "canonical_slug": "meta-llama/llama-3.3-70b-instruct",
                    "name": "Llama 3.3 70B",
                    "context_length": 131072,
                    "pricing": {"prompt": "0", "completion": "0"},
                },
            ]
        }
        fox_payload = {
            "moonshotai/kimi-k2.6": {
                "model_id": "moonshotai/kimi-k2.6",
                "pass_rate": 92.0, "composite_score": 43.25, "avg_latency": 24.16,
                "by_category": {
                    "multi_step_tool": {"pass_rate": 100.0},
                    "delegation_reasoning": {"pass_rate": 100.0},
                    "reasoning": {"pass_rate": 80.0},
                    "failure_mode": {"pass_rate": 66.7},
                },
            },
            "openai/gpt-oss-120b": {
                "model_id": "openai/gpt-oss-120b",
                "pass_rate": 84.0, "composite_score": 34.13, "avg_latency": 7.73,
                "by_category": {
                    "multi_step_tool": {"pass_rate": 85.7},
                    "delegation_reasoning": {"pass_rate": 100.0},
                    "reasoning": {"pass_rate": 100.0},
                    "failure_mode": {"pass_rate": 0.0},
                },
            },
        }
        openrouter_path = self._write_json(td_path / "openrouter.json", openrouter_payload)
        fox_path = self._write_json(td_path / "fox.json", fox_payload)
        return openrouter_path, fox_path

    def _make_fake_hermes(self, td_path, log_path, provider_response="openrouter", model_response="some-model"):
        """Create a fake hermes binary that logs calls and responds to config get."""
        fake_bin_dir = td_path / "bin"
        fake_bin_dir.mkdir(exist_ok=True)
        fake_hermes = fake_bin_dir / "hermes"
        fake_hermes.write_text(
            textwrap.dedent(
                f"""#!/usr/bin/env bash
                printf '%s\\n' "$*" >> {str(log_path)!r}
                # Respond to config get
                if [[ "$1" == "config" && "$2" == "get" ]]; then
                    if [[ "$3" == "model.provider" ]]; then
                        echo "{provider_response}"
                        exit 0
                    elif [[ "$3" == "model.default" ]]; then
                        echo "{model_response}"
                        exit 0
                    else
                        exit 1
                    fi
                fi
                # Respond to cron create
                if [[ "$1" == "cron" && "$2" == "create" ]]; then
                    echo "fake-cron-id-$RANDOM"
                    exit 0
                fi
                exit 0
                """
            ),
            encoding="utf-8",
        )
        fake_hermes.chmod(fake_hermes.stat().st_mode | stat.S_IEXEC)
        return fake_bin_dir

    def _make_env(self, td_path, fake_bin_dir):
        """Create environment with fake hermes and HERMES_HOME."""
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin_dir}:{env['PATH']}"
        env["HERMES_HOME"] = str(td_path / "hermes-home")
        return env

    def test_activate_creates_sentinel_and_applies_config(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path, fox_path = self._make_fixtures(td_path)
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = self._make_fake_hermes(td_path, log_path)
            env = self._make_env(td_path, fake_bin_dir)

            result = self._run(
                "--openrouter-models-source", str(openrouter_path),
                "--fox-metrics-source", str(fox_path),
                "--imbroke", "--activate",
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            # Sentinel should exist
            sentinel_path = td_path / "hermes-home" / "model-routing" / "imbroke-state.json"
            self.assertTrue(sentinel_path.is_file())
            state = json.loads(sentinel_path.read_text(encoding="utf-8"))
            self.assertTrue(state["active"])
            self.assertEqual(state["current_model"], "moonshotai/kimi-k2.6:free")
            self.assertEqual(state["previous_provider"], "openrouter")
            self.assertIn("watchdog_cron_id", state)

            # hermes config set should have been called
            calls = log_path.read_text(encoding="utf-8")
            self.assertIn("config set model.provider openrouter", calls)
            self.assertIn("config set model.default moonshotai/kimi-k2.6:free", calls)

            # Notification should mention activation
            self.assertIn("[IMBROKE]", result.stdout)

    def test_activate_requires_imbroke_flag(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path, fox_path = self._make_fixtures(td_path)
            result = self._run(
                "--openrouter-models-source", str(openrouter_path),
                "--fox-metrics-source", str(fox_path),
                "--activate",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--activate exige --imbroke", result.stderr)

    def test_deactivate_restores_previous_config(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = self._make_fake_hermes(td_path, log_path, provider_response="anthropic", model_response="claude-sonnet")
            env = self._make_env(td_path, fake_bin_dir)

            # Create a sentinel manually
            sentinel_dir = td_path / "hermes-home" / "model-routing"
            sentinel_dir.mkdir(parents=True)
            sentinel_path = sentinel_dir / "imbroke-state.json"
            sentinel_path.write_text(json.dumps({
                "active": True,
                "activated_at": "2026-06-08T01:00:00Z",
                "previous_provider": "anthropic",
                "previous_model": "claude-sonnet-4-20250514",
                "current_model": "moonshotai/kimi-k2.6:free",
                "current_rating": 9.2,
                "failed_models": {},
                "recovery_cron_id": None,
                "watchdog_cron_id": "fake-watchdog-123",
            }), encoding="utf-8")

            result = self._run("--deactivate", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)

            # Sentinel should be removed
            self.assertFalse(sentinel_path.is_file())

            # Previous config should be restored
            calls = log_path.read_text(encoding="utf-8")
            self.assertIn("config set model.provider anthropic", calls)
            self.assertIn("config set model.default claude-sonnet-4-20250514", calls)

            # Watchdog cron should be cancelled
            self.assertIn("cron remove fake-watchdog-123", calls)

            # Notification
            self.assertIn("[IMBROKE OFF]", result.stdout)

    def test_status_shows_inactive_when_no_sentinel(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env = os.environ.copy()
            env["HERMES_HOME"] = str(td_path / "hermes-home")

            result = self._run("--status", env=env)
            self.assertEqual(result.returncode, 0)
            self.assertIn("INATIVO", result.stdout)

    def test_status_shows_active_state(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env = os.environ.copy()
            env["HERMES_HOME"] = str(td_path / "hermes-home")

            sentinel_dir = td_path / "hermes-home" / "model-routing"
            sentinel_dir.mkdir(parents=True)
            (sentinel_dir / "imbroke-state.json").write_text(json.dumps({
                "active": True,
                "activated_at": "2026-06-08T01:00:00Z",
                "previous_provider": "anthropic",
                "previous_model": "claude-sonnet",
                "current_model": "moonshotai/kimi-k2.6:free",
                "current_rating": 9.2,
                "failed_models": {"some-model:free": {"reason": "rate_limit", "cooldown_until": "2026-06-08T02:00:00Z"}},
                "recovery_cron_id": "rec-123",
                "watchdog_cron_id": "watch-456",
            }), encoding="utf-8")

            result = self._run("--status", env=env)
            self.assertEqual(result.returncode, 0)
            self.assertIn("ATIVO", result.stdout)
            self.assertIn("kimi-k2.6:free", result.stdout)
            self.assertIn("rate_limit", result.stdout)

    def test_mark_failed_without_imbroke_active_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path, fox_path = self._make_fixtures(td_path)
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = self._make_fake_hermes(td_path, log_path)
            env = self._make_env(td_path, fake_bin_dir)

            result = self._run(
                "--openrouter-models-source", str(openrouter_path),
                "--fox-metrics-source", str(fox_path),
                "--mark-failed", "moonshotai/kimi-k2.6:free",
                "--fail-reason", "rate_limit",
                env=env,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_mark_failed_failover_to_next_model(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path, fox_path = self._make_fixtures(td_path)
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = self._make_fake_hermes(td_path, log_path)
            env = self._make_env(td_path, fake_bin_dir)

            # Create active sentinel
            sentinel_dir = td_path / "hermes-home" / "model-routing"
            sentinel_dir.mkdir(parents=True)
            (sentinel_dir / "imbroke-state.json").write_text(json.dumps({
                "active": True,
                "activated_at": "2026-06-08T01:00:00Z",
                "previous_provider": "anthropic",
                "previous_model": "claude-sonnet",
                "current_model": "moonshotai/kimi-k2.6:free",
                "current_rating": 9.2,
                "failed_models": {},
                "recovery_cron_id": None,
                "watchdog_cron_id": "watch-456",
            }), encoding="utf-8")

            result = self._run(
                "--openrouter-models-source", str(openrouter_path),
                "--fox-metrics-source", str(fox_path),
                "--mark-failed", "moonshotai/kimi-k2.6:free",
                "--fail-reason", "rate_limit",
                "--cooldown", "1800",
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            # Should have failed over to next model
            state = json.loads((sentinel_dir / "imbroke-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["current_model"], "openai/gpt-oss-120b:free")
            self.assertIn("moonshotai/kimi-k2.6:free", state["failed_models"])
            self.assertEqual(state["failed_models"]["moonshotai/kimi-k2.6:free"]["reason"], "rate_limit")
            self.assertIsNotNone(state.get("recovery_cron_id"))

            # hermes should have applied the new model
            calls = log_path.read_text(encoding="utf-8")
            self.assertIn("config set model.default openai/gpt-oss-120b:free", calls)

            # Notification should mention failover
            self.assertIn("[FAILOVER]", result.stdout)
            self.assertIn("gpt-oss-120b:free", result.stdout)

    def test_guard_detects_provider_change_and_auto_deactivates(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            log_path = td_path / "hermes-calls.log"
            # Fake hermes responds with "openai" as provider (simulating external change)
            fake_bin_dir = self._make_fake_hermes(td_path, log_path, provider_response="openai", model_response="gpt-4o")
            env = self._make_env(td_path, fake_bin_dir)

            # Create active sentinel
            sentinel_dir = td_path / "hermes-home" / "model-routing"
            sentinel_dir.mkdir(parents=True)
            sentinel_path = sentinel_dir / "imbroke-state.json"
            sentinel_path.write_text(json.dumps({
                "active": True,
                "activated_at": "2026-06-08T01:00:00Z",
                "previous_provider": "anthropic",
                "previous_model": "claude-sonnet",
                "current_model": "moonshotai/kimi-k2.6:free",
                "current_rating": 9.2,
                "failed_models": {},
                "recovery_cron_id": "rec-123",
                "watchdog_cron_id": "watch-456",
            }), encoding="utf-8")

            result = self._run("--guard", env=env)
            self.assertEqual(result.returncode, 0)

            # Sentinel should be removed
            self.assertFalse(sentinel_path.is_file())

            # Crons should be cancelled
            calls = log_path.read_text(encoding="utf-8")
            self.assertIn("cron remove rec-123", calls)
            self.assertIn("cron remove watch-456", calls)

            # Notification should mention auto-off
            self.assertIn("[AUTO-OFF]", result.stdout)
            self.assertIn("openai", result.stdout)

    def test_guard_keeps_imbroke_when_provider_is_openrouter(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = self._make_fake_hermes(td_path, log_path, provider_response="openrouter")
            env = self._make_env(td_path, fake_bin_dir)

            sentinel_dir = td_path / "hermes-home" / "model-routing"
            sentinel_dir.mkdir(parents=True)
            sentinel_path = sentinel_dir / "imbroke-state.json"
            sentinel_path.write_text(json.dumps({
                "active": True,
                "activated_at": "2026-06-08T01:00:00Z",
                "previous_provider": "anthropic",
                "previous_model": "claude-sonnet",
                "current_model": "moonshotai/kimi-k2.6:free",
                "current_rating": 9.2,
                "failed_models": {},
                "recovery_cron_id": None,
                "watchdog_cron_id": "watch-456",
            }), encoding="utf-8")

            result = self._run("--guard", env=env)
            self.assertEqual(result.returncode, 0)

            # Sentinel should still exist
            self.assertTrue(sentinel_path.is_file())
            # No auto-off notification
            self.assertNotIn("[AUTO-OFF]", result.stdout)

    def test_activate_and_deactivate_manages_environment_hint(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            openrouter_path, fox_path = self._make_fixtures(td_path)
            log_path = td_path / "hermes-calls.log"
            fake_bin_dir = self._make_fake_hermes(td_path, log_path)
            env = self._make_env(td_path, fake_bin_dir)

            # Create existing config.yaml with environment hint
            hermes_home = td_path / "hermes-home"
            hermes_home.mkdir(parents=True, exist_ok=True)
            config_path = hermes_home / "config.yaml"
            config_path.write_text(
                "model:\n  provider: openrouter\n  default: original-model\nagent:\n  environment_hint: 'original-hint'\n",
                encoding="utf-8"
            )

            # Activate
            result = self._run(
                "--openrouter-models-source", str(openrouter_path),
                "--fox-metrics-source", str(fox_path),
                "--imbroke", "--activate",
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            # State should store the original hint
            sentinel_path = hermes_home / "model-routing" / "imbroke-state.json"
            self.assertTrue(sentinel_path.is_file())
            state = json.loads(sentinel_path.read_text(encoding="utf-8"))
            self.assertEqual(state["previous_environment_hint"], "original-hint")

            # Config should have the new hint
            import yaml
            content = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertIn("[IMBROKE MODE]", content["agent"]["environment_hint"])

            # Deactivate
            result = self._run("--deactivate", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)

            # Hint should be restored
            content = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertEqual(content["agent"]["environment_hint"], "original-hint")


class CircuitBreakerUnitTest(unittest.TestCase):
    """Unit tests for circuit breaker pure functions."""

    def test_is_model_available_not_in_failed(self):
        from scripts.openrouter_free_model_router import is_model_available
        self.assertTrue(is_model_available("some-model", {}))

    def test_is_model_available_cooldown_expired(self):
        from scripts.openrouter_free_model_router import is_model_available
        failed = {"some-model": {"cooldown_until": "2020-01-01T00:00:00Z"}}
        self.assertTrue(is_model_available("some-model", failed))

    def test_is_model_available_cooldown_not_expired(self):
        from scripts.openrouter_free_model_router import is_model_available
        failed = {"some-model": {"cooldown_until": "2099-01-01T00:00:00Z"}}
        self.assertFalse(is_model_available("some-model", failed))

    def test_select_with_failover_skips_failed(self):
        from scripts.openrouter_free_model_router import select_with_failover, RankedModel
        ranked = [
            RankedModel(id="model-a", canonical_slug="a", name="A", context_length=1000,
                        pricing={}, benchmarked=True, intelligence_index=90.0,
                        pass_rate=90.0, composite_score=40.0, avg_latency=10.0,
                        fox_model_id="a", benchmark_timestamp="t", secondary_source=None, secondary_index=None),
            RankedModel(id="model-b", canonical_slug="b", name="B", context_length=1000,
                        pricing={}, benchmarked=True, intelligence_index=80.0,
                        pass_rate=80.0, composite_score=30.0, avg_latency=10.0,
                        fox_model_id="b", benchmark_timestamp="t", secondary_source=None, secondary_index=None),
        ]
        failed = {"model-a": {"cooldown_until": "2099-01-01T00:00:00Z"}}
        selected = select_with_failover(ranked, failed)
        self.assertEqual(selected.id, "model-b")

    def test_select_with_failover_all_failed_picks_soonest_expiry(self):
        from scripts.openrouter_free_model_router import select_with_failover, RankedModel
        ranked = [
            RankedModel(id="model-a", canonical_slug="a", name="A", context_length=1000,
                        pricing={}, benchmarked=True, intelligence_index=90.0,
                        pass_rate=90.0, composite_score=40.0, avg_latency=10.0,
                        fox_model_id="a", benchmark_timestamp="t", secondary_source=None, secondary_index=None),
            RankedModel(id="model-b", canonical_slug="b", name="B", context_length=1000,
                        pricing={}, benchmarked=True, intelligence_index=80.0,
                        pass_rate=80.0, composite_score=30.0, avg_latency=10.0,
                        fox_model_id="b", benchmark_timestamp="t", secondary_source=None, secondary_index=None),
        ]
        failed = {
            "model-a": {"cooldown_until": "2099-06-01T00:00:00Z"},
            "model-b": {"cooldown_until": "2099-01-01T00:00:00Z"},
        }
        selected = select_with_failover(ranked, failed)
        # model-b expires sooner
        self.assertEqual(selected.id, "model-b")

    def test_format_status_inactive(self):
        from scripts.openrouter_free_model_router import format_status
        result = format_status(None)
        self.assertIn("INATIVO", result)

    def test_format_status_active(self):
        from scripts.openrouter_free_model_router import format_status
        state = {
            "active": True,
            "activated_at": "2026-06-08T01:00:00Z",
            "previous_provider": "anthropic",
            "previous_model": "claude-sonnet",
            "current_model": "kimi-k2.6:free",
            "current_rating": 9.2,
            "failed_models": {},
            "recovery_cron_id": None,
            "watchdog_cron_id": "w-123",
        }
        result = format_status(state)
        self.assertIn("ATIVO", result)
        self.assertIn("kimi-k2.6:free", result)

    def test_build_imbroke_hint(self):
        from scripts.openrouter_free_model_router import _build_imbroke_hint
        hint = _build_imbroke_hint("test-model", 8.5)
        self.assertIn("[IMBROKE MODE]", hint)
        self.assertIn("test-model", hint)
        self.assertIn("8.5/10", hint)

    def test_fallback_providers_writes_both_keys(self):
        from scripts.openrouter_free_model_router import _set_fallback_providers
        import yaml

        with tempfile.TemporaryDirectory() as td:
            # Set HERMES_HOME env var for testing
            os.environ["HERMES_HOME"] = td
            config_path = Path(td) / "config.yaml"
            config_path.write_text("model:\n  provider: openrouter\n", encoding="utf-8")

            fallback_list = [{"provider": "openrouter", "model": "model-a"}]
            success = _set_fallback_providers(fallback_list)
            self.assertTrue(success)

            # Check that both keys are set
            content = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertEqual(content["fallback_providers"], fallback_list)
            self.assertEqual(content["fallback_model"], fallback_list)

    def test_fallback_providers_manual_writes_both_keys(self):
        from scripts.openrouter_free_model_router import _set_fallback_providers_manual

        with tempfile.TemporaryDirectory() as td:
            config_path = Path(td) / "config.yaml"
            config_path.write_text("model:\n  provider: openrouter\nfallback_providers: []\nfallback_model: []\n", encoding="utf-8")

            fallback_list = [{"provider": "openrouter", "model": "model-a"}]
            success = _set_fallback_providers_manual(config_path, fallback_list)
            self.assertTrue(success)

            text = config_path.read_text(encoding="utf-8")
            self.assertIn("fallback_providers:", text)
            self.assertIn("fallback_model:", text)
            self.assertIn("- provider: openrouter", text)
            self.assertIn("model: model-a", text)

    def test_set_environment_hint(self):
        from scripts.openrouter_free_model_router import _set_environment_hint
        import yaml

        with tempfile.TemporaryDirectory() as td:
            os.environ["HERMES_HOME"] = td
            config_path = Path(td) / "config.yaml"
            config_path.write_text("model:\n  provider: openrouter\n", encoding="utf-8")

            success = _set_environment_hint("test-hint")
            self.assertTrue(success)

            content = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertEqual(content["agent"]["environment_hint"], "test-hint")

            # Test clearing the hint
            success = _set_environment_hint(None)
            self.assertTrue(success)
            content = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertNotIn("environment_hint", content.get("agent", {}))


if __name__ == "__main__":
    unittest.main()

