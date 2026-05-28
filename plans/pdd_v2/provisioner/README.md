# Exocórtex.IA — Provisioner

Pacote de automação para instalar, configurar e executar o PDD v2 numa instância Hermes — local ou Docker.

## Como usar

### O jeito conversacional (recomendado)

Abra qualquer agente CLI (Hermes, Gemini CLI, Claude CLI) e diga:

```
Instale o Exocórtex para mim.
Leia o RUNBOOK em plans/pdd_v2/provisioner/RUNBOOK.md e siga as instruções.
```

O agente vai:
1. Detectar seu ambiente
2. Perguntar no máximo 3 coisas (modo, LLM, key)
3. Instalar tudo automaticamente
4. Reportar o progresso

### O jeito manual

```bash
# 1. Verificar pré-requisitos
bash lib/detect_environment.sh

# 2. Verificar golden image
bash lib/verify.sh --pre-provision

# 3. Copiar golden image
bash plans/pdd_v2/artifacts/setup.sh

# 4. Verificar resultado
bash lib/verify.sh --post-provision

# 5. Executar PDD manualmente
hermes chat
# (digite /exocortex-alpha para ativar o bundle, depois cole os prompts de prompts/ em ordem)
```

### Docker

```bash
# Build + start
docker compose -f docker/docker-compose.yml up -d

# Verificar
docker exec exocortex-provisioner bash lib/verify.sh --post-provision

# Executar PDD
docker exec -it exocortex-provisioner hermes chat
# (digite /exocortex-alpha para ativar o bundle)
```

## Estrutura

```
provisioner/
├── RUNBOOK.md              ← Documento executável (o agente lê isto)
├── README.md               ← Este arquivo
├── lib/
│   ├── common.sh           ← Utilitários compartilhados
│   ├── detect_environment.sh ← Detecta OS/Docker/Hermes
│   ├── verify.sh           ← Verificações estruturais
│   └── drift_audit.sh      ← Drift audit automatizado
├── prompts/
│   ├── _MASTER_CONTEXT.md  ← Contexto inicial para o Hermes
│   ├── P1_001_*.md         ← Prompts fase P1 (Identity)
│   ├── P2_006_*.md         ← Prompts fase P2 (Memory)
│   ├── P3_013_*.md         ← Prompts fase P3 (Behavior)
│   ├── P4_022_*.md         ← Prompts fase P4 (Validation)
│   └── P5_027_*.md         ← Prompt fase P5 (Production)
└── docker/
    ├── docker-compose.yml  ← Compose para instância Docker
    └── entrypoint.sh       ← Entry point do container
```

## Prompts

27 prompts atomizados, extraídos dos phase files do PDD v2. Cada prompt tem:
- Frontmatter YAML com metadata (phase, sequence, dependencies, exit_criteria)
- O prompt exato a ser enviado ao Hermes
- Comando de verificação

## Verificação

```bash
# Pré-provisioning (golden image intacta?)
bash lib/verify.sh --pre-provision

# Pós-provisioning (HERMES_HOME correto?)
bash lib/verify.sh --post-provision

# Drift audit por fase
bash lib/drift_audit.sh P1
bash lib/drift_audit.sh ALL
```
