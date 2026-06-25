# Prompt de Inicialização — Inteligência Competitiva (META #97)

> **Para:** Agentes do Exocórtex · Nova sessão de execução
> **Contexto:** Fase 4 da arquitetura de pesquisa setorial — fontes públicas estruturadas
> **Plano canônico:** `docs/plans/2026-06-25_inteligencia-competitiva-fase4-10.md`
> **Repo:** `/home/elder/projetos/projetob/exocortex.saas/`

---

## Antes de começar

1. Leia este prompt.
2. Leia o plano canônico completo: `docs/plans/2026-06-25_inteligencia-competitiva-fase4-10.md`.
3. Leia a issue que você vai executar com `gh issue view <n>`. As issues #111–#113 já existem.
4. Inspecione o estado local antes de editar:
   - `git status --short`
   - `python3 --version`
   - arquivos já existentes da issue no repo
5. Trabalhe localmente. **Não faça `git push`, comentário em issue, edição remota ou deploy sem aprovação explícita.**
6. Ao terminar, prepare um DRAFT local de atualização da issue com evidências de teste; só publique se o executivo aprovar.

---

## Contrato de continuidade

Este prompt existe para evitar retrabalho entre agentes.

Regras:
- Se a issue já tiver artefatos locais em andamento, **continue e corrija**; não recrie do zero.
- Se a issue tiver divergência entre corpo do GitHub e plano canônico, **o plano canônico vence**.
- Se a issue usar convenções legadas, normalize para as convenções já adotadas no repo.

Exemplos de normalização obrigatória:
- CLI canônica: `python3 -m tools.excrtx_source_{nome}.cli ...`
- Timestamp canônico: `retrieved_at`
- Envelope canônico: `source`, `query`, `retrieved_at`, `data`, `provenance`, `errors`

---

## O que está acontecendo

A META #97 saiu das Fases 1–3:

| Fase | Issue | Estado |
|---|---:|---|
| Agent-Reach | #108 | concluída |
| Crawler BR | #98 | concluída |
| Skill-wrapper CPG | #99 | concluída |
| Firecrawl local/MCP | #9 | concluída como capacidade opcional |

Agora entramos na **Fase 4 — Fontes Públicas Estruturadas**. O objetivo é capturar sinais que a imprensa não cobre: cadastro corporativo, busca do consumidor e reputação pública.

### Estado verificado localmente neste repo

| Issue | Componente | Estado local |
|---|---|---|
| #113 | `excrtx-source-cnpj` | em andamento local: tool + testes + skill já existem |
| #112 | `excrtx-source-google-trends` | não iniciado |
| #111 | `excrtx-source-reclameaqui` | não iniciado |

Se o estado local e o plano divergirem, atualize o plano antes de abrir nova frente de implementação.

---

## Ordem operacional recomendada

A prioridade de negócio das três issues é P0. A ordem abaixo reduz risco técnico e cria padrão reutilizável para os próximos coletores:

### 1. #113 — `excrtx-source-cnpj`
Coletor de dados cadastrais via BrasilAPI/ReceitaWS. É o menor risco: API pública, fixture simples, bom primeiro caso para padronizar envelope JSON, CLI e skill wrapper.

### 2. #112 — `excrtx-source-google-trends`
Coletor de tendências de busca via `pytrends`. Entrega séries temporais, distribuição geográfica e queries relacionadas. Requer tratamento explícito de rate limit, mocks offline e governança de dependência antes de instalar qualquer pacote.

### 3. #111 — `excrtx-source-reclameaqui`
Coletor de reputação via Reclame Aqui. Tem maior impacto de consumidor, mas maior fragilidade de scraping. Comece por HTTP/HTML parsing; use browser/Firecrawl só se a página realmente depender de JavaScript.

> Se houver só um agente, comece por #113. Se #113 já estiver adiantada localmente, finalize, revise e só então abra #112 ou #111.

---

## Contrato comum dos coletores

### Estrutura de arquivos

