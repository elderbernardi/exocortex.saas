# Contrato de verdade operacional do harness

Use este checklist quando uma feature do harness promete wrappers, diretórios locais, setup automatizado ou PASS em dogfood.

## Quando aplicar
- A documentação diz que um wrapper ou diretório "existe".
- O `setup.sh` promete provisionar artefatos em `~/.hermes` / `$HERMES_HOME`.
- Um probe de dogfood declara PASS/FAIL com base na presença de artefatos locais.
- A issue é de credibilidade operacional: o sistema declara uma capacidade que pode não existir de fato.

## Checklist mínimo
1. **Arquivos no repo**
   - confirme que os wrappers prometidos existem fisicamente no repositório
   - se não existem, corrigir código antes de mexer em documentação

2. **Provisionamento**
   - confirme que o `setup.sh` copia os wrappers para o destino correto
   - crie também os diretórios operacionais esperados pela feature
   - aplique permissões executáveis quando o contrato da feature depender disso

3. **Fonte de verdade de paths**
   - probes e wrappers devem usar `$HERMES_HOME` ou helper central equivalente
   - evitar `Path.home() / ".hermes"` quando a feature precisa ser testável em ambiente temporário/provisionado

4. **Teste isolado**
   - crie ou expanda teste que injeta `HERMES_HOME` temporário
   - valide tanto presença de wrappers quanto comportamento do probe

5. **Smoke real do artefato provisionado**
   - execute o wrapper instalado no destino real de `HERMES_HOME`, não só o script do repo
   - confirme geração de artefatos esperados (`runs/`, `events/`, `reviews/` ou equivalentes)

6. **Dogfood real-agent**
   - rode a feature específica em modo real-agent
   - só declare correção concluída quando o resultado de PASS estiver ancorado em evidência concreta

7. **Documentação**
   - alinhe `FEATURES.md`, skill operacional e qualquer referência que prometa a capacidade
   - documentação nunca deve permanecer mais otimista que o runtime

## Pitfalls recorrentes
- Corrigir só o markdown e esquecer o arquivo físico.
- Criar o wrapper no repo mas não provisionar no `setup.sh`.
- Probe usando `Path.home()` e quebrando testes com `HERMES_HOME` temporário.
- Considerar um timeout de smoke adjacente como blocker da issue, mesmo quando a feature-alvo já foi provisionada e validada separadamente.
- Declarar PASS sem executar o wrapper provisionado no destino real.

## Evidência que vale
- teste automatizado verde cobrindo `HERMES_HOME` temporário
- smoke do wrapper provisionado com artefatos gerados
- resultado dogfood `PASS` da feature específica
- leitura do artefato final (`summary.json`, `review.md`, `result.json` ou equivalente)

## Caso-base capturado
Issue EX-33 / #46: wrappers ausentes, probe apontando para `Path.home()`, setup sem provisionar diretório de aprendizado. A correção exigiu alinhar quatro camadas: arquivos reais no repo, `setup.sh`, runtime em `~/.hermes`, e dogfood real-agent.