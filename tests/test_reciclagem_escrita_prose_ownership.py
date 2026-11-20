#!/usr/bin/env python3
"""Regressão: quem revisa prosa no pacote Exocórtex.

A fixture `tests/fixtures/editorial/reciclagem-escrita.md` carrega os casos
sintéticos e o contrato verificável. Estes testes falham enquanto:

- `excrtx-quality-antislop` mantiver proibição mecânica absoluta (cortar todos
  os advérbios, voz ativa sempre, nenhum travessão) no corpo, no frontmatter,
  na calibração ou nas regras compiladas;
- `excrtx-quality-antislop` não declarar a preservação de autoria, citação
  literal, grau de certeza, quem agiu e ficção didática;
- `excrtx-quality-gate` carregar regra própria de reescrita de prosa ou
  exemplo que introduz dado ausente da fonte;
- o seed versionado mantiver, fora do bloco compilado, regra fixa que
  contradiz a correção.
"""

import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "editorial" / "reciclagem-escrita.md"
ANTISLOP = REPO_ROOT / "skills" / "excrtx-quality-antislop" / "SKILL.md"
GATE = REPO_ROOT / "skills" / "excrtx-quality-gate" / "SKILL.md"
SEED = REPO_ROOT / "SOUL_SEED.md"

START_MARKER = "<!-- COMPILED_RULES_START -->"
END_MARKER = "<!-- COMPILED_RULES_END -->"


def load_contract() -> dict:
    text = FIXTURE.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)
    assert blocks, f"fixture sem bloco yaml: {FIXTURE}"
    return yaml.safe_load(blocks[-1])


def split_skill(path: Path) -> tuple[dict, str]:
    """Devolve (frontmatter, corpo) de um SKILL.md."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?\n)---\n(.*)$", text, re.DOTALL)
    assert match, f"frontmatter ausente em {path}"
    return yaml.safe_load(match.group(1)), match.group(2)


def compiled_rules(frontmatter: dict) -> str:
    return frontmatter.get("compiled_rules") or ""


def calibration_text(frontmatter: dict) -> str:
    hermes = (frontmatter.get("metadata") or {}).get("hermes") or {}
    return yaml.safe_dump(hermes.get("calibration") or [], allow_unicode=True)


def normalise(text: str) -> str:
    """Prosa em markdown, comparável por substring.

    Colapsa quebras de linha e remove ênfase (`**`, `` ` ``) para que um
    requisito como "mechanical signal" case mesmo escrito em negrito ou
    partido pelo limite de coluna. Não afrouxa o contrato: a frase ainda
    precisa existir, na ordem, no corpo da skill.
    """
    stripped = re.sub(r"[*`_]", "", text)
    return " ".join(stripped.split()).lower()


CONTRACT = load_contract()


class FixtureContractTest(unittest.TestCase):
    def test_every_case_declares_criterion_and_evidence(self):
        casos = CONTRACT["casos"]
        self.assertGreaterEqual(len(casos), 6)
        for caso in casos:
            for field in ("id", "criterio", "evidencia"):
                self.assertTrue(
                    str(caso.get(field, "")).strip(),
                    msg=f"caso {caso.get('id')} sem {field}",
                )


class AntiSlopOwnsStyleReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontmatter, cls.body = split_skill(ANTISLOP)
        cls.full = ANTISLOP.read_text(encoding="utf-8")

    def test_no_absolute_mechanical_prohibition_anywhere(self):
        for banned in CONTRACT["absolutos_proibidos_antislop"]:
            self.assertNotIn(
                banned.lower(),
                self.full.lower(),
                msg=f"proibição mecânica absoluta ainda presente: {banned!r}",
            )

    def test_declares_preservation_guarantees(self):
        body_lower = self.body.lower()
        for required in CONTRACT["garantias_antislop"]:
            self.assertIn(
                required.lower(),
                body_lower,
                msg=f"garantia de preservação ausente do corpo: {required!r}",
            )

    def test_admits_didactic_fiction(self):
        body_lower = self.body.lower()
        for required in CONTRACT["ficcao_antislop"]:
            self.assertIn(
                required.lower(),
                body_lower,
                msg=f"ficção didática não admitida: {required!r}",
            )

    def test_calibration_has_no_absolute_rule(self):
        calibration = calibration_text(self.frontmatter).lower()
        self.assertTrue(calibration.strip(), msg="calibração ausente")
        for banned in CONTRACT["absolutos_proibidos_antislop"]:
            self.assertNotIn(
                banned.lower(),
                calibration,
                msg=f"calibração ainda carrega regra absoluta: {banned!r}",
            )

    def test_compiled_rules_preserve_source_meaning(self):
        rules = compiled_rules(self.frontmatter)
        self.assertTrue(rules.strip(), msg="compiled_rules vazio")
        rules_lower = rules.lower()
        for banned in CONTRACT["absolutos_proibidos_antislop"]:
            self.assertNotIn(banned.lower(), rules_lower, msg=f"regra compilada absoluta: {banned!r}")
        for required in ("certainty", "quote", "actor", "35/50"):
            self.assertIn(
                required,
                rules_lower,
                msg=f"regra compilada não preserva {required!r}",
            )


class QualityGateOnlyRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontmatter, cls.body = split_skill(GATE)
        cls.full = GATE.read_text(encoding="utf-8")

    def test_keeps_routing_surface(self):
        for required in CONTRACT["roteamento_gate"]:
            self.assertIn(
                required.lower(),
                self.full.lower(),
                msg=f"gate perdeu o roteamento de {required!r}",
            )

    def test_carries_no_prose_rewrite_rule(self):
        for banned in CONTRACT["proibidos_gate"]:
            self.assertNotIn(
                banned.lower(),
                self.full.lower(),
                msg=f"gate ainda reescreve prosa: {banned!r}",
            )

    def test_examples_do_not_fabricate_data(self):
        allowed = set(CONTRACT["numeros_admitidos_gate"])
        found = set(re.findall(r"\d+", self.body))
        fabricated = sorted(found - allowed)
        self.assertEqual(
            fabricated,
            [],
            msg=f"gate introduz número não fornecido pela fonte: {fabricated}",
        )

    def test_calibration_does_not_fabricate_data(self):
        """m2: a calibração é onde o gate antigo descrevia resultado de estilo."""
        allowed = set(CONTRACT["numeros_admitidos_calibracao_gate"])
        found = set(re.findall(r"\d+", calibration_text(self.frontmatter)))
        fabricated = sorted(found - allowed)
        self.assertEqual(
            fabricated,
            [],
            msg=f"calibração do gate introduz número não justificado: {fabricated}",
        )

    def test_compiled_rules_delegate_prose_to_antislop(self):
        rules = compiled_rules(self.frontmatter).lower()
        self.assertIn("excrtx-quality-antislop", rules)
        self.assertIn("excrtx-quality-taste", rules)
        self.assertTrue(
            "routes" in rules or "roteia" in rules,
            msg="compiled_rules do gate não declara que ele apenas roteia",
        )
        for banned in ("adverb", "passive"):
            self.assertNotIn(banned, rules, msg=f"gate compila regra de prosa: {banned!r}")


class ValidatorConflictTest(unittest.TestCase):
    """I1: o score do harness é sinal mecânico, não juízo de fidelidade.

    Falha enquanto o gate alegar que `validate_artifact_manifest.py` rejeita
    "prose below the floor" (o harness penaliza justamente o que a skill de
    estilo manda preservar) ou enquanto o comportamento seguro diante de uma
    reprovação de prosa fiel não estiver escrito: manter rascunho, citar o
    trecho, não adulterar o texto, não ignorar o exit code.
    """

    @classmethod
    def setUpClass(cls):
        cls.gate_frontmatter, cls.gate_body = split_skill(GATE)
        cls.gate_norm = normalise(cls.gate_body)
        cls.antislop_frontmatter, cls.antislop_body = split_skill(ANTISLOP)
        cls.antislop_norm = normalise(cls.antislop_body)

    def test_gate_distinguishes_mechanical_signal_from_fidelity(self):
        for required in CONTRACT["conflito_validador_gate"]:
            self.assertIn(
                normalise(required),
                self.gate_norm,
                msg=f"gate não resolve o conflito do validador: {required!r}",
            )

    def test_antislop_denies_score_as_licence_to_edit_faithful_text(self):
        for required in CONTRACT["conflito_validador_antislop"]:
            self.assertIn(
                normalise(required),
                self.antislop_norm,
                msg=f"anti-slop não nega licença de edição por score: {required!r}",
            )

    def test_safe_behaviour_keeps_draft_and_preserves_text(self):
        """O comportamento seguro aparece junto, não espalhado em negações soltas."""
        self.assertRegex(
            self.gate_norm,
            r"keep the artifact as draft.{0,600}?quote the flagged excerpt",
            msg="gate não descreve, em sequência, manter rascunho e citar o trecho",
        )
        self.assertRegex(
            self.gate_norm,
            r"never rewrite faithful prose to raise the score.{0,400}?never ignore the exit code",
            msg="gate não proíbe, junto, adulterar o texto e ignorar o exit code",
        )

    def test_fidelity_conflict_reaches_executive_before_retry(self):
        # Read each decision where an executor makes it, not across the file.
        validation, retry = self.gate_body.split("### 4. Artifact validation", 1)[1].split("### 5. Correction by Executor", 1)
        retry = retry.split("### 6.", 1)[0]
        self.assertRegex(normalise(validation), r"return the conflict to the executive")
        self.assertRegex(normalise(validation), r"draft.{0,160}warn")
        self.assertIn("correctable", retry.lower())
        pitfalls = normalise(self.gate_body.split("## Pitfalls", 1)[1].split("## Verification", 1)[0])
        self.assertNotIn("never expose gate scores or diagnoses to the executive", pitfalls)
        rules = normalise(compiled_rules(self.gate_frontmatter))
        self.assertRegex(rules, r"draft.{0,150}executive")

    def test_gate_states_the_harness_measures_density(self):
        self.assertIn(
            "density",
            self.gate_norm,
            msg="gate não diz que o harness mede densidade",
        )
        self.assertNotIn(
            "rejecting prose below the floor",
            self.gate_norm,
            msg="gate ainda alega coerência inexistente com o harness",
        )

    def test_gate_names_the_script_path_not_just_the_filename(self):
        """Achado 5 do judge: o validador aparecia só pelo nome."""
        self.assertIn(
            normalise(CONTRACT["caminho_validador"]),
            self.gate_norm,
            msg="gate não dá o caminho do validador",
        )
        self.assertTrue(
            (REPO_ROOT / CONTRACT["caminho_validador"]).is_file(),
            msg="caminho do validador declarado na fixture não existe no repo",
        )


