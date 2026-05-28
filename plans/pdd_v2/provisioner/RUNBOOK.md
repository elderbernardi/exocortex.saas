---
name: exocortex-provisioner
version: 2.0.0
trigger:
  - "instale o exocortex"
  - "configure o exocortex"
  - "provisione hermes"
  - "install exocortex"
purpose: >
  Transform a fresh Hermes Agent instance into a fully configured Exocórtex.IA
  by orchestrating installation, golden image provisioning, and PDD v2 execution.
paths:
  root: "."
  lib: "./lib"
  prompts: "./prompts"
  artifacts: "./artifacts"
  docker: "./docker"
---

# Exocórtex.IA — Provisioner Runbook

Você é o **Provisioner do Exocórtex.IA**. Quando o humano solicitar instalação
ou configuração do Exocórtex, siga este runbook sequencialmente.

**IMPORTANTE**: Todos os paths neste documento são relativos ao diretório onde
este RUNBOOK.md se encontra. Antes de executar, resolva o diretório base:

```bash
PROVISIONER_DIR="$(cd "$(dirname "$0")" && pwd)"
# OU, se lendo este arquivo:
PROVISIONER_DIR="$(dirname "$(readlink -f RUNBOOK.md)")"
```

## Regras de Interação

- 🗣️ = Pergunte ao humano (máximo 3 perguntas)
- 🤖 = Execute automaticamente (sem perguntar)
- ⏸️ = Pause e reporte progresso
- ❌ = Se falhar, tente corrigir automaticamente (max 2x). Se persistir, pergunte.

---

## FASE 0: Reconhecimento (🤖 automático)

Execute silenciosamente e armazene os resultados:

```bash
bash "$PROVISIONER_DIR/lib/detect_environment.sh" --quiet
```

Análise do output:
- `hermes_installed`: true → pular instalação
- `docker_available`: true → oferecer opção Docker
- `existing_skills_count` > 0 → realizar backup silencioso e sobrescrever
- `artifacts_present`: false → ERRO: repositório incompleto, abortar

---

## FASE 1: Decisões (🗣️ máximo 3 perguntas)

### Pergunta 1 — Modo de instalação
**Só pergunte se Docker estiver disponível E Hermes não instalado.**
Se Docker não disponível OU Hermes já instalado, assuma `local`.

```
Deseja instalar o Exocórtex:
  1. Localmente (~/.hermes) — recomendado
  2. Em container Docker (instância isolada)
  [default: 1]
```

### Pergunta 2 — Autenticação LLM
**Só pergunte se não houver credenciais existentes.**
Se `existing_provider != "none"`, use credenciais existentes e informe o humano.

```
Como deseja autenticar com o LLM?
  1. Nous Portal (OAuth — abre navegador) — modelos Nous
  2. ChatGPT / OpenAI (OAuth — abre navegador) — modelos OpenAI
  3. API Key direta (OpenRouter, Anthropic, etc.)
  4. Já tenho configuração — usar credenciais existentes
  [default: 2]
```

### Pergunta 3 — API Key
**Só pergunte se a resposta à Pergunta 2 for opção 3.**

```
Cole sua API key (OpenRouter ou Anthropic):
```

Detecte automaticamente o provider pela key:
- `sk-or-...` → OpenRouter
- `sk-ant-...` → Anthropic
- Outro padrão → pergunte qual provider

---

## FASE 2: Instalação do Hermes (🤖 automático)

### Se Hermes NÃO instalado:

```
⏸️ "Instalando Hermes Agent..."
```

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Aguardar conclusão. Verificar:
```bash
hermes --version
```

Se falhar → ❌ reportar erro detalhado ao humano.

### Se Hermes JÁ instalado:

```
ℹ️ Hermes {version} já instalado. Prosseguindo com configuração.
```

---

## FASE 3: Configuração do LLM (🤖 automático)

Baseado na resposta da Pergunta 2:

### Opção 1 — Nous Portal (OAuth):
```bash
hermes auth add nous --type oauth
```
(Abre navegador para autenticação)

### Opção 2 — ChatGPT / OpenAI Codex (OAuth):
```bash
hermes auth add codex-oauth
```
(Abre navegador para autenticação)

### Opção 3 — API Key direta:
```bash
# Detectar provider e adicionar via CLI
hermes auth add openrouter --api-key "$KEY"   # Se OpenRouter
# OU
hermes auth add anthropic --type api-key --api-key "$KEY"     # Se Anthropic
```

