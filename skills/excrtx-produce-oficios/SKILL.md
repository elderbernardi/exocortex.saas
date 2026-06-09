---
name: excrtx-produce-oficios
description: "Gera ofícios profissionais do gabinete (IFSul Campus Passo Fundo) em DOCX, PDF ou HTML a partir de templates."
version: 1.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, gabinete, documentos, oficio, word, pdf, html]
    category: exocortex
---

# Gerador de Ofícios — Gabinete IFSul

Gera ofícios em DOCX, PDF ou HTML usando templates persistidos no acervo.

## When This Skill Activates

- Executivo pede para gerar/redigir um ofício
- Pedido menciona "ofício", "convite formal", "comunicação oficial"
- Contexto é o gabinete (micro/gabinete)

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
- `localidade`: padrão "Passo Fundo" (preenchido automaticamente)
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

## Quality Gate

Antes de entregar, aplique o Quality Gate Unificado (`excrtx-quality-gate`) como passo final obrigatório:
- A prosa do ofício deve passar pelo gate de anti-slop (`excrtx-quality-antislop`).
- A redação oficial do gabinete deve ser extremamente formal e polida, sem qualquer uso de linguagem neutra, adjetivações vazias, ou palavras de enchimento.
- A conformidade do texto será auditada pelo harness de verificação (`validate_artifact_manifest.py`).

