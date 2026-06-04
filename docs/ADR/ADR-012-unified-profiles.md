# ADR-012 — Unificação de Profiles (exec+evol → default)

## Status

Aceita (2026-06-04)

## Contexto

Os vetores Execução, Evolução e Manutenção do framework cognitivo Exocórtex (Cap. 3 — docs/exocortex.ia/03_framework.md) foram implementados como profiles Hermes separados (`hermes -p exec`, `hermes -p evol`, `hermes -p manut`).

O framework define que vetores **alternam dentro da mesma sessão**:

> "Na prática, os dois vetores se alternam — muitas vezes dentro da mesma sessão. Você está criando uma aula (Execução) e percebe que não domina um conceito (Evolução). Pausa. Aprende. Volta a criar com mais profundidade."

Profiles Hermes são **instâncias isoladas** com HERMES_HOME, memória, sessão e skills separados. Trocar profile requer reiniciar a sessão e perder contexto.

### Dados medidos

- **Overhead de skills no contexto:** O Hermes injeta apenas um índice leve no system prompt (Layer 7 do prompt assembly). Para 33 skills: ~1.300 tokens. Skills são carregadas sob demanda via `skill_view(name)`.
- **Impacto de 33 vs 15 skills:** Diferença negligível (~600 tokens de índice). Não justifica profiles separados por overhead.

## Decisão

1. **Fundir `exec` e `evol`** no profile **default** do Hermes (`~/.hermes`).
2. A skill `exocortex-vetor-ativo` classifica cada input como Execução, Evolução ou Manutenção **dinamicamente, por mensagem**.
3. O profile default carrega o bundle completo `exocortex-alpha` (33 skills).
4. **Manter `manut` como profile separado** (`~/.hermes/profiles/manut/`) porque:
   - Roda em background (cron, rotinas, automações)
   - Tem skills focadas (15 de 33) — sem slides, ofícios, estúdio
   - SOUL.md zelador (sem vetores Evolução/Execução)
   - Memória e sessão isoladas para não poluir sessão do executivo
5. Onboarding personaliza apenas o profile default (gera Macroverso → SOUL.md).

## Uso

```bash
hermes              # profile default — interativo, exec↔evol dinâmico
hermes -p manut     # profile manut — background, zelador
```

## Consequências

- Elimina troca de profile para alternar entre exec↔evol
- Reduz de 3 profiles para 2 (default + manut)
- Setup.sh instala apenas `profiles/manut/` (default é o `~/.hermes` raiz)
- Classificação de vetor passa a ser responsabilidade da skill `vetor-ativo`, não do profile

## Referências

- `docs/exocortex.ia/03_framework.md` — Vetores de Execução e Evolução
- Hermes prompt assembly Layer 7 — skill index injection
- ADR-011 D003 — Personas como seções no SOUL.md, não profiles separados
