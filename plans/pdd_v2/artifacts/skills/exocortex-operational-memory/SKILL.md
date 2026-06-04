---
name: exocortex-operational-memory
description: Governar, implantar e auditar providers de memória operacional do agente no Exocórtex/Hermes sem substituir o Acervo Cognitivo.
version: 1.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, hermes, memory, hindsight, operational-memory, acervo, setup, governance]
    category: exocortex
    related_skills: [acervo-manager, hermes-agent]
---

# Exocórtex Operational Memory

Use esta skill quando o usuário pedir para avaliar, implantar, configurar, comparar ou auditar providers de memória operacional do agente no Hermes/Exocórtex, como Hindsight, Holographic, Honcho, Mem0, Supermemory, RetainDB, ByteRover ou OpenViking.

## Princípio

Memória operacional auxilia a operação do agente. Ela não substitui o harness primário do Exocórtex.

```text
Provider observa e recupera.
Exocórtex interpreta.
Acervo canoniza.
Skills proceduralizam.
Built-in memory guarda invariantes.
Session Search preserva histórico literal.
```

## Precedência

Em caso de conflito, aplicar esta ordem:

1. SOUL / instruções de sistema.
2. Contratos do Acervo com `operational_mode: blocking`.
3. Skills carregadas e workflows canônicos.
4. Built-in memory para invariantes compactos.
5. Acervo Cognitivo v2 para conhecimento, decisões e processos canônicos.
6. Session Search para histórico literal.
7. Provider de memória operacional para observações semânticas.

Nunca trate uma observação recuperada por provider como decisão canônica.

## Avaliação de suitability

Ao comparar providers, avalie:

- maturidade do plugin;
- modo local, self-hosted ou cloud;
- auto-recall e auto-retain;
- capacidade de consolidar observações;
- risco de sobrecarga de contexto;
- auditabilidade;
- reversibilidade;
- aderência ao Acervo;
- custo/latência;
- risco de criar fonte de verdade paralela.

## Padrão de adoção

Para provider maduro em produção:

1. Criar contrato no microverso de setup.
2. Criar workflow operacional.
3. Criar templates de configuração.
4. Atualizar workflow de setup replicável.
5. Atualizar `index.md` e `log.md` do microverso.
6. Atualizar `~/.hermes/setup.sh` com ativação explícita e idempotente.
7. Validar sem ativar por default.
8. Ativar só após configurar credenciais/backend.
9. Auditar em 7 e 14 dias.

## Padrão de `setup.sh`

Integrações de memória operacional devem ser opcionais e guardadas por flag:

```bash
EXOCORTEX_ENABLE_<PROVIDER>=1 bash ~/.hermes/setup.sh
```

O script deve:

- preservar configs existentes;
- copiar template só quando config não existir;
- não sobrescrever credenciais;
- não ativar provider se o config contém `CHANGE_ME`;
- não falhar o setup inteiro se o provider não estiver pronto;
- deixar claro o próximo passo.

## Hindsight

### Padrão operacional validado (Exocórtex)

Quando a prioridade for simplicidade de setup com persistência local:

1. Rodar Hindsight em container Docker dedicado (single-container), separado do processo Hermes.
2. Manter diretório próprio do Hindsight (ex.: `~/.hermes/hindsight-local/`) com:
   - `docker-compose.yml`
   - `.env`
   - `data/` persistente.
3. Executar essa etapa **antes** da ativação/configuração do provider de memória no setup.
4. Tratar reset de memória como ação destrutiva com confirmação explícita por parâmetros.

Flags recomendadas para reset seguro:

- `EXOCORTEX_HINDSIGHT_RESET_DATA=1`
- `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`

Sem ambas as flags, a memória deve ser preservada.

Referência operacional: `references/hindsight-single-container-setup.md`.

Padrão de estado após ativação do Hindsight no Hermes:

- `memory.provider=hindsight`
- `memory.memory_enabled=false`
- `memory.user_profile_enabled=false`

Padrão de escopo para este setup:

- Um Hindsight por instância Hermes.
- Perfis `exec` e `evol` compartilham o mesmo bank (`bank_id_template: exocortex`).

Preferência inicial para o Exocórtex:

```json
{
  "memory_mode": "hybrid",
  "auto_recall": true,
  "auto_retain": true,
  "retain_async": true,
  "retain_every_n_turns": 2,
  "recall_budget": "low",
  "recall_prefetch_method": "recall",
  "recall_types": "observation",
  "recall_max_tokens": 1200,
  "recall_max_input_chars": 800
}
```

`local_embedded` significa que o serviço/banco Hindsight roda localmente. O backend LLM pode ser local real, self-hosted ou API externa. Explique essa distinção para não criar a falsa exigência de rodar um modelo completo no mesmo host.

### Pitfall crítico (Hermes + plugin Hindsight)

No estado atual de integração do Hermes, o provider `hindsight` pode exigir `HINDSIGHT_API_KEY` para ficar `available` em `hermes memory status`, mesmo quando `mode=local_embedded`.

Implicação prática:
- `local_embedded` NÃO implica operação "sem chave da plataforma".
- Sem `HINDSIGHT_API_KEY`, o provider pode permanecer `not available`.

Diagnóstico obrigatório antes de concluir setup:
1. Rodar `hermes memory status`.
2. Se houver `Missing: HINDSIGHT_API_KEY`, tratar como bloqueio de ativação do provider.
3. Decidir explicitamente:
   - manter Hindsight e provisionar a chave exigida, ou
   - migrar para provider local-first alternativo (ex.: holographic/honcho/mem0 local) quando o requisito de cloud-key for inaceitável.

Regra de comunicação para o usuário:
- Não dizer "basta backend LLM".
- Sempre separar três camadas: storage local, backend LLM, autenticação exigida pelo plugin.

## Holographic

Use como alternativa local-first e auditável quando soberania, SQLite e controle explícito forem mais importantes que auto-organização. Comece com `auto_extract: false` e use fatos explícitos até haver evidência de qualidade.

## Promoção para memória canônica

Use este funil:

```text
provider observation
→ validação contra contexto atual
→ candidato
→ Acervo decision/contract/workflow/reflection
→ skill, se procedural
→ built-in memory, se invariante compacto
```

## Referências

- `references/operational-memory-provider-integration.md` — padrão detalhado de integração e checklist de repetibilidade.
- `references/hindsight-local-embedded-key-requirement.md` — distinção operacional entre storage local, backend LLM e autenticação exigida pelo plugin Hermes.

## Pitfalls

- Não apontar provider de memória para substituir Acervo.
- Não ativar auto-recall amplo em produção sem período de auditoria.
- Não iniciar com recall de fatos brutos se o provider oferece observações consolidadas.
- Não transformar erro de setup em regra permanente contra o provider.
- Não registrar segredos, credenciais ou rascunhos não aprovados como memória operacional.
