# ADR-024: Instalador v2 sobre Hermes pré-existente

**Status:** Accepted  
**Data:** 2026-07-30  
**Supersede:** ADR-012 no que trata da UX e da orquestração da instalação

## Contexto

O instalador anterior acumulava responsabilidades de bootstrap do sistema,
instalação do Hermes, configuração de providers, provisionamento de integrações,
verificação estrutural, pós-provisionamento e calibração comportamental extensa.
O resultado era lento, difícil de reproduzir e propenso a falsos positivos: o
catálogo de dogfood repetia invariantes que arquivos e comandos determinísticos já
podiam provar.

O Hermes é o runtime. O Exocórtex é o harness de identidade, memória, vetores,
profiles, skills e Acervo instalado sobre esse runtime. Misturar as duas instalações
impede que cada produto tenha ciclo de vida e autoridade claros.

## Decisão

1. Hermes instalado e `hermes config check` aprovado são pré-condições.
2. O instalador Exocórtex não instala pacotes do sistema, Python, Node ou Hermes.
3. A interface canônica tem três comandos: `plan`, `apply` e `verify`.
4. `core` instala o harness; `full` acrescenta NotebookLM, Hindsight, Firecrawl e
   WebUI. Dependências seguem o manifesto orientado a capacidades da ADR-025.
5. Serviços do profile `full` são obrigatórios por default. Degradação exige
   `--allow-degraded-services` e permanece visível no relatório.
6. Toda mutação ocorre sob lock e snapshot dos arquivos gerenciados.
7. A instalação preserva um `SOUL.md` já identificado como Exocórtex, incluindo o
   onboarding, e recompila apenas o bloco de regras.
8. Verificação estrutural é determinística e precede qualquer chamada a LLM.
9. Aceitação comportamental usa três cenários reais: identidade, vetor Evolução e
   Draft-First. Ela não injeta correções e não é descrita como treinamento.
10. O catálogo EX completo pertence a CI, release qualification e desenvolvimento
    do harness, não ao caminho normal de instalação.
11. O instalador produz estado JSON, logs sanitizados por estágio e snapshot local.

## Consequências

### Positivas

- instalação menor, previsível e auditável;
- consumo fixo de três turnos vivos, com opção explícita de zero turnos;
- falhas de infraestrutura deixam de aparecer como sucesso degradado silencioso;
- reexecução segura sobre um Hermes e Macroverso vivos;
- separação entre defeito do pacote, defeito do ambiente e drift comportamental;
- automação headless usa o mesmo orquestrador do fluxo interativo.

### Custos

- o operador precisa instalar e configurar Hermes antes;
- `full` exige Docker/Compose e pode baixar imagens grandes;
- integrações não essenciais ao harness deixam de ser acopladas ao setup;
- testes antigos que verificavam a UX monolítica deixam de representar o contrato.

## Verificação

```bash
python3 -m py_compile \
  scripts/exocortex_install.py \
  scripts/verify_exocortex_install.py \
  scripts/verify_exocortex_behavior.py
bash -n install.sh setup.sh setup/step-07-install-identity.sh
python3 -m pytest tests/test_installer_v2.py
python3 scripts/exocortex_install.py plan --profile core
```

A aceitação viva só deve ser executada depois dos gates acima:

```bash
python3 scripts/verify_exocortex_behavior.py
```