### Opção 4 — Existente:
Nenhuma ação.

### Validação (todas as opções):
```bash
hermes chat -q "Responda APENAS a palavra: OK" --quiet 2>&1 | head -5
```

Se a resposta contém "OK" → ✅ LLM conectado
Se falhar → ❌ "Falha na conexão com o LLM. Verifique suas credenciais."

```
⏸️ "✅ LLM configurado ({provider}). Testando conectividade..."
```

---

## FASE 4: Provisioning — Golden Image (🤖 automático)

### Pré-verificação:
```bash
bash "$PROVISIONER_DIR/lib/verify.sh" --pre-provision
```
Se falhar → ❌ abortar com detalhes.

### Detecção de conflito:
Se `existing_skills_count > 0`:
Realizar o backup automático usando a data/hora atual:
```bash
TIMESTAMP=$(date +%Y%m%d%H%M%S)
mv "$HERMES_HOME/skills/exocortex" "$HERMES_HOME/skills/exocortex_backup_$TIMESTAMP" 2>/dev/null || true
```
ℹ️ "Encontradas {N} skills existentes. Backup automático realizado antes de aplicar a golden image."

### Copiar golden image:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
ARTIFACTS="$PROVISIONER_DIR/artifacts"

# Skills (15)
TIMESTAMP=$(date +%Y%m%d%H%M%S)
mv "$HERMES_HOME/skills/exocortex" "$HERMES_HOME/skills/exocortex_backup_$TIMESTAMP" 2>/dev/null || true

mkdir -p "$HERMES_HOME/skills/exocortex"
cp -r "$ARTIFACTS/skills/"* "$HERMES_HOME/skills/exocortex/"

# Acervo (4 camadas)
mkdir -p "$HERMES_HOME/acervo/"{macro,global,micro/_template,shared/cross-refs}
cp -r "$ARTIFACTS/acervo/"* "$HERMES_HOME/acervo/"

# Profiles (exec, evol)
mkdir -p "$HERMES_HOME/profiles"
cp -r "$ARTIFACTS/profiles/"* "$HERMES_HOME/profiles/"

# Bundle
mkdir -p "$HERMES_HOME/skill-bundles"
cp "$ARTIFACTS/skill-bundles/"*.yaml "$HERMES_HOME/skill-bundles/"

# Identity seed
cp "$ARTIFACTS/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
```

### Pós-verificação:
```bash
bash "$PROVISIONER_DIR/lib/verify.sh" --post-provision
```

```
⏸️ "✅ Golden image instalada: 15 skills, 4 camadas, 2 profiles."
```

---

## FASE 5: Execução do PDD (🤖 automático com reportes)

```
⏸️ "Configurando identidade do Exocórtex. Isso levará alguns minutos..."
```

### Sequência de execução:

⚠️ **REGRA CRÍTICA PARA O AGENTE:** Não crie arquivos de script auxiliares (como `run_pdd.py` ou `.sh`) nem tente rodar comandos como `find`, `ls` ou inspecionar os arquivos de prompt antes da execução. A automação já está pronta.

Para executar uma fase inteira (ex: `P1`), simplesmente **copie e rode o bloco de código bash abaixo DIRETAMENTE no seu terminal integrado**. O script em bash fará a leitura, o loop de execução e a auditoria de forma totalmente automática.


```bash
FASE="P1" # Troque por P2, P3, P4 ou P5
mkdir -p "$PROVISIONER_DIR/state"

if [ -f "$PROVISIONER_DIR/state/$FASE.done" ]; then
  echo "Fase $FASE já concluída. Pulando..."
else
  # Ativar bundle
  hermes chat -q "/exocortex-alpha" --quiet
  
  CONTEXT=$(cat "$PROVISIONER_DIR/prompts/_MASTER_CONTEXT.md")
  
  for PROMPT_FILE in $(ls -v "$PROVISIONER_DIR/prompts/${FASE}_"*.md); do
    echo "Executando $PROMPT_FILE..."
    CLEAN_PROMPT=$(sed '/^---$/,/^---$/d' "$PROMPT_FILE")
    
    if [[ "$PROMPT_FILE" == *"_001_"* ]]; then
      # Primeiro prompt injeta o contexto mestre
      hermes chat -q "$CONTEXT"$'\n\n'"$CLEAN_PROMPT" -c --quiet
    else
      hermes chat -q "$CLEAN_PROMPT" -c --quiet
    fi
  done
  
  # Auditoria e Checkpoint
  bash "$PROVISIONER_DIR/lib/drift_audit.sh" $FASE
  if [ $? -eq 0 ]; then
    touch "$PROVISIONER_DIR/state/$FASE.done"
  fi
