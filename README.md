# Exocórtex.IA — Custom Cognitive Extension for Executives

> **An exoskeleton for the mind.** AI has no soul. You do.
>
> **Exocórtex.IA** is a structured cognitive extension designed for executives. It is not an autonomous replacement for your intelligence—it is a system designed to amplify what you are already capable of. Your cognition remains in command of thinking, creating, and deciding, while the Exocortex manages organization, memory persistence, context routing, and task execution.

---

## 🏛️ System Philosophy & Foundations

The Exocortex operates on a fundamental premise: LLMs have vast knowledge of the past but lack intent and are blind to your immediate present. The Exocortex acts as the structural bridge, translating your intent and immediate context to govern and focus the processing power of the AI.

```mermaid
graph TD
    A[Executive / Intent] -->|Governs| B(Exocórtex.IA / Method)
    B -->|Operates| C(Hermes Agent / Execution)
    C -->|Orchestrates| D[Skills, MCPs, Acervo and APIs]
```

### 1. The Three Concentric Layers (A Estrutura em Três Camadas Concêntricas)

To eliminate semantic drift and optimize contextual efficiency, all information and operations are organized into three concentric depth levels:

- **🏛️ Macroverso (Who Speaks):** This is the executive's personal "Constitution." It defines your core identity, non-negotiable values, communication style, tone, and personal boundaries. Generated during the onboarding phase, it rarely changes and silently governs all interactions.
- **🌍 Microversos (Semantic Domains):** These are live, self-contained semantic and operational entities. They represent specific clients, projects, disciplines, or areas of responsibility (e.g., `microverso-financas`, `microverso-juridico`). Each Microverso preserves its own context, rules, memory, and **sharing constraints** (e.g., `deny: [ALL]`, `allow: [gabinete]`, where `allow` takes precedence over `deny`).
- **🎯 Tarefa (The Operational Room):** The concrete room where execution happens. A task is short-lived and represents the active project or action. A task is anchored to a primary Microverso and may pull secondary Microversos for support. **Crucial semantic rule (EX-06):** _A Microverso is never a room; the Tarefa is the room._

---

### 2. The Three Operational Vectors

The Exocortex dynamically adjusts its cognitive posture by classifying every executive interaction into one of three operational vectors:

| Vector                    | Cognitive Posture      | Focus Area                         | Exocortex Behavior                                                                                                                             |
| :------------------------ | :--------------------- | :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| **🧠 Evolução (THINK)**   | Socratic Guide         | Idea refinement & understanding    | Challenging assumptions, asking 2-3 deep analytical questions, and promoting learnings to the Acervo. Never provides lazy, ready-made answers. |
| **⚡ Execução (DO)**      | Specialist Agent       | Production of premium deliverables | Fast, precise, and highly technical. Builds documents, drafts code, or coordinates execution with quality validation.                          |
| **🧹 Manutenção (CLEAN)** | Ecological Housekeeper | Ecosystem health & integrity       | Background verification: runs quality audits, updates indexes, archives stale logs, and validates paths/manifests.                             |

---

### 3. Core Governance & Safety Protocols

#### Draft-First Protocol (`excrtx-govern-draftfirst`)

Irreversible actions external to the local execution environment (e.g., sending emails, scheduling calendar events, committing/pushing to Git, publishing posts, or deploying code) **must never** be automated directly.

1. The Exocortex prepares the exact payload or plan.
2. The payload is displayed in the chat as a demarcated `📋 DRAFT`.
3. The system halts and waits for explicit approval (e.g., "OK", "proceed").
4. Execution occurs only after this consent.

#### Accuracy Verification (`excrtx-behavior-accuracy`)

The Exocortex is strictly forbidden from claiming that a system action (e.g., closing an issue, pushing a commit, creating a file) was successful without executing an empirical verification command and printing the raw command output as physical proof.

---

## 🧩 The 50 Custom Skills Catalog

This repository (`exocortex.saas`) packages the custom features and skills deployed on top of the **Hermes Agent** runtime. They are organized into 8 functional categories:

