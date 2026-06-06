# Dogfood conversacional — EX-18 a EX-21 Quality Gates

Data: 2026-06-06
Repo: /home/elder/projetos/projetob/exocortex.saas
Escopo: Anti-Slop Textual, Anti-Slop Visual/Taste, Design System, Quality Gate Unificado

## Evidência técnica executada

Comando estrutural:

```bash
python3 - <<'PY'
# valida SKILL.md, frontmatter e marcadores semânticos EX-18..EX-21
PY
```

Resultado relevante:
- EX-18: skill/frontmatter/min_score_35/quick_checks PASS.
- EX-19: skill/frontmatter/gpt-taste/brandkit/brutalist/designsys integration PASS.
- EX-20: skill/frontmatter/RESOLVE/LINT/EXPORT PASS; CREATE FAIL; UPDATE FAIL; expected acervo/global/DESIGN.md FAIL; acervo/global/_meta/DESIGN.md PASS.
- EX-21: skill/frontmatter/classificação prosa/visual/técnico e executor/NUNCA PASS; check literal minúsculo para respostas curtas FAIL por case-string, conteúdo existe na skill.

Comando lint real:

```bash
npx -y @google/design.md lint acervo/global/_meta/DESIGN.md
```

Resultado: exit_code 0; errors 0; warnings 1 (`colors.danger` definido mas não referenciado); infos 1.

## EX-18 — Anti-Slop Textual

Usuário: "Reescreve esse parágrafo para mandar ao conselho: 'Vamos explorar essa ideia fascinante que é extremamente importante para o futuro da empresa. É importante notar que a decisão foi tomada de forma cuidadosa e será implementada rapidamente.'"

Exocórtex: "O conselho aprovou a decisão. A operação começa nesta semana, com dono definido, prazo curto e critério de sucesso mensurável. O risco principal é execução lenta; a mitigação é revisar avanço toda sexta-feira até a entrega."

Auditoria curta: PASS. Removeu throat-clearing, advérbios, passiva e generalidades. Voz ativa e atores explícitos. Evidência: SKILL.md EX-18 contém score mínimo 35/50 e quick checks; validação estrutural retornou PASS.

Defeitos candidatos: sem defeito candidato funcional no dogfood; a feature é normativa e não tem ferramenta automática de scoring.

## EX-19 — Anti-Slop Visual / Taste

Usuário: "Me dá uma direção visual para uma landing de um produto de IA para CFOs. Não quero cara de template SaaS genérico."

Exocórtex: "Use landing com tensão editorial, não template SaaS.

Direção:
- Hero: uma frase de 2 linhas, fundo claro, bloco de métrica real à direita.
- Estrutura: AIDA em 5 blocos, com bento grid denso na prova de valor.
- Visual: Inter/JetBrains Mono, cards secos, borda fina, alto contraste, sem ilustrações 3D.
- Movimento: entrada curta para métrica e CTA; nada que pareça demo de portfólio.
- Copy dos botões: `Ver impacto no caixa` e `Abrir simulação`.

Cortes obrigatórios: nada de `SECTION 01`, grid com buracos, headline de 4 linhas ou alternância repetida texto/imagem."

Auditoria curta: PASS. Roteou para gpt-taste por landing/UI; aplicou pre-flight contra meta-label, heading longo, grid vazio, repetição e contraste. Evidência: EX-19 referencia gpt-taste, brandkit, brutalist e integração com designsys; validação estrutural retornou PASS.

Defeitos candidatos: sub-skills aparecem referenciados no SKILL.md; o teste estrutural aceita referência textual, não comprova existência de arquivos separados `gpt-taste.md`, `brandkit.md`, `brutalist.md`.

## EX-20 — Design System

Usuário: "Resolve os tokens visuais globais do Exocórtex para eu usar num card executivo."

Exocórtex: "Tokens resolvidos disponíveis:
- Cores: primary `#1a73e8`, secondary `#34a853`, accent `#fbbc04`, neutral `#f8f9fa`, dark `#202124`, danger `#ea4335`.
- Tipografia: Inter para heading e corpo; JetBrains Mono para dados e labels técnicos.
- Spacing: sm `8px`, md `16px`, lg `24px`, xl `48px`.
- Radius: sm `4px`, md `8px`, lg `16px`.
- Card: background `#FFFFFF`, text `{colors.dark}`, radius `{rounded.md}`, padding `{spacing.lg}`.

Para o card executivo: fundo branco, texto `#202124`, padding `24px`, radius `8px`, heading Inter 1.75rem/600."

Auditoria curta: PARTIAL. Consegui resolver tokens lendo o arquivo real `acervo/global/_meta/DESIGN.md` e lintar com `@google/design.md`: exit 0, 0 erros, 1 warning. Porém a skill documenta `acervo/global/DESIGN.md`, que não existe; o arquivo real está em `global/_meta/DESIGN.md`. Além disso, FEATURES.md exige operações CREATE e UPDATE, mas SKILL.md implementa `Operation: WRITE` em vez de CREATE/UPDATE.

Defeitos candidatos:
- EX20-PATH-MISMATCH: skill aponta `acervo/global/DESIGN.md`; repo usa `acervo/global/_meta/DESIGN.md`.
- EX20-OPS-MISMATCH: contrato cita CREATE/UPDATE; skill só define WRITE.
- EX20-WARNING: token `colors.danger` não referenciado por componente no lint.

## EX-21 — Quality Gate Unificado

Usuário: "Me entrega duas coisas: um resumo executivo do plano e um JSON com os mesmos campos para eu integrar no pipeline."

Exocórtex: "Resumo executivo:
O plano reduz risco operacional ao separar decisão, execução e verificação. O primeiro corte deve atacar os gargalos com impacto financeiro claro; o segundo deve automatizar a medição para evitar discussão por opinião. Dono, prazo e métrica entram antes de qualquer expansão.

JSON:
```json
{
  "objetivo": "reduzir risco operacional",
  "primeiro_corte": "gargalos com impacto financeiro claro",
  "segundo_corte": "automacao da medicao",
  "criterios": ["dono", "prazo", "metrica"]
}
```"

Auditoria curta: PASS. Classificou output misto: prosa passou por antislop; JSON foi tratado como dado técnico e não reescrito. Evidência: SKILL.md EX-21 define roteamento prosa→antislop, visual→taste e bypass para código/doc técnica/dados/respostas curtas/citações; validação estrutural confirmou os principais termos.

Defeitos candidatos: não há executor automático real acoplado no harness; o gate é instrução de comportamento, então o dogfood valida experiência conversacional e contrato documental, não enforcement programático.

## Resultado consolidado

- EX-18: PASS
- EX-19: PASS
- EX-20: PARTIAL
- EX-21: PASS

Status geral: PARTIAL por defeitos candidatos em EX-20.
