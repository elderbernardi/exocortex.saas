1|---
2|name: excrtx-memory-mvinstall
3|description: >-
4|  Instala um microverso empacotado verificando dependências de skills, pacotes Python/Node,
5|  e MCPs declarados no microverso.yaml. Executa hooks de pós-instalação e registra no
6|  manifest global. Ativar quando executivo pede para instalar um microverso de terceiros
7|  ou quando setup.sh provisiona microversos base com manifesto.
8|version: 1.0.0
9|category: excrtx
10|metadata:
11|  hermes:
12|    tags: [exocortex, memory, microverso, install, package, dependencies]
13|---
14|
15|# Microverso Package Installer
16|
17|> Microversos não são só arquivos. São skills, pacotes, dependências — um ecossistema.
18|
19|## Trigger
20|
21|Ativar quando:
22|- Executivo pede "instale o microverso X", "adicione o pacote Y"
23|- Setup.sh provisiona microversos base que contêm `microverso.yaml`
24|- Executivo importa um microverso de terceiros (diretório com manifesto)
25|- Comando `/xc mvinstall <path>` executado
26|
27|## Procedure
28|
29|### 1. Ler Manifesto
30|
31|Carregar `microverso.yaml` do diretório fonte. Validar schema `excrtx/v1`:
32|
33|```yaml
34|apiVersion: excrtx/v1    # obrigatório
35|kind: Microverso          # obrigatório
36|metadata:
37|  name: <slug>            # obrigatório
38|  version: <semver>       # obrigatório
39|  description: <string>   # obrigatório
40|```
41|
42|Se `microverso.yaml` ausente ou inválido → WARN + perguntar se instalar como microverso legado (sem verificação de dependências).
43|
44|### 2. Verificar Dependências de Skills
45|
46|Para cada skill em `requires.skills`:
47|- Verificar se existe em `$HERMES_HOME/skills/exocortex/<skill>/SKILL.md`
48|- Se presente → ✅
49|- Se ausente → WARN com lista de skills faltantes
50|- Oferecer: "Instalar skills faltantes?" (se disponíveis no bundle)
51|- Se não disponíveis → bloquear instalação com explicação
52|
53|### 3. Verificar Pacotes Python
54|
55|Para cada pacote em `requires.python_packages`:
56|- Verificar via `python3 -c "import <pkg>"` ou `uv pip show <pkg>`
57|- Se ausente e `uv` disponível → `uv pip install <spec>`
58|- Se ausente e `uv` não disponível → `pip install <spec>` com aviso
59|- Registrar pacotes instalados para possível rollback
60|
61|### 4. Copiar Árvore
62|
63|Copiar diretório do microverso para `$ACERVO/micro/<name>/`:
64|- Se já existe → perguntar: "Atualizar?" (merge, não overwrite)
65|- Preservar arquivos locais que o executivo tenha adicionado
66|- rsync com `--ignore-existing` para merge seguro
67|
68|### 5. Executar Hooks
69|
70|Se `hooks.post_install` definido:
71|- Validar que o path é relativo e dentro do diretório do microverso
72|- Rejeitar paths absolutos ou com `../` (segurança)
73|- Executar com timeout de 60 segundos
74|- Capturar stdout/stderr para relatório
75|
76|Se `hooks.validate` definido:
77|- Executar após post_install
78|- Se falhar → WARN mas não desfazer instalação
79|
80|### 6. Registrar no Manifest Global
81|
82|Adicionar entrada em `$ACERVO/global/_meta/microversos.yaml`:
83|
84|```yaml
85|installed:
86|  - name: <slug>
87|    version: <semver>
88|    installed_at: <ISO8601>
89|    path: micro/<slug>
90|    status: active
91|    requires_met: true|false
92|```
93|
94|### 7. Relatório
95|
96|Apresentar resumo:
97|- Microverso instalado: `<name>` v`<version>`
98|- Skills verificadas: X/Y presentes
99|- Pacotes instalados: lista
100|- Hooks executados: status
101|- Path: `$ACERVO/micro/<name>/`
102|
103|## Regras
104|
105|- Hooks executam apenas scripts dentro do diretório do microverso — sem paths absolutos
106|- Pacotes instalados via ferramentas locais (uv, pip, npm) — sem `curl | bash`
107|- Microversos de terceiros requerem aprovação do executivo (Draft-First Protocol)
108|- Se o microverso já existe com mesma versão, skip silencioso
109|- Se versão superior, oferecer upgrade
110|- Manifest global é append-only (histórico preservado)
111|
112|## Gotchas
113|
114|- `uv` pode não estar instalado — fallback para `pip` com aviso
115|- `microverso.yaml` com `apiVersion` diferente de `excrtx/v1` → rejeitar com mensagem clara
116|- Hooks com permissões de execução ausentes → `chmod +x` antes de executar
117|- rsync pode não estar disponível → fallback para `cp -rn`
118|
119|## Verificação
120|
121|- [ ] Manifesto lido e validado (schema excrtx/v1)
122|- [ ] Dependências de skills verificadas
123|- [ ] Pacotes Python/Node instalados (se necessário)
124|- [ ] Árvore copiada para $ACERVO/micro/<name>/
125|- [ ] Hooks executados com sucesso (se definidos)
126|- [ ] Registro no manifest global atualizado
127|- [ ] Relatório apresentado ao executivo
128|