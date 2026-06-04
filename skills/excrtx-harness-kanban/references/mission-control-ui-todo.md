# Mission Control UI TODO — Exocórtex

Session note captured from executive request:

> Anotar como TODO: implantar mission control personalizado para Exocórtex e integrado com UI de chat e arquivos. Buscar usar soluções prontas e consolidadas na comunidade.

## Canonical backlog wording

- Implantar um Mission Control personalizado para o Exocórtex, integrado com UI de chat e arquivos, priorizando soluções prontas e consolidadas na comunidade em vez de construir UI própria do zero.

## Retrieval context

Use when the executive resumes UI/cockpit/admin-surface work for Exocórtex.

Related architecture already present in the project at the time of capture:
- Existing UI was only a vanilla HTML dropzone demo for the Intake Control Plane.
- The API/control-plane pattern was `USER -> GUI/gateway -> intake control plane -> intake_ingest.py -> _inbox -> triagem -> promoção`.
- The next product-level question is not “polish the dropzone”, but “choose/implant a consolidated mission-control surface that can host chat + files + operational controls”.

## Bias for future work

Prefer evaluating mature community solutions before building a bespoke frontend. The expected output of a resumption is a shortlist/decision path, not immediate greenfield UI implementation.
