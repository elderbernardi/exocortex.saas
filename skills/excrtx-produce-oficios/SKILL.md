---
name: excrtx-produce-oficios
description: Generate professional official documents in DOCX, PDF, or Markdown format.
version: 1.0.0
category: excrtx
platforms:
- linux
author: Exocórtex
gate:
  require_quality_gate: true
  max_context_tokens: 2000
metadata:
  hermes:
    tags:
    - exocortex
    - gabinete
    - documentos
    - oficio
    - word
    - pdf
    - html
    related_skills:
    - excrtx-quality-gate
    - excrtx-quality-antislop
    - excrtx-govern-draftfirst
    calibration:
    - feature_id: EX-24
      calibration_prompt: Você gera ofícios profissionais em DOCX, PDF ou HTML. Formatação institucional com cabeçalhos, numeração
        e estilo oficial. Validação de campos obrigatórios antes de gerar. Quality gate anti-slop com formalidade extrema.
      test_prompt: 'Prepare um ofício para o Ministério da Educação solicitando prorrogação do prazo de entrega do relatório
        anual. Remetente: Elder Bernardi, Diretor Executivo.'
      acceptance_criteria: '1. O agente valida campos obrigatórios (destinatário, remetente, assunto, corpo)

        2. O texto usa linguagem formal institucional (sem coloquialismos, sem padrões de IA)

        3. O formato segue estrutura de ofício (cabeçalho, numeração, vocativo, fecho)

        4. Apresenta como DRAFT antes de gerar o documento final'
      remediation_tip: 'FALHA: Ofício sem formato institucional ou com linguagem informal. Um ofício exige: cabeçalho institucional,
        número de referência, vocativo formal, corpo em linguagem oficial, fecho protocolar (''Atenciosamente'' ou ''Respeitosamente''),
        e identificação do signatário com cargo. Use o template DOCX da skill.'
---
# Gerador de Ofícios — Gabinete Institucional

Gera ofícios em DOCX, PDF ou HTML usando templates persistidos no acervo.

## When to Use

- Executivo pede para gerar/redigir um ofício
- Pedido menciona "ofício", "convite formal", "comunicação oficial"
- Contexto é o gabinete (micro/gabinete)

**Don't use for:** Memos, reports, or generic documents (use appropriate template skills). Drafting emails or messages (use `excrtx-govern-draftfirst`). Documents outside institutional context.

## Workflow Interativo

### 1. Identificar campos obrigatórios (NUNCA assumir valores)

Cada template tem campos obrigatórios definidos no frontmatter. **Antes de gerar**, o agente DEVE:

1. Ler o template: `~/.hermes/acervo/micro/gabinete/templates/oficio-generico.md`
2. Extrair `campos_requeridos` do frontmatter YAML
3. Identificar quais campos já foram informados no pedido do executivo
4. **Perguntar sobre TODOS os campos faltantes** em uma única mensagem estruturada
5. Perguntar o **formato de saída**: DOCX, PDF ou HTML

#### Exemplo de pergunta de campos faltantes:

> Para gerar o ofício, preciso de algumas informações:
>
> 1. **Número do Ofício** — ex: 042
> 2. **Data** — ex: 29 de maio de 2026
> 3. **Destinatário** — nome, cargo e órgão
> 4. **Assunto** — linha curta
> 5. **Formato**: DOCX, PDF ou HTML?
>
> Se preferir, me passe o texto completo e eu extraio os campos.

### 2. Validação de campos

- `numero_oficio`: apenas dígitos (ex: 042)
- `data`: formato textual livre em português
- `ano_atual`: sempre o ano corrente (preenchido automaticamente)
- `localidade`: padrão "Localidade Padrão" (preenchido automaticamente)
- Se `nome_signatario` não informado: usar "Lucas Vanini"
- Se `cargo_signatario` não informado: usar "Diretor Geral"

### 3. Geração do documento

Executar o script:

```bash
# DOCX
/tmp/oficio_env/bin/python ~/.hermes/skills/exocortex/excrtx-produce-oficios/scripts/gerar_oficio.py \
  --template ~/.hermes/acervo/micro/gabinete/templates/oficio-generico.md \
  --dados '{"numero_oficio":"042","data":"29 de maio de 2026",...}' \
  --formato docx \
  --output /tmp/oficio_final.zip

# PDF
/tmp/oficio_env/bin/python ~/.hermes/skills/exocortex/excrtx-produce-oficios/scripts/gerar_oficio.py \
  --template ~/.hermes/acervo/micro/gabinete/templates/oficio-generico.md \
  --dados '{...}' \
  --formato pdf \
  --output /tmp/oficio_final.pdf

# HTML
/tmp/oficio_env/bin/python ~/.hermes/skills/exocortex/excrtx-produce-oficios/scripts/gerar_oficio.py \
  --template ~/.hermes/acervo/micro/gabinete/templates/oficio-generico.md \
  --dados '{...}' \
  --formato html \
  --output /tmp/oficio_final.html
```

### 4. Entrega

- DOCX: enviar como ZIP (padrão do Telegram Mobile — ver memória do usuário)
- PDF: enviar direto como anexo
- HTML: enviar como arquivo ou exibir inline se pequeno

**Draft-First:** o ofício gerado é DRAFT. O executivo revisa antes de assinar/imprimir.

## Templates disponíveis

- `oficio-generico.md` — modelo padrão para convites, comunicações e solicitações

Novos templates podem ser adicionados no mesmo diretório. O frontmatter YAML define os campos.
Especificação completa do schema: `references/template-spec.md`

## Pitfalls

- **Nenhum valor assumido** — sempre confirmar campos com o executivo
- **Encoding** — o script usa UTF-8, sem problemas com acentos
- **Venv** — o script roda em `/tmp/oficio_env/` que precisa ter python-docx instalado
  - Se venv não existir ou python-docx faltar: `python -m venv /tmp/oficio_env && /tmp/oficio_env/bin/pip install python-docx`
- **Weasyprint (PDF)** — requer instalação separada; se falhar, sugerir HTML como alternativa
- **Telegram Mobile** — preferir ZIP para DOCX (arquivo único pode corromper)

## Log no acervo

Após gerar um ofício, logar no `micro/gabinete/log.md`:
```
## [YYYY-MM-DD] oficio | OFÍCIO Nº {numero}/{ano} — {assunto resumido}
```

## Verification

- [ ] All mandatory fields from template frontmatter were collected (not assumed)
- [ ] Document generated successfully (script exit code 0)
- [ ] Output file exists and is non-empty
- [ ] Field validation passed (numero_oficio is digits, data is valid)
- [ ] Draft presented to executive for review before delivery
- [ ] Quality gate check passed (`excrtx-quality-gate`)
- [ ] Anti-slop gate passed (no filler language, extreme formality)
- [ ] Log entry appended to `micro/gabinete/log.md`

## Procedure

Follow the Workflow Interativo (steps 1-4) defined above.
