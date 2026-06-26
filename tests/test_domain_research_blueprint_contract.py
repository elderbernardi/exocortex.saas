from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = REPO_ROOT / "docs/architecture/domain-research-blueprint.md"
AGRONEGOCIO_EXAMPLE = REPO_ROOT / "docs/architecture/examples/agronegocio-research-config.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_blueprint_document_exists_and_covers_required_sections() -> None:
    text = _read(BLUEPRINT)
    for needle in [
        "## 3. Anatomia mínima do wrapper",
        "## 5. Contrato de fontes por camada",
        "## 6. Checklist de ativação de um novo domínio",
        "## 7. Exemplo completo — Agronegócio Brasil",
        "Issue de fontes/crawler: [#98]",
        "Issue do wrapper CPG: [#99]",
    ]:
        assert needle in text


def test_blueprint_documents_reference_wrapper_and_json_contract() -> None:
    text = _read(BLUEPRINT)
    assert "skills/excrtx-research-cpg-brasil/scripts/orchestrate.py" in text
    assert "structured_sources" in text
    assert "--document" in text
    assert "--output md|json" in text


def test_agronegocio_example_config_contains_real_sources_and_templates() -> None:
    text = _read(AGRONEGOCIO_EXAMPLE)
    for needle in [
        "https://abag.com.br/",
        "https://cnabrasil.org.br/",
        "https://www.embrapa.br/",
        "https://www.cepea.esalq.usp.br/",
        "https://www.noticiasagricolas.com.br/",
        "panorama:",
        "graos:",
        "pecuaria:",
        "insumos:",
        "comercio_exterior:",
    ]:
        assert needle in text