```mermaid
graph TD
    subgraph "Memory (Acervo)"
        EX11[EX-11 Acervo Mgr] --> EX12[EX-12 Wiki Adapt]
        EX11 --> EX13[EX-13 New Micro]
        EX11 --> EX14[EX-14 MV Setup]
        EX11 --> EX15[EX-15 MV Install]
        EX11 --> EX16[EX-16 Ops Memory]
        EX11 --> EX17[EX-17 Intake]
    end

    subgraph "Behavior & Governance"
        EX05[EX-05 Vector Classifier] --> EX06[EX-06 Canvas]
        EX05 --> EX07[EX-07 Briefing]
        EX08[EX-08 Draft-First]
        EX09[EX-09 Tool Gov]
        EX49[EX-49 Accuracy Verification]
        EX10[EX-10 Kanban Backlog]
    end

    subgraph "Quality Gates"
        EX18[EX-18 Anti-Slop Prose]
        EX19[EX-19 Anti-Slop Visual]
        EX20[EX-20 Design System] --> EX19
        EX21[EX-21 Quality Gate Orchestrator] --> EX18
        EX21 --> EX19
        EX52[EX-52 Quality Enforced] --> EX21
    end

    subgraph "Production"
        EX22[EX-22 Artifacts Mgr] --> EX52
        EX23[EX-23 Slide Gen] --> EX52
        EX24[EX-24 Official Docs Gen] --> EX52
    end

    subgraph "Integration"
        EX25[EX-25 Google Drive]
        EX27[EX-27 DocBrain Parser]
        EX28[EX-28 NotebookLM Route]
        EX29[EX-29 NotebookLM Ops]
        EX30[EX-30 Browser Automation]
    end
```

### 1. Onboarding & Assessment

- **`excrtx-onboard-welcome` (EX-01)**: Welcome flow. Detects empty Acervo, presents `WELCOME.md`, and triggers calibration.
- **`excrtx-onboard-interview` (EX-02)**: Conducts the structured 5-block interview to build the `SOUL.md` profile.
- **`excrtx-assess-selftest` (EX-03)**: Self-test validator. Audits system state and prints a `N/5` checkpoint score.
- **`excrtx-assess-repofit` (EX-04)**: Evaluates external repositories, identifying architectural fits and delta gaps.

### 2. Behavior & Governance

- **`excrtx-behavior-vetor` (EX-05)**: Classifies user inputs silently into Execution, Evolution, or Maintenance.
- **`excrtx-behavior-canvas` (EX-06)**: Implements the cognitive canvas (Macroverso Status, Primary vs. Secondary Microversos, Sharing Constraints, and Task Anchor).
- **`excrtx-behavior-briefing` (EX-07)**: Generates brief summaries of active microverso states and priority context.
- **`excrtx-govern-draftfirst` (EX-08)**: Intercepts all external integrations to enforce Draft-First gates.
- **`excrtx-govern-tools` (EX-09)**: Rules of engagement for tools, preventing unnecessary executions and enforcing strict logging.
- **`excrtx-harness-kanban` (EX-10)**: Maps current task states to the persistent Hermes Kanban system.
- **`excrtx-behavior-accuracy` (EX-49)**: Restricts the agent from asserting completion without printing command proof.

### 3. Memory & Acervo

- **`excrtx-memory-manager` (EX-11)**: Core memory manager for the 4-layer Acervo. Enforces access scopes and directory routing.
- **`excrtx-memory-wikiadapt` (EX-12)**: Translates native Hermes LLM-Wiki structures into the 11 Natures of the Exocortex Acervo.
- **`excrtx-memory-newmicro` (EX-13)**: Scaffolds a new Microverso directory structure from standard templates.
- **`excrtx-memory-mvsetup` (EX-14)**: Designates a microverso as a replication seed for future setup runs.
- **`excrtx-memory-mvinstall` (EX-15)**: Installs packaged microversos, resolving skill, python/node, and API dependencies.
- **`excrtx-memory-opsmemory` (EX-16)**: Orchestrates operational memories (e.g., Hindsight) to act as short-term retrieval buffers.
- **`excrtx-memory-intake` (EX-17)**: Multi-channel file and media intake pipeline (OCR, STT, PDF parsing) routed to `$ACERVO/_inbox/`.

### 4. Quality Gates