class GateRoutesVisualWithoutOwningItTest(unittest.TestCase):
    """Achados 1 e 4 do judge: o gate deixou de reescrever prosa mas seguia
    corrigindo layout. Falha enquanto o gate carregar instrução de grid, fonte
    ou escolha de sub-skill visual, ou enquanto pedir escore de prosa para
    diagnosticar falha exclusivamente visual.
    """

    @classmethod
    def setUpClass(cls):
        cls.frontmatter, cls.body = split_skill(GATE)
        cls.full_norm = normalise(GATE.read_text(encoding="utf-8"))
        cls.body_norm = normalise(cls.body)

    def test_carries_no_visual_correction_rule(self):
        for banned in CONTRACT["proibidos_visuais_gate"]:
            self.assertNotIn(
                normalise(banned),
                self.full_norm,
                msg=f"gate ainda corrige visual em vez de rotear: {banned!r}",
            )

    def test_still_routes_visual_to_its_owner(self):
        for required in CONTRACT["roteamento_visual_gate"]:
            self.assertIn(
                normalise(required),
                self.body_norm,
                msg=f"gate perdeu o roteamento visual: {required!r}",
            )

    def test_diagnosis_follows_the_failing_domain(self):
        for required in CONTRACT["diagnostico_por_dominio_gate"]:
            self.assertIn(
                normalise(required),
                self.body_norm,
                msg=f"gate não diagnostica pelo domínio da falha: {required!r}",
            )

    def test_preserved_routes_survive_the_visual_cleanup(self):
        """O piso da prosa, as quatro rotas e o executor continuam no gate."""
        for required in CONTRACT["roteamento_gate"]:
            self.assertIn(
                normalise(required),
                self.full_norm,
                msg=f"limpeza visual derrubou rota preservada: {required!r}",
            )


class InclusiveFloorAndAuthorityTest(unittest.TestCase):
    """Achados 2 e 3 do judge.

    O piso é inclusivo: 35/50 exato passa. Falha enquanto a calibração do gate
    exigir "superar" o piso, enquanto a skill de estilo não disser que 35 passa,
    ou enquanto o gate confundir aprovação de qualidade com autorização do
    executivo para publicar.
    """

    @classmethod
    def setUpClass(cls):
        cls.gate_frontmatter, cls.gate_body = split_skill(GATE)
        cls.gate_body_norm = normalise(cls.gate_body)
        cls.gate_calibration = normalise(calibration_text(cls.gate_frontmatter))
        cls.antislop_frontmatter, cls.antislop_body = split_skill(ANTISLOP)
        cls.antislop_norm = normalise(cls.antislop_body)
        cls.contract = CONTRACT["limite_inclusivo"]

    def test_gate_calibration_does_not_demand_exceeding_the_floor(self):
        for banned in self.contract["proibido_calibracao"]:
            self.assertNotIn(
                normalise(banned),
                self.gate_calibration,
                msg=f"calibração do gate trata o piso como limite exclusivo: {banned!r}",
            )

    def test_gate_calibration_states_the_floor_is_inclusive(self):
        for required in self.contract["exigido_calibracao"]:
            self.assertIn(
                normalise(required),
                self.gate_calibration,
                msg=f"calibração do gate não declara piso inclusivo: {required!r}",
            )

    def test_antislop_states_that_exactly_the_floor_passes(self):
        for required in self.contract["exigido_corpo_antislop"]:
            self.assertIn(
                normalise(required),
                self.antislop_norm,
                msg=f"anti-slop não resolve o limite no piso: {required!r}",
            )

    def test_gate_separates_quality_approval_from_publication_authority(self):
        for required in CONTRACT["autoridade_gate"]:
            self.assertIn(
                normalise(required),
                self.gate_body_norm,
                msg=f"gate confunde aprovação de qualidade com autorização: {required!r}",
            )


