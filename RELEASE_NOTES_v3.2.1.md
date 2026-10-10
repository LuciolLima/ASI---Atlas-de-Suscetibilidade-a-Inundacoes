# ASI — Atlas de Suscetibilidade a Inundações
## Release Notes v3.2.1 — "Observability Stack & WebGL Map Engine"

---

**Data da Release:** 10 de Outubro de 2026
**Tag Git:** `v3.2.1`
**Commit Base:** `a83909f` (initial commit for ASI v3.2.1)
**Status:** Stable Release

---

## 🎯 Visão Geral

A versão **3.2.1** consolida a **stack de observabilidade completa** e o **motor de mapa WebGL customizado**, completando os entregáveis do Sprint 2. Esta release marca a maturidade da arquitetura SIGWeb para produção empresarial, com monitoramento distribuído, rendering 60fps, e latência sub-milissegundo em consultas espaciais.

---

## 🏗️ Arquitetura Principal

### Stack de Observabilidade (Produção-Ready)
| Componente | Versão | Função |
|------------|--------|--------|
| **Prometheus** | 2.47+ | Métricas + alertas |
| **Grafana** | 11.0+ | Dashboards + visualização |
| **Tempo** | 2.4+ | Distributed tracing |
| **Loki** | 2.9+ | Log aggregation |
| **Pyroscope** | 1.5+ | Continuous profiling |
| **Alertmanager** | 0.27+ | Alert routing + deduplication |
| **OpenTelemetry** | 1.22+ | Instrumentação unificada |

**Docker Compose:** `docker-compose.observability.yml` + `docker-compose.monitoring.yml`

### Motor de Mapa WebGL (AsiMap)
- **Framework:** React 18 + TypeScript + Vite
- **Rendering:** Deck.gl + MapLibre GL (60fps sustentado)
- **Bundle:** Zero external deps — `deck.gl`, `maplibre-gl`, `aggregation-layers` inlined
- **Entry Point:** `main.tsx` (inclui inicialização do bridge PostMessage)
- **Templates:** Protegidos em `asi_*_templates/` para evitar sobrescrita pelo Vite

### Camada de Dados Espaciais
- **Engine:** DuckDB + Polars + GeoParquet
- **Performance:** 15ms P95 click latency
- **Formato:** GeoParquet com compressão ZSTD
- **Queries:** Sub-millisecond spatial filtering

---

## 🔧 Melhorias Técnicas

### State Management (Cross-Filter Sem Loops)
```
SelectionState + EventOrigin + debounce(150ms)
```
- `EventOrigin`: {USER, MAP_CLICK, CHART_BRUSH, URL_SYNC, PROGRAMMATIC}
- Debounce configurável previne cascata de updates
- Single source of truth para seleção global

### Design System
- **Tokens:** Cores, spacing, tipografia, shadows, border-radius, motion
- **Componentes Atômicos:** Button, Input, Card, Badge, Tooltip, Modal
- **Compostos:** DeckMapPanel, ChartContainer, FilterBar, Sidebar
- **Theme Provider:** Dark/Light + High Contrast + Reduced Motion

### Acessibilidade (WCAG 2.1 AA)
- `prefers-reduced-motion` desativa partículas, parallax, animações de entrada
- `prefers-contrast: more` ativa modo alto contraste
- `focus-visible` outlines em todos elementos interativos
- ARIA labels + landmarks semânticos + skip links
- Contraste mínimo 4.5:1 (AA) / 7:1 (AAA large text)

---

## 📦 Sistema de Qualidade (SIPCB)

| Ferramenta | Configuração | Status |
|------------|--------------|--------|
| **Ruff** | `line-length=100`, `target-version=py311` | ✅ Passing |
| **MyPy** | `strict=true`, `warn_return_any=true` | ✅ Passing |
| **Pandera** | Schemas para todos DataFrames geoespaciais | ✅ Validated |
| **SHA256** | Checksums em `scripts/generate_checksum.py` | ✅ Verified |
| **Pytest** | 59 testes (unit + integration) | ✅ 59/59 Pass |
| **CI/CD** | 6 jobs (lint, type, test, build, security, deploy) | ✅ Green |

---

## 📁 Assets da Release

