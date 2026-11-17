> **Escopo operacional vigente:** consultar `databrain_execution_status` e o runbook DataBrain `ops/EXECUTION_CONTROL.md` antes de usar estados/versões históricos deste documento. Gates são locais via `pb heavy`; o perfil factual atual é `semantic-v1`. Instruções de segurança, publicação ampla e autorização deste documento continuam aplicáveis.

# Cockpit do gestor via Tailscale — padrão seguro

Use este procedimento quando o executivo pedir acesso remoto ao Cockpit DataBrain.

## Topologia-alvo

```text
Tailnet HTTPS (Tailscale Serve)
  → proxy allowlisted em 127.0.0.1:<porta-proxy>
    → DataBrain em 127.0.0.1:8000
```

Nunca altere o bind do DataBrain para `0.0.0.0`. Nunca use Tailscale Funnel para esse caso.

## Ordem obrigatória

1. Confirmar saúde do DataBrain, IP Tailscale, MagicDNS, listeners e configuração atual de `tailscale serve`.
2. Auditar autenticação **antes de criar exposição**:
   - `COCKPIT_ADMIN_EMAIL` presente;
   - `COCKPIT_ADMIN_PASSWORD` presente, não vazia e diferente do fallback de desenvolvimento;
   - `JWT_SECRET` presente, não vazio e diferente do fallback de desenvolvimento.
3. Se qualquer credencial estiver ausente/default:
   - não ativar Serve;
   - apresentar DRAFT complementar para gerar credenciais, alterar o deploy e reiniciar o container;
   - nunca imprimir valores existentes durante a auditoria.
4. Escolher e registrar o perfil de exposição aprovado:
   - **mínimo (default):** `/cockpit/ui*`, `/cockpit/quarantine*`, `/cockpit/campanhas*`, `/cockpit/grupos-empresariais*` e `/public/cockpit.css`;
   - **gerencial ampliado:** todas as rotas de negócio já implantadas, desde que enumeradas explicitamente, limitadas aos métodos documentados e protegidas por sessão real. Consulte “Perfil gerencial ampliado” abaixo.
5. Criar proxy loopback deny-by-default. Em ambos os perfis, bloquear `/health`, `/api/docs`, `/api/docs-json`, login JSON independente e qualquer rota futura não revisada. No perfil mínimo, bloquear também `/cockpit/runs*`; no ampliado, runs são somente leitura e recebem autenticação adicional no proxy porque o upstream implantado pode deixá-las públicas e carregar `config_snapshot`.
6. O proxy deve aceitar como autenticada apenas uma sessão observada após login válido no upstream. A mera presença de um cookie `session` não basta para páginas SSR ou APIs de negócio.
7. Validar localmente:
   - listener somente em loopback;
   - login e CSS acessíveis;
   - dashboard sem sessão redireciona para login;
   - cookie forjado não autentica;
   - rotas bloqueadas retornam 404;
   - sessão real abre dashboard, campanhas e grupos.
8. Só depois da validação e da aprovação Draft-First, ativar o mapeamento exato com `sudo -n tailscale serve --bg --yes http://127.0.0.1:<porta-proxy>`. Em hosts onde o operador Tailscale não foi delegado ao usuário, a chamada sem `sudo` será recusada; não altere o operador global só para contornar isso.
9. Verificar pela URL MagicDNS HTTPS — inclusive login real e páginas protegidas — e confirmar:
   - `tailscale serve status` mostra `(tailnet only)` e o proxy loopback esperado;
   - certificado TLS válido para o MagicDNS;
   - rotas técnicas continuam `404` mesmo com sessão válida;
   - backend e proxy permanecem saudáveis;
   - nenhuma porta `0.0.0.0`/`[::]` foi criada para DataBrain ou proxy.
