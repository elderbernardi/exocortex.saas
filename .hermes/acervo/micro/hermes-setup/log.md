
# Log

## [2026-05-30] create | microverso hermes-setup ontology v2
- Criado microverso `hermes-setup` para registrar setup, replicabilidade e evolução do harness Hermes/Exocórtex.
- Definido `SCHEMA.md` local com Ontologia Multifocal v2: diretórios funcionais + Natures semânticas no frontmatter.
- Registrado contrato bloqueante `contracts/llm-wiki-adapter-contract.md`: LLM Wiki nativa é upstream mecânico; Acervo é fonte canônica; escrita somente via `acervo-llm-wiki-adapter` → `acervo-manager`.
- Registrada decisão `decisions/adr-007-ontology-v2-summary.md`: arquivos flat de Nature foram descontinuados; novas escritas usam diretórios funcionais.
- Registrado workflow `workflows/replicable-exocortex-setup.md`: setup reproduzível cria camadas, diretórios funcionais, bundle de skills, profiles e lint estrutural.
- Index atualizado com referências para contratos, decisões e workflows do microverso.
- Definições importantes vinculadas às ADRs do projeto Exocórtex SaaS: ADR-006 e ADR-007.

## [2026-05-30] update | Personal Artifact Workspace no microverso hermes-setup
- Registrada decisão `decisions/personal-artifact-workspace.md`: Drive é ferramenta de publicação, Acervo mantém fonte/assets/manifest/receipt e compartilhamento externo segue Draft-First.
- Registrado workflow `workflows/publish-final-artifacts.md`: pacote `_artifacts/`, exports finais, upload privado no Drive, receipt local e página semântica quando houver valor cognitivo.
- Atualizado `workflows/replicable-exocortex-setup.md` para incluir publicação de artefatos finais como etapa pós-setup.
- Index atualizado com decisão e workflow.

## [2026-05-30] update | Personal Intake Workspace no microverso hermes-setup
- Registrada decisão `decisions/personal-intake-workspace.md`: bruto entra por `_inbox/` e promoção semântica só ocorre após triagem.
- Registrado workflow `workflows/ingest-multichannel-inputs.md`: persistência, extração, roteamento e promoção semântica posterior.
- Atualizado `workflows/replicable-exocortex-setup.md` para incluir `_inbox/`, skill e ferramenta de intake como parte do setup reproduzível.
- Index atualizado com decisão e workflow.


## [2026-05-30] update | Intake Control Plane de referência
- Registrada ADR `docs/ADR/ADR-009-intake-control-plane.md`: GUI/gateway falam com um server HTTP mínimo antes do Hermes.
- Criado `apps/intake_control_plane/` no projeto com server local, schema do `IntakeEnvelope`, README e dropzone demo.
- Atualizado workflow `workflows/ingest-multichannel-inputs.md` para separar canal, server e Hermes.
- Atualizado workflow `workflows/replicable-exocortex-setup.md` para preservar o control plane no rollout reproduzível.
