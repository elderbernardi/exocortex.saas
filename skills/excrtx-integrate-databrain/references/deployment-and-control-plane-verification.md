> **Escopo operacional vigente:** consultar `databrain_execution_status` e o runbook DataBrain `ops/EXECUTION_CONTROL.md` antes de usar estados/versões históricos deste documento. Gates são locais via `pb heavy`; o perfil factual atual é `semantic-v1`. Instruções de segurança, publicação ampla e autorização deste documento continuam aplicáveis.

# DataBrain — verificação de deploy e plano de controle

Use este roteiro para distinguir estados independentes: Cockpit implantado, API saudável, automação ativa, executor Oracle seguro e ponte apta a operar.

## 1. Provar o deploy do Cockpit

Validar separadamente:

1. container `running` e healthcheck `healthy`;
2. `/health` confirma PostgreSQL e DuckDB;
3. `/cockpit/ui/login` entrega HTML;
4. `/cockpit/runs` entrega histórico;
5. rota protegida sem credencial responde `401`;
6. a imagem contém `dist/api/cockpit`.

Não inferir deploy pela porta aberta ou pelo código do checkout. Produção roda a imagem implantada; o checkout pode estar em outro SHA.

## 2. Identificar o scheduler canônico

Não assumir que o scheduler interno do container é a automação de produção. Verificar as duas camadas:

- host: `databrain-ingest.timer`, `databrain-backup.timer` e `databrain-net.service`;
- container: `DATABRAIN_SCHEDULER_ENABLED` e log do `SchedulerService`.

No desenho validado, o timer systemd do host é canônico e o scheduler interno fica desligado para evitar duplicidade. Reportar:

- estado `active/enabled` dos timers;
- próximo trigger;
- scheduler interno efetivo;
- VPN inativa fora da janela de extração.

Nunca ativar ambos por analogia.

## 3. Rotear operações pelo executor correto

### Sem Oracle

Estágios locais usam o CLI oficial dentro de `databrain-databrain-1`:

- `dry_run`;
- `ingest_inbox`;
- `cold`;
- `hot`;
- `judge`;
- `publish`.

### Com Oracle

Toda operação contendo `--fetch-oracle` deve passar por:

```text
/srv/databrain/ops/ingest-run.sh
```

O wrapper governa VPN exclusiva, `flock`, preflight Oracle real, watchdog, liberação antecipada e watermark. `docker exec` direto é incorreto para pulls Oracle.

## 4. Verificar a ponte sem efeito externo

Sequência mínima:

1. self-test do MCP;
2. handshake do Hermes e contagem de tools;
3. saúde, timers e histórico saneado;
4. `dry_run` por receipt;
5. aguardar `succeeded` e exit code `0`;
6. inspecionar log persistido;
7. teste negativo: `publish` sem `approval_ref` deve ser recusado;
8. confirmar que operações Oracle resolvem para o wrapper do host.

`started` nunca prova sucesso. Uma unit transitória coletada pode depois aparecer como `LoadState=not-found`; use `Result`, `ExecMainCode`, `ExecMainStatus` e o log.

## 5. Fronteira de dados

Cockpit é fonte operacional, não payload confiável por padrão. Antes de responder via MCP:

- remover `config_snapshot` integralmente;
- redigir recursivamente password, secret, token, API/service key, private key, credential e database URL;
- testar o JSON serializado contra marcadores sensíveis;
- devolver apenas campos operacionais necessários.

Se a rota upstream expõe snapshot sem autenticação, proteger o adaptador e registrar hardening upstream. Nunca repetir valores sensíveis.

## 6. Recovery e armadilhas

- `publish --retry-failed` não é recuperação seletiva na imagem validada: cai em publicação completa. Não expor `publish_retry` até existir implementação real.
- Falha incremental normalmente se recupera repetindo a janela: o watermark não avança após falha.
- Backfill `--resume` é distinto de `--reset`; reset exige governança reforçada.
- Não testar `backfill-cli.js --help` sem confirmar suporte: versões observadas podem iniciar o fluxo em vez de mostrar ajuda.
- Backups podem existir sem runbook de restore. Não automatizar restore antes de validar extração temporária, integridade e procedimento aprovado.
- Nunca usar checkout `databrain.clean.RETIRED-*`.

## 7. Isolamento de mudanças

Quando o checkout ativo contém trabalho alheio:

- criar worktree limpo da branch de destino;
- copiar só os arquivos da ponte;
- testar e commitar no worktree;
- manter contrato do harness em branch própria quando pertencer a outro repositório;
- não fazer push sem aprovação;
- só remover cópias após confirmar commit e ausência de trabalho alheio.