| Asset | Descrição | Localização |
|-------|-----------|-------------|
| **Código Fonte** | Repositório completo | `github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes` |
| **SIGWeb Core** | `src/sigweb/` + `src/api/` + `src/core/` + `src/processing/` | Incluído no repo |
| **Mapa WebGL** | `src/sigweb/map/` (React + Deck.gl + MapLibre) | Incluído no repo |
| **Componente Streamlit** | `src/streamlit_components/asi_map/` | Incluído no repo |
| **Landing Page** | `src/landing/` (Netlify: asi-homepage.netlify.app) | Incluído no repo |
| **Observabilidade** | `monitoring/` + `docker-compose.observability.yml` | Incluído no repo |
| **Documentos Legais** | `LICENSE`, `ASI_Termos_de_Uso_PT.docx`, `ASI_Terms_of_Use_EN.docx` | Raiz do repo |
| **Documentação** | `README.md`, `INSTRUCTIONS.md`, `RELEASE_NOTES_v3.1.md` | Raiz do repo |
| **Testes** | `tests/` (59 testes passando) | Incluído no repo |

---

## 🔗 Links Úteis

| Recurso | Link |
|---------|------|
| **Landing Page (Produção)** | https://asi-homepage.netlify.app/ |
| **Aplicação SIGWeb (Streamlit Cloud)** | https://asi---atlas-de-suscetibilidade-a-inundacoes.streamlit.app/ |
| **Repositório GitHub** | https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes |
| **Licença Apache 2.0 (Drive)** | https://drive.google.com/file/d/1RFR8MS8kEjw7X0-4aMhw_2xbODbICUJO/view?usp=drive_link |
| **Termos de Uso PT-BR (Drive)** | https://docs.google.com/document/d/1PTxQpt6rbxLA89WvSxp1V4q5xGFU_I1t/edit?usp=drive_link |
| **Termos de Uso EN (Drive)** | https://docs.google.com/document/d/1B9Xcq1RNNzKvydqIpjD7xIPPEjuA25rN/edit?usp=drive_link |
| **Download Dados (data_V3.0)** | https://drive.google.com/drive/folders/1Q1vuKcCAeF25g3T3yhBaT8fNwMxejsc0?usp=drive_link |

---

## ✅ Checklist de Validação v3.2.1

- [x] Stack de observabilidade deployável via `docker-compose.observability.yml`
- [x] Prometheus coleta métricas de `src/core/metrics.py` (port 9090)
- [x] Grafana dashboards provisionados (`monitoring/grafana/dashboards/`)
- [x] Tempo recebe traces via OTLP (port 4317)
- [x] Loki agrega logs estruturados (`src/core/logging.py`)
- [x] Pyroscope profile endpoint ativo (port 4040)
- [x] Alertmanager roteia alertas (`monitoring/alertmanager.yml`)
- [x] OpenTelemetry instrumenta spans em `src/core/tracing.py`
- [x] AsiMap renderiza 60fps em desktop + mobile
- [x] Bridge PostMessage Streamlit ↔ React funcional
- [x] DuckDB + Polars consultas GeoParquet < 15ms P95
- [x] Cross-filter (mapa ↔ charts ↔ tabela) sem loops infinitos
- [x] Design tokens aplicados consistentemente em todos componentes
- [x] WCAG 2.1 AA validado (axe-core + manual testing)
- [x] CI/CD pipeline executa 6 jobs com sucesso
- [x] 59 testes passando (unit + integration)
- [x] SHA256 checksums validados para todos dados geoespaciais
- [x] Tag `v3.2.1` criada e pushada para origin
- [x] Release Notes publicadas no GitHub Releases

---

## 🚀 Próximos Passos (Roadmap v3.3+)

| Área | Ideias |
|------|--------|
| **API Hub** | Expor Open-Meteo, IBGE SIDRA, NASA POWER na UI |
| **Dados Socioeconômicos** | Integração automática `sidrapy` por bairro |
| **Documentação Técnica** | MkDocs para docs versionados |
| **ML/IA** | Modelo de susceptibilidade treinado (Random Forest / XGBoost) |
| **Mobile PWA** | Service worker + offline-first para campo |
| **Multi-tenancy** | Organizações + RBAC para deploy empresarial |

---

## 👨‍💻 Autoria

**Desenvolvedor:** Lúcio Luiz de Lima
**Orientador:** Prof. Dr. Renilson Ramos (Mestre em Geografia e Análise Geoespacial)
**Instituição:** FACEPE — Faculdade de Ciências Educacionais de Pernambuco
**Fomento:** FACEPE / CNPq — Bolsa de Iniciação Científica e Tecnológica
**Contato:** [Lucio0x01@proton.me](mailto:Lucio0x01@proton.me) | [github.com/LuciolLima](https://github.com/LuciolLima)

---

> **Licença:** Apache License 2.0 + Termos de Uso próprios
> **Lei Aplicável:** República Federativa do Brasil — Foro: Comarca de Recife/PE
> **Versão do Documento:** 1.0 (10/10/2026)