from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SOUL_SEED = REPO_ROOT / "SOUL_SEED.md"
WELCOME = REPO_ROOT / "acervo/global/knowledge/WELCOME.md"
FEATURES = REPO_ROOT / "FEATURES.md"
ONBOARD_WELCOME = REPO_ROOT / "skills/excrtx-onboard-welcome/SKILL.md"
ONBOARD_INTERVIEW = REPO_ROOT / "skills/excrtx-onboard-interview/SKILL.md"
SCHEMA_REF = REPO_ROOT / "skills/excrtx-onboard-interview/references/business-context-schema.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_soul_seed_exposes_business_context_placeholder() -> None:
    text = _read(SOUL_SEED)
    assert "## Contexto de Negócio" in text
    assert "industry: string|null" in text
    assert "companies: []" in text
    assert "competitors: []" in text


def test_onboard_interview_documents_six_blocks_and_parseable_contract() -> None:
    text = _read(ONBOARD_INTERVIEW)
    assert "Interview (6 blocks)" in text
    assert "Block D — Business Context" in text
    assert "industry: bens de consumo domésticos" in text
    assert "companies:" in text
    assert "competitors:" in text
    assert "references/business-context-schema.md" in text


def test_reference_schema_exists_and_contains_skip_defaults() -> None:
    text = _read(SCHEMA_REF)
    assert "EXCRTX:BUSINESS_CONTEXT:BEGIN" in text
    assert "industry: null" in text
    assert "companies: []" in text
    assert "competitors: []" in text


def test_welcome_surface_and_feature_catalog_advertise_six_block_onboarding() -> None:
    welcome_text = _read(WELCOME)
    features_text = _read(FEATURES)
    welcome_skill_text = _read(ONBOARD_WELCOME)

    assert "São 6 blocos de perguntas" in welcome_text
    assert "Contexto de Negócio" in welcome_text
    assert "6 blocos" in welcome_skill_text
    assert "Contexto de Negócio" in welcome_skill_text
    assert "6 blocos" in features_text
    assert "{industry, companies, competitors}" in features_text
