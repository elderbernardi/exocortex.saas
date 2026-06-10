
# Replication Checklist — Personal Intake Workspace

Minimum capability to reproduce multichannel intake in another Exocórtex-Hermes:

1. Create `~/.hermes/acervo/_inbox/` with operational README.
2. Install `~/.hermes/acervo/global/contracts/personal-intake-workspace.md`.
3. Install `~/.hermes/acervo/global/tools/personal-intake-workspace.md`.
4. Install `~/.hermes/acervo/global/tools/intake_ingest.py`.
5. Install skill `exocortex/personal-intake-workspace`.
6. Update `setup.sh` and bundle to include the capability.
7. Register decision and workflow in microverso `hermes-setup`.
8. Validate minimum ingestion: text, PDF, image, and ZIP.
9. Validate semantic promotion to an existing microverso.
10. Preserve the separation `input -> _inbox -> acervo -> _artifacts -> publish`.
