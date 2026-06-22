#!/usr/bin/env python3
import os
import tempfile
import subprocess
import unittest
from pathlib import Path

class SetupHindsightTest(unittest.TestCase):
    def test_hindsight_setup_isolated(self):
        with tempfile.TemporaryDirectory() as td:
            # Setup isolated environment dirs
            isolated_dir = Path(td)
            hermes_home = isolated_dir / ".hermes"
            exocortex_home = isolated_dir / "exocortex"
            hermes_home.mkdir()
            exocortex_home.mkdir()
            
            # Create isolated config.yaml
            parent_config = hermes_home / "config.yaml"
            parent_config.write_text(
                "model:\n"
                "  default: deepseek\n"
                "  base_url: https://api.deepseek.com/v1\n"
            )
            
            # Mock docker command by placing a mock docker script in PATH
            bin_dir = isolated_dir / "bin"
            bin_dir.mkdir()
            mock_docker = bin_dir / "docker"
            mock_docker.write_text(
                "#!/bin/sh\n"
                "echo \"Mock docker called with: $@\"\n"
                "exit 0\n"
            )
            mock_docker.chmod(0o755)
            
            # Run the Hindsight setup step directly in isolated environment
            repo_root = Path(__file__).resolve().parents[1]
            step_script = repo_root / "setup" / "step-01-hindsight.sh"

            new_env = os.environ.copy()
            new_env["HERMES_HOME"] = str(hermes_home)
            new_env["EXOCORTEX_HOME"] = str(exocortex_home)
            new_env["EXOCORTEX_ENABLE_HINDSIGHT"] = "1"
            new_env["PATH"] = f"{bin_dir}:{new_env['PATH']}"
            # Hindsight's LLM backend uses the 'auxiliar' role, which inherits the
            # 'default' role here (only DEFAULT is set). Base URL is derived from
            # the provider catalog (deepseek -> https://api.deepseek.com/v1).
            new_env["EXOCORTEX_DEFAULT_PROVIDER"] = "deepseek"
            new_env["EXOCORTEX_DEFAULT_MODEL"] = "deepseek-v4-pro"
            new_env["EXOCORTEX_DEFAULT_API_KEY"] = "test-aux-key"
            for stale in ("EXOCORTEX_AUX_PROVIDER", "EXOCORTEX_AUX_MODEL",
                          "EXOCORTEX_AUX_API_KEY", "EXOCORTEX_AUX_BASE_URL"):
                new_env.pop(stale, None)
            
            result = subprocess.run(
                ["bash", str(step_script)],
                cwd=str(repo_root),
                env=new_env,
                capture_output=True,
                text=True
            )
            
            # Verify setup.sh outputs indicating it successfully configured Hindsight
            self.assertIn("Hindsight .env criado", result.stdout)
            
            # Check that the hindsight local .env was generated correctly with resolved keys
            hs_env = hermes_home / "hindsight-local" / ".env"
            self.assertTrue(hs_env.exists())
            
            env_content = hs_env.read_text()
            self.assertIn("HINDSIGHT_API_LLM_API_KEY=test-aux-key", env_content)
            self.assertIn("HINDSIGHT_API_LLM_MODEL=deepseek-v4-pro", env_content)
            self.assertIn("HINDSIGHT_API_LLM_BASE_URL=https://api.deepseek.com/v1", env_content)

            # Check that setup aligned Hermes memory config for Hindsight without disabling built-in memory
            config_content = parent_config.read_text()
            self.assertIn("provider: hindsight", config_content)
            self.assertIn("memory_enabled: true", config_content)
            self.assertIn("user_profile_enabled: true", config_content)

if __name__ == "__main__":
    unittest.main()
