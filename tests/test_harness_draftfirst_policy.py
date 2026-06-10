#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOUL_SEED = ROOT / "SOUL_SEED.md"
DRAFTFIRST_SKILL = ROOT / "skills" / "excrtx-govern-draftfirst" / "SKILL.md"
TOOLS_SKILL = ROOT / "skills" / "excrtx-govern-tools" / "SKILL.md"


class HarnessDraftFirstPolicyTest(unittest.TestCase):
    def test_soul_seed_distinguishes_internal_from_external_actions(self):
        content = SOUL_SEED.read_text(encoding="utf-8")
        self.assertIn("Taxonomia de ações: internas vs externas", content)
        self.assertIn("Ações internas (execução direta, sem DRAFT)", content)
        self.assertIn("Ações externas (DRAFT obrigatório)", content)
        self.assertIn("git commit (local)", content)
        self.assertIn("git push para remote", content)
        self.assertIn("Override do executivo", content)

    def test_soul_seed_distinguishes_self_delivery_from_external_communication(self):
        content = SOUL_SEED.read_text(encoding="utf-8")
        self.assertIn("Self-delivery operacional", content)
        self.assertIn("Comunicação em nome do executivo", content)
        self.assertIn("Publicação/compartilhamento externo", content)
        self.assertIn("Enviar emails ou mensagens para terceiros", content)
        self.assertIn("Self-delivery operacional pode executar sem DRAFT", content)
        self.assertIn("Na dúvida entre self-delivery e comunicação externa, tratar como comunicação externa", content)

    def test_draftfirst_skill_defines_internal_vs_external_actions(self):
        content = DRAFTFIRST_SKILL.read_text(encoding="utf-8")
        self.assertIn("## Taxonomia de Ações: Internas vs Externas", content)
        self.assertIn("### Ações internas (execução direta)", content)
        self.assertIn("### Ações externas (DRAFT obrigatório)", content)
        self.assertIn("git commit", content)
        self.assertIn("git push", content)
        self.assertIn("Execução direta", content)
        self.assertIn("Draft-First obrigatório", content)

    def test_draftfirst_skill_defines_category_regimes(self):
        content = DRAFTFIRST_SKILL.read_text(encoding="utf-8")
        self.assertIn("## Taxonomia de Canais", content)
        self.assertIn("### 4. Regime por categoria", content)
        self.assertIn("**Self-delivery operacional**", content)
        self.assertIn("**Comunicação em nome do executivo**", content)
        self.assertIn("**Publicação/compartilhamento externo**", content)
        self.assertIn("Pode executar sem DRAFT quando o destinatário é inequivocamente o próprio executivo", content)
        self.assertIn("Destinatário ambíguo ou canal compartilhado deve ser tratado como comunicação externa", content)

    def test_draftfirst_skill_has_executive_override(self):
        content = DRAFTFIRST_SKILL.read_text(encoding="utf-8")
        self.assertIn("O executivo pode forçar DRAFT em ação interna", content)
        self.assertIn("O executivo pode autorizar ação externa sem DRAFT", content)
        self.assertIn("quero revisar antes", content)
        self.assertIn("confio, execute direto", content)

    def test_tool_governance_skill_classifies_internal_actions(self):
        content = TOOLS_SKILL.read_text(encoding="utf-8")
        self.assertIn("**Ações internas (git/tests)**", content)
        self.assertIn("Execução direta. Sem DRAFT", content)
        self.assertIn("**Ações externas (git push/deploy)**", content)
        self.assertIn("git push, deploy scripts", content)

    def test_tool_governance_skill_separates_self_delivery_and_third_party_communication(self):
        content = TOOLS_SKILL.read_text(encoding="utf-8")
        self.assertIn("**Entrega ao executivo**", content)
        self.assertIn("**Comunicação para terceiros**", content)
        self.assertIn("### R3: Governança de entrega e comunicação", content)
        self.assertIn("Política: pode executar sem DRAFT", content)
        self.assertIn("Política: Draft-First obrigatório", content)
        self.assertIn("Na dúvida sobre destinatário, canal ou efeito social, tratar como comunicação para terceiros.", content)
        self.assertIn("Envio direto de email/mensagem para terceiros sem aprovação pós-DRAFT", content)


if __name__ == "__main__":
    unittest.main()
