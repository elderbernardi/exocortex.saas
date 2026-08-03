import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_anti_narration as C

NARRATED = {"messages": [
    {"role": "user", "content": "faça o ofício"},
    {"role": "assistant", "content": "Classificação: Execução. Definição de pronto: ofício aprovado. Vou agir."},
]}
CLEAN = {"messages": [
    {"role": "user", "content": "faça o ofício"},
    {"role": "assistant", "content": "Preparei o rascunho do ofício; aguardando sua aprovação para enviar."},
]}

def test_flags_ptbr_phase_narration():
    hits = C.check_narration(NARRATED["messages"])
    assert hits, "deve pegar 'Classificação:'/'Definição de pronto:' na resposta do agente"

def test_clean_reply_passes():
    assert C.check_narration(CLEAN["messages"]) == []

def test_cli_exit_codes(tmp_path):
    nf = tmp_path / "n.json"; nf.write_text(json.dumps(NARRATED), encoding="utf-8")
    cf = tmp_path / "c.json"; cf.write_text(json.dumps(CLEAN), encoding="utf-8")
    script = str(Path(__file__).resolve().parents[1] / "scripts" / "check_anti_narration.py")
    assert subprocess.run([sys.executable, script, str(nf)]).returncode == 1
    assert subprocess.run([sys.executable, script, str(cf)]).returncode == 0
