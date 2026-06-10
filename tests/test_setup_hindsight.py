#!/usr/bin/env python3
import os
import tempfile
import subprocess
import shutil
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
            
            # Create isolated parent .env
            parent_env = hermes_home / ".env"
            parent_env.write_text(
                "HINDSIGHT_LLM_API_KEY=test-hindsight-llm-key\n"
                "DEEPSEEK_API_KEY=test-deepseek-key\n"
                "OPENROUTER_API_KEY=test-openrouter-key\n"
            )
            
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
            
            # Copy setup.sh to isolated workspace to run it
            repo_root = Path(__file__).resolve().parents[1]
            shutil.copy(repo_root / "setup.sh", isolated_dir / "setup.sh")
            
            # We also need folders like "skills", "acervo", "profiles" etc. because setup.sh copies them
            # Let's create dummy directories so setup.sh doesn't fail
            (isolated_dir / "skills").mkdir()
            (isolated_dir / "acervo").mkdir()
            (isolated_dir / "profiles").mkdir()
            (isolated_dir / "skill-bundles").mkdir()
            
            # Run setup.sh in isolated environment
            new_env = os.environ.copy()
            new_env["HERMES_HOME"] = str(hermes_home)
            new_env["EXOCORTEX_HOME"] = str(exocortex_home)
            new_env["EXOCORTEX_ENABLE_HINDSIGHT"] = "1"
            new_env["PATH"] = f"{bin_dir}:{new_env['PATH']}"
            
            result = subprocess.run(
                ["bash", "./setup.sh"],
                cwd=str(isolated_dir),
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
            self.assertIn("HINDSIGHT_API_LLM_API_KEY=test-hindsight-llm-key", env_content)
            self.assertIn("HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash", env_content)
            self.assertIn("HINDSIGHT_API_LLM_BASE_URL=https://api.deepseek.com/v1", env_content)

if __name__ == "__main__":
    unittest.main()
