#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOUL_SEED = ROOT / "SOUL_SEED.md"
DRAFTFIRST_SKILL = ROOT / "skills" / "excrtx-govern-draftfirst" / "SKILL.md"
TOOLS_SKILL = ROOT / "skills" / "excrtx-govern-tools" / "SKILL.md"


class HarnessDraftFirstPolicyTest(unittest.TestCase):
    def test_soul_seed_distinguishes_self_delivery_from_external_communication(self):
        content = SOUL_SEED.read_text(encoding="utf-8")
        self.assertIn("Self-delivery operacional", content)
        self.assertIn("Comunicação em nome do executivo", content)
        self.assertIn("Publicação/compartilhamento externo", content)
        self.assertIn("Enviar emails ou mensagens para terceiros", content)
        self.assertIn("Self-delivery operacional pode executar sem DRAFT", content)
        self.assertIn("Na dúvida entre self-delivery e comunicação externa, tratar como comunicação externa", content)

    def test_draftfirst_skill_defines_category_regimes(self):
        content = DRAFTFIRST_SKILL.read_text(encoding="utf-8")
        self.assertIn("## Taxonomia obrigatória", content)
        self.assertIn("### 4. Regime por categoria", content)
        self.assertIn("**Self-delivery operacional**", content)
        self.assertIn("**Comunicação em nome do executivo**", content)
        self.assertIn("**Publicação/compartilhamento externo**", content)
        self.assertIn("Pode executar sem DRAFT quando o destinatário é inequivocamente o próprio executivo", content)
        self.assertIn("Destinatário ambíguo ou canal compartilhado deve ser tratado como comunicação externa", content)

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
