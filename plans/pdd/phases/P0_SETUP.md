# Fase P0: Setup — Hermes Bootstrap

> **Status:** ⬜ Não Iniciada
> **Prompts:** Nenhum (fase manual)
> **Checkpoint:** `hermes doctor` passa ✅
> **Estimated Time:** 1-2 horas

---

## Objetivo

Clonar o Hermes Agent, instalar dependências, configurar LLM providers, e validar que o agente responde a prompts. **Nenhum prompt PDD é executado nesta fase.** É setup manual.

---

## Pré-Requisitos

- [ ] Python 3.12+ instalado
- [ ] `uv` package manager instalado (`pip install uv`)
- [ ] Docker instalado e rodando
- [ ] API Key: OpenAI (Codex subscription)
- [ ] API Key: OpenRouter (fallback)

---

## Passos

### P0.1 — Clonar Hermes Agent

```bash
cd /home/elder/projetos/pessoal/exocortex.saas/
git clone https://github.com/NousResearch/hermes-agent.git hermes-agent/
cd hermes-agent/
git tag -l  # Anotar a tag mais recente para versionamento
git checkout <latest-stable-tag>  # Usar tag, não main
```

**Verificação:** `ls hermes-agent/run_agent.py` existe.

**⚠️ Importante:** Clonar por tag, não por `main`. Anotar a versão no `KNOWLEDGE.md` (ver K-009).

---

### P0.2 — Instalar Dependências

```bash
cd hermes-agent/
# Usar setup script oficial
bash setup-hermes.sh
# OU manualmente com uv:
uv pip install -e .
```

**Verificação:** `hermes --version` retorna versão.

---

### P0.3 — Configurar LLM Providers

```bash
# Primary: OpenAI
hermes model
# Selecionar OpenAI, inserir API key

# Fallback: OpenRouter
# Configurar em config.yaml ou via hermes model
```

**Verificação:** `hermes` inicia e responde a "Olá, quem é você?"

---

### P0.4 — Validar Diagnóstico

```bash
hermes doctor
```

**Verificação:** Todos os checks passam. Anotar qualquer warning.

---

### P0.5 — Testar Gateway (Opcional nesta fase)

```bash
hermes gateway setup
# Configurar WhatsApp (QR code) e/ou Telegram (BotFather token)
```

**Verificação:** Mensagem enviada ao WhatsApp/Telegram recebe resposta.

---

### P0.6 — Documentar Versão e Config

Atualizar `plans/KNOWLEDGE.md` com:
- Versão/tag do Hermes instalado
- Quaisquer modificações feitas no setup
- Warnings do `hermes doctor`

Atualizar `plans/STATUS.md`:
- P0 → ✅ Completo
- Avançar foco para P1

---

## Critérios de Saída

| Critério | Método de Verificação |
|---|---|
| Hermes clonado e instalado | `hermes --version` |
| LLM provider configurado | Agente responde a prompts |
| Diagnóstico limpo | `hermes doctor` sem erros |
| Versão documentada | Entry em `KNOWLEDGE.md` |

---

## Próximo

Após P0 completo → avançar para `P1_IDENTITY.md` (início dos prompts PDD)