10. Não use `tailscale funnel status` vazio como único gate: em algumas versões ele espelha a configuração Serve. A evidência canônica de ausência de Funnel é a classificação explícita `(tailnet only)` em `tailscale serve status`, combinada com o mapeamento criado por `tailscale serve` — nunca por `tailscale funnel`.
11. Entregue a credencial sem registrá-la em logs. Se o canal mascarar segredos no texto, gere um artefato local `0600`, verifique-o sem imprimir o valor, entregue-o ao próprio executivo e programe remoção curta. Nunca deixe uma segunda cópia transitória depois da entrega.
12. Registrar comando de parada: `sudo tailscale serve --https=443 off`; depois parar/desabilitar o proxy se a borda não for mais necessária.

## Perfil gerencial ampliado

Use somente após aprovação explícita do executivo para ampliar a borda. Antes de editar o proxy, leia o OpenAPI implantado e confirme cada rota diretamente no upstream com cookie obtido pelo login UI — nunca derive a allowlist apenas do checkout.

Rotas de negócio observadas e método esperado:

- `GET /api/auth/me`;
- `GET /api/mgmt/team-overview`;
- `GET /api/mgmt/carteira`;
- `GET /api/mgmt/funnels`;
- `GET /api/mgmt/campaigns-effectiveness`;
- `GET /api/mgmt/vendedores` e `GET /api/mgmt/vendedores/{id}`;
- `GET /api/mgmt/lookups/{kind}`, restringindo `kind` aos valores documentados;
- `GET /cockpit/runs` e `GET /cockpit/runs/{id}`.

Regras:

1. Enumerar rotas estáticas; para parâmetros, aceitar exatamente um segmento e validar enums conhecidos. Não liberar prefixos amplos como `/api/mgmt/*`.
2. Exigir sessão conhecida pelo proxy em todas as rotas acima. Em runs, esta proteção compensa a ausência de guard no upstream.
3. Limitar runs e APIs gerenciais a leitura; método diferente retorna `404`.
4. Reiniciar o proxy invalida o conjunto de sessões observadas: avisar que será necessário novo login.
5. Fazer backup antes da alteração e preparar rollback automático se start, login ou qualquer teste falhar.
6. Validar pela URL HTTPS final: sem sessão, cookie forjado, sessão real, cada rota permitida, cada rota técnica bloqueada, método indevido, TLS, listeners, saúde e `(tailnet only)`.
7. **API disponível não significa funcionalidade visível na interface.** Depois dos `200`, inspecionar links/scripts do HTML e navegar pelas telas. Se o backend expõe APIs gerenciais mas o Cockpit não possui páginas para elas, relatar como limitação de frontend; não declarar que a função está disponível visualmente.

## Particularidades observadas

- O login UI do upstream pode variar entre versões: há imagens que respondem `200 + Location` e outras que respondem `201 + Set-Cookie` sem redirect. Não fixe o teste em `status == 200` nem em URL final após o POST. O gate robusto é: resposta `< 400`, cookie `session` emitido com formato JWT e acesso `200` a uma página protegida; o proxy só normaliza `200 + Location` para `302` quando esse cabeçalho existir.
- Reiniciar o proxy zera o conjunto de fingerprints de sessões reconhecidas, mesmo que o JWT ainda seja válido no upstream. Sempre avise o executivo para autenticar novamente depois de restart ou deploy do proxy.
- Em units systemd de usuário, diretivas de capability/hardening podem não ser suportadas pelo ambiente. Comece com hardening compatível, valide o start e adicione proteções incrementalmente; não transforme falha de unit em exposição direta improvisada.
- Arquivos `.env` e alterações/restarts de deploy são efeitos externos/operacionais separados da ativação do Tailscale Serve. Se o DRAFT original não incluiu rotação de credenciais, apresente um DRAFT complementar.

## Gate de conclusão

Só declarar o Cockpit publicado quando houver evidência de todos os itens:

- DataBrain healthy;
- credenciais não-default configuradas;
- proxy active em loopback;
- sessão real validada;
- rotas técnicas bloqueadas;
- Serve HTTPS ativo e classificado como `(tailnet only)`;
- configuração criada por `tailscale serve`, sem uso de `tailscale funnel`;
- URL final acessível pelo MagicDNS.
