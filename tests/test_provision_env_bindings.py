#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class ProvisionEnvBindingsTest(unittest.TestCase):
    @staticmethod
    def _run_common(
        env_file: Path,
        *,
        openrouter_key: str | None,
        firecrawl_key: str | None,
        bind_ip: str | None = None,
        cors_origins: str | None = None,
        upstream_ref: str | None = None,
        allow_floating_upstream_ref: str | None = None,
        command: str = 'ensure_env_file && cat "$EXOCORTEX_PROVISION_ENV_FILE"',
    ):
        repo_root = Path(__file__).resolve().parents[1]
        common = repo_root / "provision" / "hermes-web-ui" / "scripts" / "common.sh"
        env = os.environ.copy()
        env["EXOCORTEX_PROVISION_ENV_FILE"] = str(env_file)
        if openrouter_key is None:
            env.pop("OPENROUTER_API_KEY", None)
        else:
            env["OPENROUTER_API_KEY"] = openrouter_key
        if firecrawl_key is None:
            env.pop("FIRECRAWL_API_KEY", None)
        else:
            env["FIRECRAWL_API_KEY"] = firecrawl_key
        if bind_ip is None:
            env.pop("EXOCORTEX_UI_BIND_IP", None)
        else:
            env["EXOCORTEX_UI_BIND_IP"] = bind_ip
        if cors_origins is None:
            env.pop("CORS_ORIGINS", None)
        else:
            env["CORS_ORIGINS"] = cors_origins
        if upstream_ref is None:
            env.pop("EXOCORTEX_HERMES_WEB_UI_REF", None)
        else:
            env["EXOCORTEX_HERMES_WEB_UI_REF"] = upstream_ref
        if allow_floating_upstream_ref is None:
            env.pop("EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF", None)
        else:
            env["EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF"] = allow_floating_upstream_ref
        return subprocess.run(
            [
                "bash",
                "-lc",
                f'source "{common}" && {command}',
            ],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_common_binds_openrouter_and_firecrawl_into_provision_env(self):
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            run = self._run_common(
                env_file,
                openrouter_key="sk-or-test-openrouter",
                firecrawl_key="fc-test-firecrawl",
            )

            self.assertEqual(run.returncode, 0, run.stderr)
            content = env_file.read_text(encoding="utf-8")
            self.assertIn("OPENROUTER_API_KEY=sk-or-test-openrouter", content)
            self.assertIn("FIRECRAWL_API_KEY=fc-test-firecrawl", content)

    def test_common_preserves_existing_bound_values(self):
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            env_file.write_text(
                "OPENROUTER_API_KEY=sk-or-existing\n"
                "FIRECRAWL_API_KEY=fc-existing\n",
                encoding="utf-8",
            )
            run = self._run_common(
                env_file,
                openrouter_key="sk-or-new",
                firecrawl_key="fc-new",
            )

            self.assertEqual(run.returncode, 0, run.stderr)
            content = env_file.read_text(encoding="utf-8")
            self.assertIn("OPENROUTER_API_KEY=sk-or-existing", content)
            self.assertIn("FIRECRAWL_API_KEY=fc-existing", content)
            self.assertNotIn("sk-or-new", content)
            self.assertNotIn("fc-new", content)

    def test_compose_exposes_both_keys_to_container_environment(self):
        repo_root = Path(__file__).resolve().parents[1]
        compose = (repo_root / "provision" / "hermes-web-ui" / "docker" / "compose.yml").read_text(encoding="utf-8")
        self.assertIn("OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:-}", compose)
        self.assertIn("FIRECRAWL_API_KEY: ${FIRECRAWL_API_KEY:-}", compose)

    def test_security_envelope_blocks_floating_refs_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            run = self._run_common(
                env_file,
                openrouter_key=None,
                firecrawl_key=None,
                upstream_ref="main",
                allow_floating_upstream_ref="0",
                command="ensure_env_file && validate_security_envelope",
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("Ref flutuante 'main' bloqueada", run.stdout)

    def test_security_envelope_accepts_floating_refs_with_explicit_override(self):
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            run = self._run_common(
                env_file,
                openrouter_key=None,
                firecrawl_key=None,
                upstream_ref="main",
                allow_floating_upstream_ref="1",
                command="ensure_env_file && validate_security_envelope",
            )

            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("override explícito", run.stdout)

    def test_security_envelope_requires_cors_when_bind_is_not_loopback(self):
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            run = self._run_common(
                env_file,
                openrouter_key=None,
                firecrawl_key=None,
                bind_ip="0.0.0.0",
                cors_origins="",
                upstream_ref="v0.6.14",
                command="ensure_env_file && validate_security_envelope",
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("CORS_ORIGINS é obrigatório", run.stdout)


if __name__ == "__main__":
    unittest.main()