- **`excrtx-quality-antislop` (EX-18)**: Text quality gate. Grades generated prose on directness, density, rhythm, and authenticity, rejecting AI cliches. Requires a minimum score of `35/50`.
- **`excrtx-quality-taste` (EX-19)**: Visual quality gate. Rotes layouts to specialized sub-skills (`gpt-taste`, `brutalist`, `brandkit`). Rejects headers > 3 lines and repeating grid templates.
- **`excrtx-quality-designsys` (EX-20)**: Design token cascade resolver (Global `DESIGN.md` -> Microverso `DESIGN.md`).
- **`excrtx-quality-gate` (EX-21)**: Unified quality gate controller that intercepts all outbound responses.
- **`excrtx-quality-skilljudge`**: Automated skill quality evaluation using multi-dimensional rubric and LLM judge.
- **`excrtx-quality-gepa`**: GEPA (Genkit Eval Prompt Audit) loop for automated skill rewriting and quality gating.

### 5. Production & Artifacts

- **`excrtx-produce-artifacts` (EX-22)**: Manages creation, indexing, views, and exports of durable documents in `$ACERVO/_artifacts/`.
- **`excrtx-produce-slides` (EX-23)**: Generates high-quality presentations using Marp Markdown to HTML/PDF/ZIP.
- **`excrtx-produce-oficios` (EX-24)**: Builds formal institutional letters from DOCX/HTML templates.

### 6. Integration

- **`excrtx-integrate-gdrive` (EX-25)**: Google Drive client. Hardened search queries (ignoring trashed files) and handle paginated list results.
- **`excrtx-integrate-oauth` (EX-26)**: Setup and diagnostic utility for configuring external OAuth-based MCP servers.
- **`excrtx-integrate-docbrain` (EX-27)**: Parser engine integration for ingesting legacy PDFs and documents.
- **`excrtx-integrate-nlmroute` (EX-28)**: Routes research requests to NotebookLM CLI (`nlm`) or NotebookLM MCP.
- **`excrtx-integrate-nlmops` (EX-29)**: Operational workflows to ingest sources and query NotebookLM notebooks.
- **`excrtx-integrate-browser` (EX-30)**: Autonomously controls local Chrome instances using `playwright` and `browser-use`.

### 7. Harness & Infrastructure

- **`excrtx-harness-promptlog` (EX-31)**: Auditable log of all configuration prompts written to `MEMORY.md`.
- **`excrtx-harness-surfaces` (EX-35)**: Routes communication interfaces (Telegram for Chat, TUI/CLI for Admin, Dashboard for cockpit).
- **`excrtx-harness-imbroke` (EX-48)**: financial contingency model fallback (OpenRouter free model watchdog and recovery router).
- **`excrtx-harness-tooldev` (EX-50)**: Standard API for writing and registering custom `/tool` extensions.
- **`excrtx-hermes-extensions` (EX-51)**: Guidelines for writing custom commands and dispatch paths in `gateway/run.py`.
- **`excrtx-harness-delivery`**: Delivery pipeline orchestration for artifact publication and distribution.
- **`excrtx-harness-maintenance` (EX-56)**: Síndico persona with 4 maintenance routines (weekly audit, inbox triage, artifact quality, publication check).
- **`excrtx-integrate-mcp`**: MCP server discovery, registration, and lifecycle management.
- **`excrtx-brandkit-generator`**: Brand identity kit generation from Macroverso design tokens.
- **`excrtx-github-issue-planning`**: GitHub issue planning and roadmap coordination.
- **`assessment-question-authoring`**: Structured assessment question creation for calibration and evaluation.

---

## ⚙️ Installation & Provisioning

### Prerequisites

- **OS**: Linux (Debian, Ubuntu, Arch) or macOS.
- **System Tools**: `git`, `curl`, `rsync`, `python3` (>=3.11), `pip`, `venv`.
- **Containers**: `docker` & `docker compose` (Required only if Hindsight local memory is enabled).

---

> **🤖 AI Agents**: If you are an AI agent (Claude, Gemini, GPT, etc.) installing or diagnosing this system via terminal, use [INSTALL.md](INSTALL.md) instead — a structured runbook with pre-conditions, executable commands, and verification steps designed for machine consumption.
>
> **`INSTALL.md` lives only in this source repository** (`elderbernardi/exocortex.saas`); it is **not** copied into the runtime (`~/.hermes`, `~/exocortex`). If you can't find it, you are not in the source checkout — `git clone https://github.com/elderbernardi/exocortex.saas.git && cd exocortex.saas`, then open `INSTALL.md`. A runtime-side pointer also lives in the Acervo at `micro/exocortex-ops/knowledge/install-runbook-location.md`.

