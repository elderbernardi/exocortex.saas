---
name: excrtx-assess-repofit
description: Evaluate whether an existing repository is suitable as a base for an
  Exocortex product. Technical feasibility, architecture, and debt analysis.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - assessment
    - architecture
    - due-diligence
    - repo
    - fit-gap
    - runtime-validation
    calibration:
    - feature_id: EX-04
      calibration_prompt: Você deve garantir que as operações e regras da skill Repo
        Fit Assessment (excrtx-assess-repofit) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se a skill de repo fit assessment tem procedimento completo
        no SKILL.md.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Repo Fit Assessment.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Repo
        Fit Assessment em seu SKILL.md estão sendo estritamente seguidos.
---
# Technical Repo Fit Assessment

Use esta skill quando o executivo pedir para estudar um sistema existente e decidir se ele atende a um propósito maior: virar engine, backend, parser, serviço, intake pipeline, viewer, ou base de produto.

O objetivo não é resumir o README. O objetivo é medir o delta entre o que o projeto diz ser e o que ele realmente entrega.

## Trigger

Ative quando o pedido tiver esta forma:

- “estude este sistema”
- “veja se os requisitos são suficientes para nosso propósito”
- “avalie se este projeto serve como base para X”
- “escreva um relatório com melhorias necessárias”
- auditoria arquitetural de um repo já existente

## Entrega esperada

A saída padrão deve conter:

1. veredito curto
2. pontos fortes reais
3. lacunas que impedem o uso para o propósito-alvo
4. riscos se acoplado como está
5. mudanças recomendadas, idealmente em P0/P1/P2
6. recomendação final de adoção, adaptação ou descarte

Se útil, grave um relatório em arquivo dentro do repo em `plans/`.

## Procedimento

### 1. Ler o contrato declarado

Inspecione primeiro os arquivos que prometem o comportamento do sistema:

- README
- purpose/design/schema/architecture docs
- package manifests e config principal
- planos e findings prévios

Pergunta central: “o que o projeto afirma ser?”

### 2. Ler o contrato executável

Depois, valide onde o comportamento realmente vive:

- entrypoints CLI/API
- pipeline principal
- adapters
- tipos de saída
- config loader
- persistência
- watcher/worker/server
- testes

Pergunta central: “o que o código realmente faz?”

### 3. Validar a trilha crítica em runtime

Não confie só na leitura estática. Sempre que possível:

- rode testes
- rode lint/build
- execute scripts de comparação ou smoke tests do caminho principal
- valide dependências opcionais que o fluxo crítico assume

Atenção: ambiente incompleto não vira regra durável. Registre apenas o efeito sobre o caminho avaliado.

### 4. Procurar quatro classes de mismatch

#### a) Claim vs implementation

Exemplo: documentação diz que um schema governa a geração, mas o código nunca o carrega.

#### b) Fallback prometido vs fallback real

Exemplo: o pipeline anuncia Vision fallback, mas o script intermediário não existe.

#### c) Contrato de produto vs contrato interno

Exemplo: o sistema foi desenhado como CLI/wiki local, mas o novo propósito exige engine de serviço com API, jobs e idempotência.

#### d) Arquitetura suficiente vs arquitetura endurecida

Exemplo: a ideia está certa, mas faltam telemetria, versionamento, retries, artifacts, qualidade e isolamento de responsabilidades.

### 5. Testar “adequação ao propósito”, não “qualidade absoluta”

A pergunta correta não é “o sistema é bom?”.
A pergunta correta é “ele é suficiente para o propósito-alvo sem impor risco estrutural?”

Um projeto pode ser bom como ferramenta local e insuficiente como engine de produção.

### 6. Estruturar a análise como delta

Use esta moldura:

- o que já serve
- o que quase serve, mas precisa endurecimento
- o que hoje impede adoção
- o que precisa virar contrato explícito

## Checklist de auditoria

### Produto e contrato

- Há um input/output canônico para o caso de uso alvo?
- O resultado principal é estruturado ou só textual?
- O sistema é centrado em CLI, arquivos locais ou serviço?
- Existe distinção entre core engine e projeções downstream?

### Pipeline

- O caminho crítico processa o documento inteiro ou só amostras/chunks parciais?
- Há agregação real entre chunks?
- Os fallbacks existem de fato?
- A escolha entre parsers é explícita e observável?

### Operação

- Há idempotência por hash ou política de reprocessamento?
- Há jobs, status, retries e timeouts?
- Há artifacts intermediários para debug?
- Há logs suficientes por etapa?

### Provenance e auditoria

- A origem externa é preservada?
- O artefato bruto local é distinguido da origem?
- A linhagem do processamento fica registrada?
- Dá para saber qual parser, qual fallback e qual LLM foram usados?

### Qualidade

- Há quality gates por tipo documental?
- Há testes nos pontos de maior risco?
- Há benchmark com corpus real do domínio?

## Heurísticas úteis

- Se o tipo principal de saída é wiki page, markdown final ou arquivo local, suspeite de acoplamento excessivo para uso como engine.
- Se a documentação promete governança declarativa, procure a leitura efetiva desses arquivos no runtime.
- Se o código tem chunking, confirme se ele agrega múltiplos chunks. Muitos sistemas “têm chunking” e processam só o primeiro chunk.
- Se o sistema promete escada de fallbacks, valide cada degrau até o fim. Um degrau ausente invalida a promessa operacional.
- Se há provenance, verifique se ela preserva origem real e não apenas caminhos locais derivados.

## Formato de veredito

Use linguagem direta:

- “suficiente como base exploratória, insuficiente como engine de produção”
- “boa fundação, contrato operacional fraco”
- “arquitetura conceitualmente correta, integração crítica quebrada”

Evite elogio genérico. Nomeie o que presta e o que falta.

## Quando a avaliação vira implementação

Se o executivo pedir para seguir do relatório para a correção, mantenha o refactor no menor corte que transforma o contrato operacional sem destruir o produto original:

1. preservar o modo existente como projeção downstream — exemplo: wiki continua funcionando
2. criar um modo engine/process-only que devolve contrato estruturado sem side effects desnecessários
3. introduzir idempotência por hash antes de expor API/worker
4. persistir jobs e revisões fora da projeção antiga — exemplo: `.docbrain/parse-jobs/`, não `wiki/`
5. tornar a política de reprocessamento explícita (`skip`, `reprocess`, `new_revision` ou equivalente)
6. validar com TDD no contrato novo e regressão no contrato antigo
7. só depois desenhar API/worker externo

Essa sequência evita o erro comum de “ligar a CLI no servidor” antes de existir contrato estável de engine.

## Artefatos de apoio

- `references/docbrain-parser-engine-case.md` — caso concreto de auditoria e hardening de um parser/document engine, incluindo processo-only, idempotência por hash e store de jobs.

## Pitfalls

- Não confundir “compila e passa testes” com “serve para o propósito-alvo”.
- Não tomar README como verdade operacional.
- Não desqualificar o sistema inteiro quando o correto é separar core promissor de contrato incompleto.
- Não registrar falhas transitórias de ambiente como se fossem limitações permanentes da arquitetura.

## Regra final

A boa análise não responde só “serve ou não serve”. Ela mostra qual refactor transforma o sistema em algo adotável.

## Procedure

Follow the steps and rules defined in this skill's body sections above.

## Verification

- [ ] Skill trigger conditions were correctly matched
- [ ] Output follows the skill's defined format and rules
- [ ] No governance violations occurred
