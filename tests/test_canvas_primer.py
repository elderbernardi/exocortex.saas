# tests/test_canvas_primer.py
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "docs" / "canvas" / "AGENT-PRIMER.md"

def test_primer_has_required_sections():
    t = P.read_text(encoding="utf-8")
    for h in ["# Canvas de Tarefas", "## Método", "## Loop de condução",
              "## Eventos da Sala", "## Contrato de consciência", "## Colheita → Receita"]:
        assert h in t, f"primer sem seção: {h}"
    # a seção colheita→receita é placeholder F4/Slice B (não descrever endpoints ainda)
    assert "Slice B" in t.split("## Colheita → Receita",1)[1][:400]