### Step-by-Step Installation

#### 1. Execute the Bootstrap Installer

This command pulls the installer, checks for OS dependencies, installs the Hermes Agent CLI (if not present), and clones the Exocortex repository to a local cache directory:

```bash
# Standard interactive installation
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash

# Guided installation with explicit review of env vars and API keys
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash -s -- --step-by-step
```

To automatically install and bind the **Telegram Gateway**, pass the token in the environment:

```bash
TELEGRAM_BOT_TOKEN="your_telegram_bot_token" curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
```

To pin a specific tag or version:

```bash
VERSION=v1.0.5 curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
```

#### Full Installation (All Utilities)

A single command that activates every optional component — WebUI cockpit, Hindsight local memory, Telegram gateway, reasoning keys, DocBrain, Firecrawl, and Context7 — with guided step-by-step review and post-install cognitive calibration:

```bash
EXOCORTEX_DEFAULT_PROVIDER="deepseek" \
EXOCORTEX_DEFAULT_API_KEY="sk-..." \
EXOCORTEX_AUX_API_KEY="sk-or-..." \
TELEGRAM_BOT_TOKEN="123456:ABC..." \
EXOCORTEX_ENABLE_HERMES_WEBUI=1 \
EXOCORTEX_ENABLE_HINDSIGHT=1 \
FIRECRAWL_API_KEY="fc-..." \
FIRECRAWL_BASE_URL="http://127.0.0.1:3002" \
CONTEXT7_API_KEY="c7-..." \
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh \
  | bash -s -- --step-by-step --calibrate
```

What each marker activates:

| Variable | Component | Notes |
|---|---|---|
| `EXOCORTEX_DEFAULT_*` | Default LLM role (`{PROVIDER,MODEL,API_KEY,BASE_URL}`) | Primary LLM — reasoning, routing, all skills. **Always used; required.** Empty `BASE_URL` is derived from `setup/providers.json`. |
| `EXOCORTEX_VISION_*` | Vision LLM role | Multimodal (image/OCR) model. Each empty field **inherits the default** role field-by-field. |
| `EXOCORTEX_AUX_*` | Auxiliary LLM role | External software: DocBrain parser and the Hindsight LLM backend. Each empty field **inherits the default**. |
| `TELEGRAM_BOT_TOKEN` | Telegram Gateway | Bot token from BotFather. Enables remote chat interface. |
| `EXOCORTEX_ENABLE_HERMES_WEBUI=1` | Hermes WebUI cockpit | MIT-licensed `nesquena/hermes-webui`. Access at `127.0.0.1:8787` or via Tailscale. |
| `EXOCORTEX_ENABLE_HINDSIGHT=1` | Hindsight local memory | Docker container for persistent cross-session memory. Requires `docker` + `docker compose`. |
| `FIRECRAWL_API_KEY` | Firecrawl crawling/extract | Web scraping engine. Optional — only if running a Firecrawl instance. |
| `FIRECRAWL_BASE_URL` | Firecrawl endpoint | Default: `http://127.0.0.1:3002`. Set if your instance runs elsewhere. |
| `CONTEXT7_API_KEY` | Context7 docs MCP | Technical documentation lookup. Optional. |

> **The 3 LLM roles** are the single source of truth for every LLM call in this repo. Configure
> just the **default** role for most setups — **vision** and **auxiliar** inherit it field-by-field
> when unset. Providers (`openrouter`, `deepseek`, `openai`, `gemini`, `xai`, `opencode`, `opencode-go`)
> and their base URLs come from `setup/providers.json`; resolve the effective config with
> `python3 scripts/lib/llm_roles.py all`. Legacy installs are migrated once by
> `scripts/migrate-env-roles.py` (run automatically by `setup.sh`): old `OPENROUTER`/`DEEPSEEK`/`OPENCODE`
> keys map to **default**, `DOCBRAIN_LLM` to **auxiliar**, `OPENAI`/`GEMINI`/`GOOGLE` to **vision**.

Flags used:

- `--step-by-step` — Pauses at each configuration block (paths, env vars, API keys, features) for explicit review before proceeding. Every value is shown masked — no secrets in terminal scrollback.
- `--calibrate` — Runs the interactive behavioral calibration suite at the end of setup, testing each core feature (vector classification, draft-first, accuracy verification) against the model and injecting corrective prompts if output drifts.

