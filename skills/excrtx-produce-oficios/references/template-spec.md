# Template Markdown Specification — Generator ofícios/documentos

## Frontmatter YAML Schema

Todo template no acervo usa frontmatter com esta estrutura:

```yaml
---
nome: "Nome Descritivo do Template"
versao: 1.0
tipo: oficio | relatorio | ata | memorando
dominio: gabinete | outro-slug
descricao: "Descrição curta do propósito do template."
campos_requeridos:
  - nome: identificador_campo      # usado em placeholders {{identificador_campo}}
    label: "Rótulo legível"        # exibido ao usuário durante entrevista
    tipo: texto | multi-linha | data | numero
    exemplo: "Texto de exemplo"    # ajuda o agente a explicar o campo
    obrigatorio: true | false
    padrao: "valor padrão"         # opcional: usado se não informado
---
```

## Corpo do Template

- Placeholders: `{{nome_campo}}` substituídos literalmente pelos dados
- Placeholders automáticos (sempre disponíveis sem informar):
  - `{{ano_atual}}` — ano corrente via `date.today().year`
  - `{{localidade}}` — padrão "Passo Fundo" (override via dados)
- Formatação Markdown suportada no corpo:
  - `**bold**` → renderizado como bold no DOCX/HTML
  - `# Título` → ignorado no DOCX (título já vem do cabeçalho)
  - Linhas em branco → quebras de parágrafo com espacejamento de 6pt

## Campos Padrão para Ofícios IFSul Passo Fundo

| Campo | Padrão | Observação |
|-------|--------|-----------|
| `nome_signatario` | Lucas Vanini | Override se outro diretor |
| `cargo_signatario` | Diretor Geral | Override se outro cargo |
| `localidade` | Passo Fundo | Manter para campus PF |

## Margens DOCX (padrão ofício brasileiro)

- Superior: 3 cm
- Inferior: 2 cm
- Esquerda: 3 cm
- Direita: 2 cm
- Fonte: Times New Roman 12pt
- Espaçamento: 1,5 linhas
- Alinhamento: justificado
