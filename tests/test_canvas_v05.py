import importlib.util
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / \
    "acervo/global/tools/harness/canvas_schema.py"


def _load():
    spec = importlib.util.spec_from_file_location("cs", SCHEMA_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CANVAS_SCHEMA


def test_v05_intent_type_superset_de_8():
    s = _load()
    assert set(s["properties"]["intent_type"]["enum"]) == {
        "explorar", "decidir", "produzir", "revisar", "manter",
        "publicar", "ingestao", "outro"}


def test_v05_campos_do_metodo_presentes_e_opcionais():
    s = _load()
    for campo in ("shape", "done_criteria", "verification"):
        assert campo in s["properties"], campo
        assert campo not in s["required"], campo
    assert set(s["properties"]["shape"]["enum"]) == {
        "pergunta", "plano-primeiro", "tarefa"}


def test_v05_nucleo_preservado():
    s = _load()
    assert s["required"] == ["focus", "vetor", "intent_type"]
    assert set(s["properties"]["vetor"]["enum"]) == {
        "execucao", "evolucao", "manutencao", "ambiguo"}
    assert s["properties"]["focus"]["minLength"] == 3
    assert s["additionalProperties"] is False


import os
import subprocess
import sys

import yaml

REGISTER = str(Path(__file__).resolve().parents[1] /
               "acervo/global/tools/harness/register_task_from_canvas.py")


def _run_register(tmp_path, canvas_yaml: str, extra=()):
    acervo = tmp_path / "acervo"
    (acervo / "_tasks").mkdir(parents=True)
    (acervo / "global/templates/harness-v0.4").mkdir(parents=True)
    src = Path(__file__).resolve().parents[1] / \
        "acervo/global/templates/harness-v0.4/task.yaml"
    (acervo / "global/templates/harness-v0.4/task.yaml").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8")
    cpath = tmp_path / "c.yaml"
    cpath.write_text(canvas_yaml, encoding="utf-8")
    env = dict(os.environ, ACERVO=str(acervo))
    proc = subprocess.run(
        [sys.executable, REGISTER, "--canvas", str(cpath), "--title", "Tarefa X",
         *extra], env=env, capture_output=True, text=True)
    return proc, acervo


def test_register_le_vetor_v05(tmp_path):
    proc, acervo = _run_register(tmp_path, "vetor: manutencao\nfocus: f\n")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    task_yaml_path = next((acervo / "_tasks").glob("task_*/task.yaml"))
    doc = yaml.safe_load(task_yaml_path.read_text())
    assert doc["vetor"] == "manutencao"


def test_register_fallback_vector_v04(tmp_path):
    proc, acervo = _run_register(tmp_path, "vector: evolucao\nfocus: f\n")
    assert proc.returncode == 0
    task_yaml_path = next((acervo / "_tasks").glob("task_*/task.yaml"))
    doc = yaml.safe_load(task_yaml_path.read_text())
    assert doc["vetor"] == "evolucao"


def test_register_rejeita_ambiguo(tmp_path):
    proc, _ = _run_register(tmp_path, "vetor: ambiguo\nfocus: f\n")
    assert proc.returncode == 1
    assert "ambiguo" in (proc.stderr + proc.stdout)


def test_task_id_tem_sufixo_de_unicidade(tmp_path):
    proc, acervo = _run_register(tmp_path, "vetor: execucao\n")
    task_dir = next((acervo / "_tasks").glob("task_*")).name
    import re
    assert re.fullmatch(r"task_\d{8}_[a-z0-9-]+_\d{6}", task_dir), task_dir


def test_task_yaml_tem_task_id_real(tmp_path):
    proc, acervo = _run_register(tmp_path, "vetor: execucao\nfocus: f\n")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    task_dir = next((acervo / "_tasks").glob("task_*"))
    doc = yaml.safe_load((task_dir / "task.yaml").read_text())
    assert doc["task_id"] == task_dir.name
    assert doc["task_id"] != "task_YYYYMMDD_slug"
