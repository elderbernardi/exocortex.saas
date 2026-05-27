# brutalist — Dados Pesados / Dashboards

## Quando Ativar

Use este sub-skill quando o output visual apresentar:
- Métricas, dashboards, cockpit executivo, BI, KPIs, tabelas e rankings.
- Visualização de dados, monitoramento, alertas, logs, sistemas operacionais.
- Interfaces data-heavy onde densidade, contraste e leitura rápida importam mais que decoração.

## Direção Estética

Brutalist aqui não significa feio. Significa:
- Estrutura explícita.
- Tipografia forte.
- Alto contraste.
- Hierarquia mecânica.
- Pouca ornamentação.
- Dados como material visual principal.

Referência mental: Swiss typography + terminal financeiro + poster industrial + interface operacional.

## Swiss Typography

Use tipografia como arquitetura:
- Sans grotesk/neo-grotesk para UI e títulos.
- Mono para números, labels técnicos, timestamps, deltas.
- Escala clara: title, section, metric, label, annotation.
- Alinhamento rígido; baseline consistente.
- Números tabulares: `font-variant-numeric: tabular-nums`.
- Uppercase seletivo para labels, nunca em parágrafos longos.

CSS base:

```css
.metric {
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.04em;
}
.label {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
}
```

## Raw Structure

Mostre a estrutura em vez de escondê-la:
- Grids visíveis, linhas duras, divisórias, coordenadas, colunas numeradas se útil.
- Cards podem parecer módulos industriais, não caixas SaaS arredondadas.
- Bordas 1-2px, fundos sólidos, poucos raios (`0`, `2px`, `4px`).
- Espaçamento compacto, com respiro apenas em blocos de decisão.
- Tabelas densas com zebra sutil ou linhas fortes.

## High Contrast

Contraste é funcional:
- Fundo quase preto + branco/quase branco, ou branco cru + preto.
- Accent único e agressivo para estado/ação: vermelho, amarelo, verde ácido, ciano elétrico.
- Cor semântica deve ser consistente: risco, alta, queda, alerta.
- Nunca use cinza claro sobre fundo claro para texto crítico.
- Botões e estados ativos devem ser inequívocos.

## Mechanical Visual Language

Use linguagem visual de máquina:
- IDs, timestamps, coordenadas, status chips, barras de progresso lineares.
- Sparklines, heatmaps, mini-bars, gauges retangulares, histograms.
- Setas/deltas com sinais explícitos: `+12.4%`, `−8.1%`, `▲`, `▼`.
- Blocos de alerta como placas: `CRITICAL`, `WATCH`, `STABLE`.
- Microcopy objetiva: verbo + objeto + estado.

## Dashboard Composition

Uma tela data-heavy premium deve ter:
1. Command header: título, período, filtros, estado de atualização.
2. KPI strip: 4-8 métricas principais com deltas e contexto.
3. Main analytical region: gráfico/tabela dominante.
4. Secondary modules: breakdowns, alerts, cohorts, ranking.
5. Decision footer ou action rail: próximos movimentos ou exceções.

## Data Visualization Rules

- Visualize comparação e tendência, não enfeite.
- Labels devem ser legíveis sem hover quando o dado é crítico.
- Escalas e unidades sempre claras.
- Ordenação deve contar uma história: maior risco, maior impacto, maior variação.
- Evite pie charts para muitos segmentos.
- Use small multiples quando comparar categorias.
- Use cor para exceção, não para carnaval.

## Anti-Slop Dashboard

Remova:
- Cards SaaS genéricos com ícones circulares e sombras suaves.
- Gráficos coloridos sem legenda clara.
- Métricas sem unidade, período ou delta.
- Tabelas com padding excessivo e pouca densidade.
- “Insights” genéricos que repetem o dado.
- Paletas brandas que escondem risco.
- Layout sem prioridade decisória.

## CSS Base

```css
.dashboard {
  background: #080808;
  color: #f2f2ea;
  font-family: Inter, Helvetica Neue, Arial, sans-serif;
}
.module {
  border: 1px solid rgba(242, 242, 234, 0.24);
  border-radius: 2px;
  background: #10100e;
}
.accent-critical { color: #ff3b30; }
.accent-watch { color: #f5d90a; }
.accent-good { color: #7cff00; }
```

## Pre-Flight Checklist

Antes de entregar:
- [ ] KPIs têm unidade, período e delta.
- [ ] Hierarquia decisória evidente.
- [ ] Tipografia numérica usa tabular nums.
- [ ] Contraste forte para texto e ação.
- [ ] Cor usada para estado/exceção.
- [ ] Estrutura grid é intencional e densa.
- [ ] Nenhum gráfico decorativo sem propósito.
- [ ] Linguagem visual mecânica, não SaaS genérica.
