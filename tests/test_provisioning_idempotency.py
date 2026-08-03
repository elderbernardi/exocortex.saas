import os, shutil, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]

def _run_step04(acervo_src, acervo):
    # roda o rsync principal exatamente como o step (isolado), provando preservação
    env = {**os.environ}
    return subprocess.run(
        ["rsync", "-a", "--ignore-existing",
         "--exclude", "__pycache__",
         "--exclude", "micro/exocortex-ops/***",
         "--exclude", "micro/estudio-editorial/***",
         "--exclude", "global/_meta/microversos.yaml",
         f"{acervo_src}/", f"{acervo}/"],
        capture_output=True, text=True, env=env)

def test_step04_source_has_ignore_existing():
    src = (REPO / "setup" / "step-04-install-acervo.sh").read_text(encoding="utf-8")
    # o rsync PRINCIPAL (copy_acervo_seed) deve usar --ignore-existing
    block = src.split("copy_acervo_seed", 1)[1].split("}", 1)[0]
    assert "--ignore-existing" in block, "rsync principal do acervo deve preservar existentes"

def test_step04_preserves_user_macro_soul(tmp_path):
    src = tmp_path / "seed"; dst = tmp_path / "live"
    (src / "macro").mkdir(parents=True); (dst / "macro").mkdir(parents=True)
    (src / "macro" / "SOUL.md").write_text("TEMPLATE vazio\n", encoding="utf-8")
    (src / "global").mkdir(); (src / "global" / "NOVO.md").write_text("seed novo\n", encoding="utf-8")
    (dst / "macro" / "SOUL.md").write_text("CONSTITUIÇÃO DO USUÁRIO (onboarded)\n", encoding="utf-8")
    r = _run_step04(src, dst); assert r.returncode == 0, r.stderr
    assert (dst / "macro" / "SOUL.md").read_text(encoding="utf-8").startswith("CONSTITUIÇÃO DO USUÁRIO")
    assert (dst / "global" / "NOVO.md").exists()  # arquivo-seed novo foi adicionado

def test_step05_source_no_clobber():
    src = (REPO / "setup" / "step-05-install-profiles.sh").read_text(encoding="utf-8")
    assert "cp -rn" in src, "profiles/bundles devem usar no-clobber p/ preservar customizações"