```text
tools/excrtx_source_{nome}/
├── __init__.py
├── cli.py
├── collector.py
└── schemas.py

skills/excrtx-source-{nome}/
└── SKILL.md

tests/test_source_{nome}.py
```

### CLI canônica

```bash
python3 -m tools.excrtx_source_{nome}.cli "input" --output json
```

### Envelope JSON canônico

Use `retrieved_at` como timestamp padrão para alinhar com `excrtx_crawler_brasil` e `excrtx-integrate-agent-reach`.

```json
{
  "source": "reclameaqui|google_trends|cnpj",
  "query": "input original",
  "retrieved_at": "2026-06-25T12:00:00Z",
  "data": {},
  "provenance": {
    "url": "https://...",
    "method": "api|html|browser|firecrawl",
    "raw_cached": false
  },
  "errors": []
}
```

### Convenções de compatibilidade

Se o corpo da issue ou rascunhos antigos mencionarem:
- `coletado_em` → normalize para `retrieved_at`
- `python -m excrtx_source_cnpj` → normalize para `python3 -m tools.excrtx_source_cnpj.cli`
- schema sem envelope → embrulhe no envelope comum

---

## Regras para todos os coletores

1. Documentação e skill em PT-BR; código, nomes de funções e módulos em inglês.
2. Sem login, sem API key e sem bypass de barreiras de acesso.
3. Unit tests offline primeiro: fixtures HTML/JSON ou mocks de API. Smoke tests reais devem ser marcados como lentos/opcionais.
4. Não rode `pip install`, `npm install` ou equivalente sem aprovação. Se faltar dependência, registre no plano e reporte.
5. Rate limit explícito por domínio/fonte. Falha de rede deve retornar erro estruturado, não stack trace bruto.
6. Skill wrapper com frontmatter Hermes e seções: `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`.
7. A saída deve ser JSON parseável e estável; campos ausentes viram `null` ou listas vazias.
8. Se criar ou alterar skill, valide com `python3 scripts/skill_judge.py --skill <nome> --d1-only`.
9. Se a execução materialmente mudar o plano, atualize `docs/plans/` no mesmo turno.

---

## Definition of Done por issue

- [ ] Ferramenta Python com CLI funcional em `tools/excrtx_source_{nome}/`.
- [ ] Skill `skills/excrtx-source-{nome}/SKILL.md` criada ou atualizada.
- [ ] Testes unitários passando com fixtures/mocks.
- [ ] Smoke test real executado ou registrado como bloqueado por rede/rate limit.
- [ ] Saída validada contra o envelope comum.
- [ ] DRAFT local de comentário para issue preparado com comandos e resultados.
- [ ] Plano/prompt atualizados se houver drift relevante entre intenção e estado real.

---

## Comandos de verificação sugeridos

```bash
cd /home/elder/projetos/projetob/exocortex.saas
python3 -m pytest tests/test_source_{nome}.py -q
python3 -m tools.excrtx_source_{nome}.cli "input de smoke" --output json
python3 scripts/skill_judge.py --skill excrtx-source-{nome} --d1-only
```

Para validar JSON em arquivo temporário:

```bash
python3 -m tools.excrtx_source_{nome}.cli "input" --output json > /tmp/source_{nome}_smoke.json
python3 -m json.tool /tmp/source_{nome}_smoke.json >/dev/null
```

---

## Contexto adicional

- Acervo: `acervo/micro/` — dados estruturados só viram material promocionável para `micro/{empresa}/` depois de curadoria.
- DocBrain: `/home/elder/projetos/projetob/docbrain/` — usado na Fase 5 para PDF/Office; não citar em docs públicos.
- Firecrawl: capacidade opcional para páginas com JavaScript pesado; trate endpoint/configuração como dependência de runtime, não como garantia universal.
- O wrapper `#99 excrtx-research-cpg-brasil` já está concluído; integrações novas devem seguir suas convenções existentes, não criar um segundo padrão.

---

**Comece pela issue escolhida, revise o estado local, execute com output real, corrija o plano se houver drift e entregue o DRAFT de atualização.**
