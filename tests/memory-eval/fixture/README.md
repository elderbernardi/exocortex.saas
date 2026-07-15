# Fixture sintético — avaliação de memória (Phase 6 da spec memory-v2)

Mini-acervo **inteiramente fictício** (executiva Marina Duarte, Atlântico
Logística — nada do acervo real) em schema `acervo/v0.2`, com material
plantado para medir recuperação, contaminação, supersedência, conflito,
staleness, temporalidade e abstenção.

- `acervo/` — 3 microversos (cliente-norte, expansao-sul, operacoes) + shared + global.
- `PLANTED.yaml` — contrato do material plantado: cada armadilha, seus paths e o
  que o harness deve verificar. **Toda extensão do fixture deve atualizar este arquivo.**
- `../golden/questions.yaml` — 25 perguntas-ouro com paths esperados/proibidos.

Regras para estender: arquivos 10–30 linhas, PT-BR, sempre válidos no
`validate_frontmatter.py` (v0.2), conteúdo fictício plausível, e cada novo
material de teste registrado no PLANTED.yaml.