class AntiSlopAmbiguityTest(unittest.TestCase):
    """Judge D2/D5 de `excrtx-quality-antislop`.

    D2: a aplicação do piso à cena didática admitia duas leituras.
    D5: duas listas de conferência cobriam as mesmas checagens.
    Economizar não pode custar autoria, citação, gênero ou ficção.
    """

    @classmethod
    def setUpClass(cls):
        cls.frontmatter, cls.body = split_skill(ANTISLOP)
        cls.body_norm = normalise(cls.body)
        cls.checklist = CONTRACT["checklist_unico_antislop"]

    def test_floor_on_a_didactic_scene_has_one_reading(self):
        for required in CONTRACT["piso_na_cena_antislop"]:
            self.assertIn(
                normalise(required),
                self.body_norm,
                msg=f"piso na cena didática continua ambíguo: {required!r}",
            )

    def test_single_delivery_checklist(self):
        headings = re.findall(r"^##\s+.*$", self.body, re.MULTILINE)
        self.assertIn(
            self.checklist["cabecalho_unico"],
            headings,
            msg="checklist final de entrega ausente",
        )
        self.assertNotIn(
            self.checklist["removido"],
            headings,
            msg="duas listas de conferência cobrem as mesmas checagens",
        )

    def test_delivery_checklist_distinguishes_intentional_from_accidental_rhythm(self):
        checklist = self.body.split("## Verification", 1)[1]
        rhythm = next(line for line in checklist.splitlines() if "rhythm" in line.lower() or "metronomic" in line.lower())
        self.assertRegex(normalise(rhythm), r"accidental|unintentional")
        self.assertRegex(normalise(rhythm), r"preserve|retain|keep")
        self.assertNotIn("no paragraph runs metronomic", rhythm.lower())

    def test_consolidation_preserves_every_guarantee(self):
        """Economia não pode derrubar autoria, citação, gênero nem ficção."""
        checklist = self.body.split(self.checklist["cabecalho_unico"])[-1]
        checklist_norm = normalise(checklist)
        for required in self.checklist["itens_preservados"]:
            self.assertIn(
                normalise(required),
                checklist_norm,
                msg=f"consolidação perdeu garantia do checklist: {required!r}",
            )

    def test_corrective_actions_survive_the_merge(self):
        """As ações de Quick Checks (restaurar hedge, remover dado) continuam."""
        for action in ("restore the hedge", "remove it", "restore the impersonal"):
            self.assertIn(
                normalise(action),
                self.body_norm,
                msg=f"ação corretiva perdida na consolidação: {action!r}",
            )


class VersionedSeedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SEED.read_text(encoding="utf-8")
        cls.before_block = cls.text.split(START_MARKER)[0]
        cls.block = cls.text.split(START_MARKER)[1].split(END_MARKER)[0]

    def test_fixed_rules_outside_block_do_not_contradict(self):
        for banned in CONTRACT["absolutos_proibidos_seed"]:
            self.assertNotIn(
                banned.lower(),
                self.before_block.lower(),
                msg=f"regra fixa do seed contradiz a correção: {banned!r}",
            )

    def test_compiled_block_matches_skill_sources(self):
        antislop_rules = compiled_rules(split_skill(ANTISLOP)[0])
        gate_rules = compiled_rules(split_skill(GATE)[0])
        block = " ".join(self.block.split())
        for rules, name in ((antislop_rules, "antislop"), (gate_rules, "gate")):
            for line in [l for l in rules.splitlines() if l.strip()]:
                self.assertIn(
                    " ".join(line.split()),
                    block,
                    msg=f"bloco compilado do seed desatualizado para {name}",
                )

    def test_voice_preference_is_scoped_not_absolute(self):
        """m1: a linha de voz chega ao perfil como preferência, com escopo escrito."""
        contract = CONTRACT["escopo_voz_seed"]
        self.assertIn(
            contract["linha_original"],
            self.before_block,
            msg="linha de voz do seed desapareceu em vez de ser escopada",
        )
        for required in contract["exigido"]:
            self.assertIn(
                required.lower(),
                self.before_block.lower(),
                msg=f"escopo da preferência de voz ausente do seed: {required!r}",
            )

    def test_rest_of_the_seed_is_untouched(self):
        for preserved in CONTRACT["escopo_voz_seed"]["preservado"]:
            self.assertIn(
                preserved,
                self.text,
                msg=f"ciclo alterou trecho do seed fora do escopo: {preserved!r}",
            )


if __name__ == "__main__":
    unittest.main()