fi
```

5. **Reporte ao humano:**
   ```
   ⏸️ "✅ Fase P{N} ({nome}) completa.
       Skills: {count}
       Self-test: {score}/5
       Drift audit: {result}"
   ```

5. **Em caso de falha:**
   - Erro técnico (timeout, crash): retry automático (max 2x)
   - Drift audit falhou: enviar prompt corretivo ao Hermes
   - Self-test abaixo do gate: enviar prompt de correção
   - 3 falhas seguidas: parar e perguntar ao humano

### Ordem dos prompts:

| Fase | Prompts | Nome | Gate |
|------|---------|------|------|
| P1 | 001-005 | Identity | self-test ≥ 2/5 |
| P2 | 006-012 | Memory | self-test ≥ 3/5 |
| P3 | 013-021 | Behavior | self-test ≥ 4/5 |
| P4 | 022-026 | Validation | self-test = 5/5 |
| P5 | 027 | Production | GRADUATION |

---

## FASE 6: Finalização (🤖 automático)

### Verificação final:
```bash
hermes doctor
bash "$PROVISIONER_DIR/lib/drift_audit.sh" ALL
```

### Reporte final ao humano:

```
✅ Exocórtex.IA instalado e configurado com sucesso!

   ┌─────────────────────────────────────┐
   │  Exocórtex.IA — PRODUCTION          │
   ├─────────────────────────────────────┤
   │  Skills:    15                      │
   │  Profiles:  exec (ação), evol (✨)   │
   │  Bundle:    exocortex-alpha         │
   │  Self-test: 5/5                     │
   │  State:     PRODUCTION              │
   └─────────────────────────────────────┘

   Para usar:
     hermes chat -s "$SKILLS"
     hermes profile use exec    # modo execução
     hermes profile use evol    # modo exploração

   Para verificar:
     hermes chat -q "Execute o self-test do Exocórtex."
```

---

## MODO DOCKER (variante)

Se o humano escolheu Docker na Fase 1:

### Substituições:
- HERMES_HOME = `/opt/data` (dentro do container)
- Instalação do Hermes: via Dockerfile (imagem base)
- Credenciais: montadas como volume read-only

### Fluxo:

```bash
# Build
docker compose -f "$PROVISIONER_DIR/docker/docker-compose.yml" build

# Start
docker compose -f "$PROVISIONER_DIR/docker/docker-compose.yml" up -d

# Provisioning (de fora do container)
docker exec exocortex-provisioner \
  bash /workspace/lib/verify.sh --post-provision

# PDD execution (de fora do container — os prompts vão via hermes CLI)
docker exec exocortex-provisioner \
  hermes chat -q "$PROMPT" -s "$SKILLS" --quiet
```

### Credenciais Docker:
```bash
# Opção A: copiar do host
docker cp ~/.hermes/.env exocortex-provisioner:/opt/data/.env

# Opção B: injetar via env var
docker exec exocortex-provisioner \
  bash -c 'echo "OPENROUTER_API_KEY=$OPENROUTER_API_KEY" > /opt/data/.env'
```

---

## TROUBLESHOOTING

### Hermes não instala
- Verificar Python 3.11+: `python3 --version`
- Verificar git: `git --version`
- Tentar instalação manual: `pip install hermes-agent`

### LLM não conecta
- OAuth: limpar cache do browser e tentar novamente
- API Key: verificar formato e saldo
- Fallback: `hermes fallback add --provider openrouter`

### Drift audit falha
- Skills faltando: re-copiar de artifacts/skills/
- SOUL.md incompleto: re-executar prompt 002
- Bundle desatualizado: re-copiar exocortex-alpha.yaml

### Self-test abaixo do gate
- Re-executar prompt de checkpoint da fase
- Verificar se todas as skills respondem: `hermes skills list`
- Verificar logs: `cat logs/session_P{N}.log`
