# Runtime driver validation for Google Drive integration

## Quando aplicar
Use este procedimento quando um teste, dogfood ou harness da integração Google Drive precisar decidir entre:
- driver ausente
- driver presente mas inválido
- falha de OAuth/API após o driver já estar íntegro

## Regra de precedência de paths
Validar primeiro o runtime real do Hermes. Ordem recomendada:

1. `$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py`
2. `$HERMES_HOME/hermes-agent/skills/productivity/google-workspace/scripts/google_api.py`
3. cópias locais do repo, apenas como artefatos de desenvolvimento

Racional: o contrato operacional do usuário roda sobre o driver do runtime Hermes. Se o probe passa numa cópia local e falha no runtime, o PASS é falso.

## Heurística mínima do probe
1. Resolver `$HERMES_HOME`; fallback: `~/.hermes`.
2. Construir a lista ordenada de candidatos.
3. Registrar todos os `driver_candidates` para evidência.
4. Selecionar o primeiro candidato existente.
5. Rodar validação sintática (`py_compile` ou equivalente) nesse arquivo.
6. Só depois seguir para OAuth e chamadas de API.

## Classificação recomendada
- Nenhum candidato existe → `driver_found=false` / diagnóstico: driver ausente.
- Candidato existe e falha em `py_compile` → `driver_found=true` / diagnóstico: driver runtime inválido.
- `py_compile` passa e OAuth falha → problema de autenticação/configuração.
- `py_compile` passa, OAuth passa e API falha → problema de permissão, query ou uso da API.

## Evidência que deve ser preservada
- `driver_candidates`
- `driver_path`
- `driver_found`
- `py_compile_exit`
- stderr completo do `py_compile`

## Caso real capturado
Sessão de correção da issue #44 em `elderbernardi/exocortex.saas`:
- o probe corrigido passou a localizar `~/.hermes/skills/productivity/google-workspace/scripts/google_api.py`
- o status correto deixou de ser "driver ausente"
- a falha real passou a aparecer como `SyntaxError` no driver runtime antes de qualquer OAuth

## Testes de regressão úteis
- encontra driver principal via `HERMES_HOME`
- prioriza runtime Hermes sobre cópia local do repo
- aceita fallback `hermes-agent/...`
- serializa paths fora do repo sem quebrar a evidência