If you prefer a non-interactive full install (CI/CD, headless server), replace `--step-by-step --calibrate` with `--yes`:

```bash
EXOCORTEX_DEFAULT_PROVIDER="deepseek" \
EXOCORTEX_DEFAULT_API_KEY="sk-..." \
EXOCORTEX_ENABLE_HERMES_WEBUI=1 \
EXOCORTEX_ENABLE_HINDSIGHT=1 \
curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh \
  | bash -s -- --yes
```

##### Installer Flags

| Flag | Effect |
|---|---|
| `--yes`, `-y` | Headless mode — no prompts, persists detected values and runs all steps |
| `--step-by-step` | Guided mode — pauses at each config block for explicit review |
| `--init-only` | Saves configuration to `.env.local` and skips provisioning steps |
| `--skip-env-check` | Skips prerequisite validation in `setup.sh` |
| `--imbroke` | Activates OpenRouter free-model contingency routing |
| `--calibrate` | Runs cognitive calibration at the end of setup |
| `-h`, `--help` | Prints usage and exits |

##### Environment Variable Preflight

Before touching Hermes, the installer runs a preflight scan of all relevant env vars (API keys, tokens, endpoints). Sensitive values are **masked** in the output — only the first and last few characters are shown. The preflight also flags suspicious values (whitespace inside a key, keys shorter than 12 chars) with actionable warnings. This means you can verify your credentials are detected **before** the install proceeds, without exposing secrets in terminal scrollback or CI logs.

If a command fails at any stage, the installer captures stderr, scrubs any secrets from it, and prints the last useful lines alongside a hint about what went wrong and how to recover — instead of a bare exit code.

#### 2. The `setup.sh` Orchestrator

The installer will automatically invoke `setup.sh`. If you want to customize home paths, you can run `setup.sh` manually:

```bash
HERMES_HOME=~/.hermes EXOCORTEX_HOME=~/exocortex bash setup.sh
HERMES_HOME=~/.hermes EXOCORTEX_HOME=~/exocortex bash setup.sh --step-by-step
```

To also provision the Hermes WebUI web cockpit (optional, MIT-licensed `nesquena/hermes-webui`):

```bash
EXOCORTEX_ENABLE_HERMES_WEBUI=1 HERMES_HOME=~/.hermes EXOCORTEX_HOME=~/exocortex bash setup.sh
```

The WebUI source is pinned via `provision/sources/sources.lock.yaml` (audited SHA ref). Access at `http://127.0.0.1:8787` or via Tailscale.

##### What `setup.sh` Executes:

- **`step-00`**: Validates Hermes version compatibility (Expected bounds: `2026.4.8` to `2026.4.16`).
- **`step-01`**: Provision Hindsight database container if `EXOCORTEX_ENABLE_HINDSIGHT=1` is provided.
- **`step-02`**: Initializes the directory trees for the workspace, logs, task boards, and the 4-layer Acervo structure.
- **`step-03` to `step-05`**: Copies and installs all 50 `excrtx` skills, bundles, and execution profiles (`default` and `manut`).
- **`step-06` (Hardening)**:
  - Applies a search paging patch to `google_api.py`.
  - Removes legacy email skills (`himalaya` / `hymalaia`) to ensure Google Workspace takes precedence.
  - Removes `composio` from the MCP registry in favor of direct API clients.
- **`step-06b` to `step-11`**: Sets up Google Auth tools, clones and compiles the DocBrain engine, installs the NotebookLM CLI, provisions Browser Automation files, optionally provisions the Hermes WebUI cockpit (`nesquena/hermes-webui`, MIT), and links Context7 documentation MCP.
- **`step-12` to `step-14`**: Performs final key verifications and validates that all 50 skills are correctly mapped in the runtime.
- **`step-15`**: Launches the interactive prompt calibration if `--calibrate` is passed.

---

## 🛠️ Post-Installation & Integration Guide

For the Exocortex to operate at full capacity, complete the following post-installation steps:

### 1. Account Calibration & Onboarding

Upon launching your first session, the Exocortex checks if your `SOUL.md` (the Macroverso) is populated. If empty, it triggers the welcome flow:

