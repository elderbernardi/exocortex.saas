1|---
2|title: Mapa de Runtime
3|created: 2026-06-05
4|updated: 2026-06-05
5|nature: knowledge
6|type: fact
7|tags: [runtime, hermes, config, tools]
8|sources: [command:hermes-tools-list, command:hermes-memory-status]
9|confidence: high
10|---
11|
12|# Mapa de runtime
13|
14|## Componentes
15|
16|- Runtime: Hermes Agent.
17|- Identidade operacional: Exocórtex.IA.
18|- Acervo Cognitivo: `/home/elder/.hermes/acervo`.
19|- Skills Exocórtex: `/home/elder/.hermes/skills/excrtx`.
20|- Config principal: `/home/elder/.hermes/config.yaml`.
21|
22|## Toolsets observados como habilitados
23|
24|- web
25|- browser
26|- terminal
27|- file
28|- code_execution
29|- vision
30|- image_gen
31|- x_search
32|- moa
33|- tts
34|- skills
35|- todo
36|- memory
37|- session_search
38|- clarify
39|- delegation
40|- cronjob
41|- messaging
42|
43|## MCPs observados
44|
45|- notebooklm: configurado e com tools habilitadas.
46|
47|## Regra
48|
49|Antes de declarar estado operacional, verificar com ferramenta. Não responder de memória sobre runtime, paths, providers, tools ou data.
50|