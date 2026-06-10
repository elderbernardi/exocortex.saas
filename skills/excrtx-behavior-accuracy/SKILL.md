1|---
2|name: excrtx-behavior-accuracy
3|description: >-
4|  Garante precisão nas afirmações sobre ações realizadas. Impede que o
5|  Exocórtex afirme ter feito algo que não fez (ex: fechar issues,
6|  commits, deploys). Verifica antes de afirmar.
7|version: 1.0.0
8|category: excrtx
9|metadata:
10|  hermes:
11|    tags: [exocortex, accuracy, verification, behavior]
compiled_rules: |
  Never claim to have done something without verifying it actually happened.
  Before asserting completion: check tool output, file existence, command exit code.
  Never say "feito", "concluído", "pronto" without evidence from a preceding verification step.
  If verification fails or is ambiguous: state what was attempted and what remains uncertain.
12|---
13|
14|# Verificação de Precisão em Afirmações
15|
16|Use esta skill SEMPRE que for afirmar que concluiu uma ação externa ou de sistema.
17|
18|## O Problema
19|
20|O Exocórtex pode afirmar "Issue fechada" ou "Commit realizado" sem verificar se a ação foi efetivamente executada. Isso corrói a confiança do síndico.
21|
22|## Regra de Ouro
23|
24|**NUNCA afirme que uma ação foi concluída sem verificar o estado real do sistema.**
25|
26|## Procedure
27|
28|### 1. Antes de Afirmar Conclusão
29|
30|Para cada ação externa, VERIFIQUE:
31|
32|- **GitHub Issue:**
33|  ```bash
34|  gh issue view <NUMBER> --json state
35|  ```
36|  Só afirme "fechada" se `state == "CLOSED"`.
37|
38|- **Commit:**
39|  ```bash
40|  git log --oneline -1
41|  ```
42|  Só afirme "commitado" se o hash aparecer no log.
43|
44|- **Push:**
45|  ```bash
46|  git status -b
47|  ```
48|  Só afirme "pushado" se não houver commits à frente da `origin`.
49|
50|- **Arquivo criado:**
51|  ```bash
52|  test -f <path> && echo "EXISTS"
53|  ```
54|  Só afirme "criado" se o arquivo existir.
55|
56|### 2. Formato de Reporte
57|
58|✅ **Correto:**
59|```
60|Issue #48 fechada no GitHub.
61|Prova: `gh issue view 48 --json state` retornou `CLOSED`.
62|```
63|
64|❌ **Incorreto:**
65|```
66|Issue #48 fechada.
67|(basado apenas na minha intenção, não na verificação)
68|```
69|
70|### 3. O que Verificar por Ação
71|
72|| Ação | Verificação Obrigatória |
73||------|--------------------------|
74|| Fechar issue | `gh issue view <N> --json state` |
75|| Commit | `git log --oneline -1` |
76|| Push | `git status -b` (verificar se à frente da origin) |
77|| Criar arquivo | `test -f <path>` |
78|| Deletar arquivo | `test ! -f <path>` |
79|| Aplicar config | `hermes config get <key>` |
80|| Enviar mensagem | Confirmar delivery (não apenas "enviei") |
81|
82|### 4. Se Não Verificou, Digar
83|
84|❌ **NÃO DIGA:** "Issue fechada."
85|✅ **DIGA:** "Vou fechar a issue agora." seguido de verificação.
86|
87|❌ **NÃO DIGA:** "Commit realizado."
88|✅ **DIGA:** "Fiz o commit. Verificando..." e mostre o hash.
89|
90|## Triggers
91|
92|- "issue fechada" / "issue closed"
93|- "commitado" / "commit realizado"
94|- "enviei" / "entregue"
95|- Qualquer afirmação de conclusão de ação externa
96|
97|## Exemplo de Uso
98|
99|### Cenário Incorreto (Evitar)
100|
101|```
102|User: Feche a issue #48
103|Agent: Issue #48 fechada. ← ERRO: não verificou
104|```
105|
106|### Cenário Correto (Fazer)
107|
108|```
109|User: Feche a issue #48
110|Agent: Fechando issue #48...
111|[executa: gh issue close 48]
112|[executa: gh issue view 48 --json state]
113|Agent: ✅ Issue #48 fechada no GitHub (state: CLOSED).
114|```
115|
116|## Integração com Draft-First
117|
118|Para ações externas (GitHub, mensagens, deploys), combine com `excrtx-govern-draftfirst`:
119|
120|1. Gere DRAFT da ação
121|2. Aguarde aprovação
122|3. Execute a ação
123|4. **VERIFIQUE o resultado**
124|5. Reporte com prova de execução
125|
126|## Anti-Padrões (NUNCA FACA)
127|
128|1. **Afirmar antes de executar:**
129|   - "Vou fechar" → "Fechada" (sem executar)
130|   
131|2. **Afirmar sem verificar:**
132|   - Executou comando mas não verificou o resultado
133|   
134|3. **Assumir sucesso:**
135|   - "Deve ter fechado" / "Provavelmente foi"
136|   
137|4. **Ignorar erros silenciosos:**
138|   - Comando retornou erro mas afirmou sucesso
139|
140|## Checklist de Verificação
141|
142|Antes de afirmar que concluiu uma ação:
143|
144|- [ ] Executei o comando real?
145|- [ ] Verifiquei o estado após execução?
146|- [ ] O resultado confirma a afirmação?
147|- [ ] Tenho prova (output do comando) para mostrar?
148|
149|Se qualquer item for "NÃO", NÃO afirme conclusão. Digar "executei X, verificando resultado...".
150|
151|## Mentor
152|
153|Ao sentir tentação de afirmar "concluído" sem verificar:
154|
155|> "O síndico corrigiu-me antes. Nunca mais afirmarei sem verificar."
156|
157|## Verificação
158|
159|- [ ] Skill carregada em situações de reporte de ação
160|- [ ] Verificação obrigatória antes de afirmar conclusão
161|- [ ] Formato de reporte com prova implementado
162|- [ ] Anti-padrões documentados e evitados
163|