1. Launch the interactive session:
   ```bash
   hermes
   ```
2. Initiate the onboarding questionnaire:
   ```text
   vamos começar o onboarding
   ```
3. Answer the structured questions covering **Identidade**, **Comunicação**, **Domínios**, **Preferências**, and **Integrações**. This writes your personality profile to `~/.hermes/SOUL.md`.

---

### 2. Prompt-Driven Development (PDD) Behavior Calibration

To ensure the LLM model respects the 12 core behavioural features (Vector classification, Draft-first, verification proofs, etc.), run the interactive calibration suite:

```bash
bash scripts/calibrate-hermes.sh
```

This script runs a test prompt for each feature, shows you the model output alongside the acceptance criteria, and asks for your verification. If the output drifts, it automatically injects a Socratic corrective prompt to recalibrate the model.

---

### 3. Google Workspace & Drive API Setup (OAuth 2.0)

The Google Workspace integration uses direct desktop OAuth credentials.

#### Step A: Configure the GCP Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and name it (e.g., `Exocortex-Workspace`).
3. Search for **Google Drive API** in the API Library and click **Enable**.
4. Configure the **OAuth Consent Screen**:
   - Set User Type to **External**.
   - Add your email address under **Test Users**.
   - Add the `.../auth/drive` scope.
5. Create Credentials:
   - Click **Create Credentials** > **OAuth client ID**.
   - Choose **Desktop application**.
   - Download the credential JSON file and rename it to `google_client_secret.json`.

#### Step B: Complete the OAuth Flow locally

Move the credential file to your home config and execute the setup utility:

```bash
# 1. Move and register the client secret
cp /path/to/downloaded/secret.json ~/.hermes/google_client_secret.json
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret ~/.hermes/google_client_secret.json

# 2. Request authorization URL
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
```

- Copy the output URL, paste it into your browser, log in, and authorize the application.
- Upon redirection, copy the string parameter after `code=` in the browser address bar.

```bash
# 3. Save the token using the code copied
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "PASTE_YOUR_OAUTH_CODE_HERE"

# 4. Verify credentials
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

If this prints `AUTHENTICATED`, the Google Workspace driver is fully functional.

---

### 4. NotebookLM Integration (`nlm` CLI)

NotebookLM integration requires the `notebooklm-mcp-cli` python package.

1. Verify `uv` is installed, then install the package:
   ```bash
   uv tool install notebooklm-mcp-cli --force
   ```
   _(Fallback: `python3 -m pip install --upgrade notebooklm-mcp-cli`)_
2. Authenticate the CLI:
   ```bash
   nlm login
   ```
3. Verify the authentication:
   ```bash
   nlm login --check
   ```
4. Register the MCP server in Hermes:
   ```bash
   hermes mcp add notebooklm --command notebooklm-mcp
   ```

---

### 5. DocBrain Parser Engine Setup

DocBrain is used to parse complex documents and PDFs.

1. Ensure Node.js and `npm` are installed.
2. Fresh installs may clone the parser repository to `~/exocortex/tools/docbrain`, but the live runtime can also use a repository-local checkout. Resolve the active workspace with `api health`, then verify/build that workspace:
   ```bash
   DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-$HOME/exocortex/tools/docbrain}"
   cd "$DOCBRAIN_DIR"
   npm install
   npm run build
   ```
3. DocBrain is configured by the **auxiliary** LLM role. The setup `step-08` generates DocBrain's
   `.env` from `EXOCORTEX_AUX_*`; if the aux role is empty, it inherits the **default** role:
   ```bash
   export EXOCORTEX_DEFAULT_PROVIDER="deepseek"
   export EXOCORTEX_DEFAULT_API_KEY="your-default-key"
   export EXOCORTEX_AUX_API_KEY="your-aux-key"        # optional — isolates DocBrain's LLM key
   export FIRECRAWL_BASE_URL="http://127.0.0.1:3002"  # se usar Firecrawl local
   ```
   _(Inspect the resolved roles with `python3 scripts/lib/llm_roles.py all`.)_

---

### 6. Browser Automation Skill Runtime

The browser automation skill uses `browser-use` and `playwright`.

1. To install the chromium dependencies and python packages in the local skill sandbox:
   ```bash
   cd ~/.hermes/skills/excrtx/excrtx-integrate-browser
   # The wrapper script does auto-provisioning on first execution:
   bash scripts/browser-use.sh open https://example.com
   ```
2. This will download and cache Playwright Chromium binaries under `.runtime/ms-playwright/`.

---

### 7. Financial Contingency Mode (Modo Imbroke)

If your OpenRouter account runs out of credits, you can toggle the system to use free models via the free-routing CLI:

```bash
# Enable free-routing circuit breaker
python3 scripts/openrouter_free_model_router.py --imbroke --activate

