# Hindsight local_embedded vs Key Requirement (Hermes)

Observed operational context:
- Hermes with `memory.provider: hindsight` and `mode: local_embedded` in `~/.hermes/hindsight/config.json`.
- `hermes memory status` reported plugin installed but `not available`.
- Missing keys reported: `HINDSIGHT_API_KEY` and `HINDSIGHT_LLM_API_KEY`.

Correct reading:
1. `local_embedded` describes where the memory storage/service runs.
2. Does not guarantee absence of platform authentication in the Hermes plugin.
3. LLM backend (model/base_url/key) is a separate layer from provider authentication.

Two distinct keys, two distinct sources:
- **LLM backend** (`HINDSIGHT_LLM_API_KEY`, model, base_url) — Hindsight's reasoning backend. This is driven by the Exocórtex **auxiliar** role (`EXOCORTEX_AUX_{PROVIDER,MODEL,API_KEY,BASE_URL}`), reserved for external software; it inherits the **default** role field-by-field when empty. `setup/step-01-hindsight.sh` generates the Hindsight LLM backend config from the resolved aux role — you do not set `HINDSIGHT_LLM_API_KEY` by hand.
- **Platform authentication** (`HINDSIGHT_API_KEY`) — the Hindsight cloud provider key. This is **not** an LLM role; it remains a standalone service credential, provisioned independently.

Activation checklist (unambiguous):
1. Configure the LLM backend via the auxiliar role (EXOCORTEX_AUX_*) and run step-01, which writes `llm_base_url`, `llm_model`, and the backend key.
2. Run `hermes memory status`.
3. If `HINDSIGHT_API_KEY` is in Missing, consider it a real provider activation blocker — this is the cloud platform key, separate from the LLM role.
4. Choose between:
   - Provisioning a Hindsight platform key, or
   - Switching provider to a local-first alternative without this requirement.

Recommended message to user:
- Avoid "it's local, so no key needed."
- Use: "local_embedded = local storage; plugin may require its own authentication; LLM backend is another layer."
