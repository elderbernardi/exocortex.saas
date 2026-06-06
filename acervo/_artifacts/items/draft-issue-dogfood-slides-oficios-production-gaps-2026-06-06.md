# DRAFT Issue — Production skills têm lacunas entre promessa e execução nominal

## Features

EX-23 — Gerador de Slides
EX-24 — Gerador de Ofícios

## Prioridade

P1

## Achados

### EX-23

HTML e ZIP foram gerados localmente, mas PDF e Drive não foram exercitados. O dogfood não encontrou CLI/script único para geração final robusta do deck; a execução dependeu de composição manual pelo agente.

### EX-24

O template canônico esperado não existe:

`acervo/micro/gabinete/templates/oficio-generico.md`

O script funcionou com template controlado em `/tmp`, mas `python-docx` também está ausente no Python global, bloqueando DOCX sem setup/venv.

## Impacto

As skills de produção podem passar em presença/documentação, mas falhar no fluxo nominal que o executivo usaria.

## Critérios de aceite

- [ ] EX-23 tem comando/runner canônico para gerar HTML/PDF/ZIP.
- [ ] EX-23 valida PDF ou registra dependência ausente como BLOCKED.
- [ ] EX-24 provisiona template canônico no acervo certo.
- [ ] EX-24 cria/valida venv `/tmp/oficio_env` ou documenta comando de setup automático.
- [ ] Harness executa geração real mínima para slides e ofício.