# Check routing status
python3 scripts/openrouter_free_model_router.py --status
```

_Note: After enabling or disabling imbroke mode, restart your active Hermes sessions with `/new` to reload the settings._

---

## 🧑‍💻 Developer Onboarding & Knowledge Base

For developers looking to contribute, extend, or troubleshoot Exocortex.IA, the primary and most up-to-date documentation is located inside the `exocortex-dev` Microverso:

- **Wiki Catalog & Schema**: Refer to the Microverso Index at [index.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/_meta/index.md) and [SCHEMA.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/_meta/SCHEMA.md).
- **System Architecture**: Detailed internal system structure and Trilho A/B pathways are documented in [architecture.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/knowledge/architecture.md).
- **Development Standards**: For coding style guidelines, skill requirements, and automated validation gates, see [development-standards.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/contracts/development-standards.md).
- **Skill vs. MCP Choice**: Deciding when to build a custom skill vs. adding an MCP server is documented in [skill-vs-mcp-selection.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/decisions/skill-vs-mcp-selection.md) (ADR-006).
- **Acervo Control Plane**: The Acervo-specific authority model is documented in [adr-022-acervo-mcp-control-plane.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/decisions/adr-022-acervo-mcp-control-plane.md) (ADR-022): filesystem stays the physical truth, while semantic agentic writes should converge on a shared core exposed by CLI and MCP.
- **Creating Custom Skills**: Step-by-step workflow (SOP) to scaffold, compile, and test skills is available in [create-custom-skill.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/workflows/create-custom-skill.md).
- **Running Preflight Audits**: Process to execute deterministic and semantic checks before committing code can be found in [run-preflight-checks.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/workflows/run-preflight-checks.md).
- **Acervo Control Plane (CLI + MCP)**: The local operational contract is `python3 scripts/acervoctl.py`, and the agentic MCP surface now lives in `python3 scripts/acervo_mcp_server.py` as a thin adapter over the same core. The installer auto-registers `acervo` in Hermes and runs both the local self-test and `hermes mcp test acervo`; if that health check fails, degraded mode is explicit: keep using `acervoctl` and direct file access for human/infra/maintenance.

  Use each surface on purpose:
  - **human / infra / corrective maintenance** → direct filesystem access is valid
  - **local scripts, tests, adapters, repeatable semantic flows** → `python3 scripts/acervoctl.py`
  - **agents already operating through Hermes tools** → MCP `acervo`
  - **if MCP health fails** → fall back to `acervoctl`, not ad hoc MCP-only logic

  ```bash
  python3 scripts/acervoctl.py list-microversos
  python3 scripts/acervoctl.py search --query macroverso
  python3 scripts/acervoctl.py prepare-write --microverso exocortex-dev --nature decisions --title "Nova decisão"
  python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$PWD/acervo"
  hermes mcp test acervo
  ```

Always check this Microverso memory first to ensure your development aligns with the active conventions and architectural guidelines of the Exocortex.

> Installer note: `setup.sh` now wires the local `acervo` MCP automatically. If health fails, the fallback is deliberate — `acervoctl` remains the official local surface and direct filesystem access stays valid for human/infra/maintenance.

---

## 🏃 Daily Operation

### 1. Interactive Session (Execution & Evolution)

Launch the standard interative session for daily tasks and cognitive evolution:

```bash
hermes
```

### 2. Maintenance Profile (Background Cleaning)

Run the housekeeping agent profile to check for dead links, audit file schemas, and clean session logs:

```bash
hermes -p manut
```

### 3. Pre-flight Quality Checks

Before committing changes to this repository, run the validation suites:

```bash
# Run core quality audit checks
python3 .agent/scripts/checklist.py .

# Run complete validation, including E2E and Lighthouse
python3 .agent/scripts/verify_all.py . --url http://localhost:3000
```

---

## ⚖️ License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
