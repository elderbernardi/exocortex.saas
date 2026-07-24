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
