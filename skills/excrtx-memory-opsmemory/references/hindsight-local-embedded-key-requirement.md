# Hindsight local_embedded vs Key Requirement (Hermes)

Observed operational context:
- Hermes with `memory.provider: hindsight` and `mode: local_embedded` in `~/.hermes/hindsight/config.json`.
- `hermes memory status` reported plugin installed but `not available`.
- Missing keys reported: `HINDSIGHT_API_KEY` and `HINDSIGHT_LLM_API_KEY`.

Correct reading:
1. `local_embedded` describes where the memory storage/service runs.
2. Does not guarantee absence of platform authentication in the Hermes plugin.
3. LLM backend (model/base_url/key) is a separate layer from provider authentication.

Activation checklist (unambiguous):
1. Configure LLM backend (`llm_base_url`, `llm_model`, backend key).
2. Run `hermes memory status`.
3. If `HINDSIGHT_API_KEY` is in Missing, consider it a real provider activation blocker.
4. Choose between:
   - Provisioning a Hindsight platform key, or
   - Switching provider to a local-first alternative without this requirement.

Recommended message to user:
- Avoid "it's local, so no key needed."
- Use: "local_embedded = local storage; plugin may require its own authentication; LLM backend is another layer."
