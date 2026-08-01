# Runbook de Incidentes — ASI (Atlas de Suscetibilidade a Inundações)

> **Versão:** 1.0  
> **Última atualização:** 2025-01-XX  
> **Responsável:** Equipe de Engenharia ASI

---

## 📋 Índice

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Componentes Críticos](#componentes-críticos)
3. [Runbooks por Tipo de Incidente](#runbooks-por-tipo-de-incidente)
4. [Procedimentos de Escalação](#procedimentos-de-escalação)
5. [Dashboards de Observabilidade](#dashboards-de-observabilidade)
6. [Checklists de Deploy/Rollback](#checklists-de-deployrollback)
7. [Contatos de Emergência](#contatos-de-emergência)

---

## 🏗️ Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ASI Application (Streamlit)               │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Browser)                                          │
│  ├─ React Component (Deck.gl + MapLibre) ← WebGL 60fps      │
│  ├─ Streamlit Components (UI Atoms/Molecules/Organisms)     │
│  └─ State Machine (SelectionState + EventOrigin)            │
├─────────────────────────────────────────────────────────────┤
│  Backend (Python/Streamlit Server)                          │
│  ├─ Data Layer (DuckDB + Polars + GeoParquet)               │
│  ├─ API Clients (IBGE SIDRA, NASA POWER, Open-Meteo)        │
│  ├─ Analytics Engine (DuckDB Spatial Queries)               │
│  └─ State Machine (SelectionState + EventOrigin)            │
├─────────────────────────────────────────────────────────────┤
│  Data Storage                                                │
│  ├─ GeoParquet (twi_points, bairros, hidro, eventos, DC)   │
│  └─ Cache (Streamlit @st.cache_resource / @st.cache_data)   │
└─────────────────────────────────────────────────────────────┘
```

### Portas & Endpoints
| Serviço | Porta | Protocolo | Health Check |
|---------|-------|-----------|--------------|
| Streamlit App | 8501 | HTTP | `GET /?_health=1` |
| DuckDB (in-memory) | N/A | Local | Query `SELECT 1` |
| GeoParquet Files | N/A | Local FS | `ls data/curated/*.parquet` |

---

## ⚙️ Componentes Críticos

| Componente | Criticidade | SLA | Monitoramento |
|------------|-------------|-----|---------------|
| **Streamlit Server** | 🔴 Crítica | 99.9% | Process uptime + health endpoint |
| **DuckDB Spatial** | 🔴 Crítica | <50ms P95 | Query latency histogram |
| **GeoParquet Files** | 🔴 Crítica | 100% disponível | File existence + size |
| **Deck.gl Map** | 🟡 Alta | 60fps | FPS counter + error boundary |
| **API Externas (IBGE/NASA/OpenMeteo)** | 🟡 Alta | <5s | Latency + error rate |
| **Cache Streamlit** | 🟢 Média | Hit rate >90% | Cache hit/miss ratio |

---

## 🚨 Runbooks por Tipo de Incidente

### INC-001: Streamlit Server Down

**Sintomas:**
- Health endpoint `/ ?_health=1` retorna 5xx ou timeout
- Usuários veem "Streamlit not running"
- Processo Python não está rodando

**Diagnóstico:**
```bash
# Verificar processo
ps aux | grep streamlit

# Verificar logs
tail -f ~/.streamlit/logs/streamlit.log

# Verificar porta
netstat -tlnp | grep 8501
```

**Resolução:**
```bash
# 1. Tentar restart graceful
pkill -f "streamlit run app.py"
streamlit run app.py --server.port 8501 &

# 2. Se falhar, verificar dependências
pip install -r requirements.txt --upgrade

# 3. Se persistir, rollback deploy
git checkout <last-known-good-tag>
./deploy.sh
```

**Escalação:** Se não resolver em 15min → Engenheiro Sênior + On-call

---

### INC-002: DuckDB Spatial Query Latency Spike

**Sintomas:**
- Métrica `click_duration_ms` P95 > 500ms (alerta: >500ms)
- Usuários reclamam de lag no clique do mapa
- Logs mostram queries lentas

**Diagnóstico:**
```python
# Verificar métricas
curl localhost:9090/metrics | grep duckdb

# Verificar índices RTREE
python -c "
import duckdb
conn = duckdb.connect()
conn.execute('CREATE TABLE twi_points AS SELECT * FROM read_parquet(\"data/curated/twi_points.parquet\")')
print(conn.execute('PRAGMA index_list(twi_points)').fetchall())
"
```

**Resolução:**
```bash
# 1. Verificar se índices RTREE existem
# 2. Recriar índices se necessário
python -c "
import duckdb
conn = duckdb.connect()
conn.execute('CREATE INDEX idx_twi_geom ON twi_points USING RTREE(geometry)')
conn.execute('CREATE INDEX idx_eventos_geom ON eventos USING RTREE(geometry)')
"

# 2. Verificar memória
# PRAGMA memory_limit='1GB' no _setup_extensions

# 3. Se dados cresceram, considerar particionamento
```

---

### INC-003: GeoParquet Files Missing/Corrupted

**Sintomas:**
- Erro `FileNotFoundError` ou `BadZipFile` no startup
- Mapa carrega vazio
- Erro `pyarrow.lib.ArrowInvalid`

**Diagnóstico:**
```bash
# Verificar arquivos
ls -la data/curated/*.parquet

# Verificar integridade
python -c "
import pyarrow.parquet as pq
for f in ['twi_points', 'bairros', 'hidro', 'eventos', 'defesa_civil']:
    pf = pq.ParquetFile(f'data/curated/{f}.parquet')
    print(f'{f}: {pf.metadata.num_rows} rows, {pf.metadata.num_columns} cols')
"
```

**Resolução:**
```bash
# 1. Re-gerar a partir do raw
python scripts/convert_to_parquet.py

# 2. Se raw também corrompido, restaurar backup
# rsync -av backup/data/raw/ data/raw/

# 3. Validar após regeneração
python -c "
import geopandas as gpd
for f in ['twi_points', 'bairros', 'hidro', 'eventos']:
    gdf = gpd.read_parquet(f'data/curated/{f}.parquet')
    print(f'{f}: {len(gdf)} rows, CRS={gdf.crs}')
"
```

---

### INC-004: API Externa Timeout/Error Rate Spike

**Sintomas:**
- Métrica `api_errors_total` spike
- Timeouts nas chamadas IBGE/NASA/OpenMeteo
- Fallback UI aparece para usuários

**Diagnóstico:**
```bash
# Testar APIs manualmente
curl -v "https://servicodados.ibge.gov.br/api/v3/agregados/9514/metadados" --max-time 10
curl -v "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&latitude=-8.28&longitude=-35.03&start=2024-01-01&end=2024-01-02" --max-time 10

# Verificar rate limits
grep -c "429" logs/api.log
```

**Resolução:**
```bash
# 1. Verificar se é rate limit (429)
#    - Implementar backoff exponencial no client
#    - Adicionar cache mais agressivo

# 2. Verificar se é mudança de API
#    - Verificar changelog da API
#    - Atualizar client se necessário

# 3. Fallback: usar cache local
#    - Aumentar TTL do cache
#    - Servir dados stale se API indisponível
```

---

### INC-005: Deck.gl Map Not Rendering (WebGL Issues)

**Sintomas:**
- Mapa carrega mas fica preto/branco
- Erro "WebGL context lost" no console
- Usuários em GPUs antigas não veem mapa

**Diagnóstico:**
```javascript
// Console do navegador
// Verificar: WebGL context lost, GL_EXT_frag_depth, etc.

// Verificar user agent
navigator.userAgent
navigator.gpu?.requestAdapter?.()
```

**Resolução:**
```bash
# 1. Fallback automático para st_folium
#    - Implementado em deck_map_panel.py fallback

# 2. Detectar WebGL support
#    - Adicionar feature detection no main.tsx

# 3. Reduzir qualidade para GPUs antigas
#    - Desabilitar HexagonLayer/HeatmapLayer por default
#    - Reduzir radiusPixels no HeatmapLayer
```

---

### INC-006: Cache Miss Rate Spike / Memory Leak

**Sintomas:**
- Cache hit rate < 80%
- Memória do processo crescendo indefinidamente
- OOM kills no container

**Diagnóstico:**
```python
# Verificar cache stats
import streamlit as st
print(st.cache_data._cache_stats)
print(st.cache_resource._cache_stats)

# Memory profiling
import tracemalloc
tracemalloc.start()
# ... run operations ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

**Resolução:**
```python
# 1. Verificar TTLs
#    - Aumentar TTL se dados mudam pouco
#    - Diminuir se dados mudam frequentemente

# 2. Limitar tamanho do cache
#    - max_entries no @st.cache_data

# 3. Memory leak no DuckDB
#    - Verificar se conexões fecham
#    - Usar :memory: com PRAGMA memory_limit
```

---

### INC-007: State Machine Loop / Infinite Rerun

**Sintomas:**
- Página recarrega infinitamente
- CPU 100% no browser
- "Maximum recursion depth" ou similar

**Diagnóstico:**
```javascript
// Console: verificar se st.rerun() em loop
// Verificar SelectionState.update() debounce
```

**Resolução:**
```python
# Verificar SelectionState.update() debounce logic
# - Mesmo evento + mesma origem + mesmo valor = debounce
# - Cliques de usuário NUNCA debounce
# - Updates programáticos SEM debounce
```

---

## 📈 Procedimentos de Escalação

| Severidade | Tempo de Resposta | Responsável | Comunicação |
|------------|-------------------|-------------|-------------|
| **SEV-1** (Sistema indisponível) | 15 min | Engenheiro Sênior + On-call | Slack #incidents + PagerDuty |
| **SEV-2** (Funcionalidade crítica degradada) | 1 hora | Engenheiro Responsável | Slack #incidents |
| **SEV-3** (Degradação menor) | 4 horas | Engenheiro Responsável | Slack #team-asi |
| **SEV-4** (Bug não-crítico) | Next sprint | Backlog | GitHub Issue |

### Matriz de Escalação

| Incidente | 15min | 30min | 1h | 4h |
|-----------|-------|-------|-----|-----|
| SEV-1 | Eng. Sênior + On-call | Tech Lead | Gerente Eng. | VP Eng. |
| SEV-2 | Eng. Responsável | Tech Lead | Gerente Eng. | - |
| SEV-3 | Eng. Responsável | - | Tech Lead | - |

---

## 📊 Dashboards de Observabilidade

### Prometheus/Grafana (se disponível)
```promql
# Latência clique mapa (P95)
histogram_quantile(0.95, rate(asi_click_duration_ms_bucket[5m]))

# Taxa de erro API
rate(asi_api_errors_total[5m])

# Cache hit rate
asi_cache_hits_total / (asi_cache_hits_total + asi_cache_misses_total)

# Memória
process_resident_memory_bytes{job="asi"}

# Cache hit rate
asi_cache_hits_total / (asi_cache_hits_total + asi_cache_misses_total)
```

### Streamlit Metrics Endpoint
```bash
curl http://localhost:8501/?_health=1
# Retorna: {"status": "healthy", "version": "3.1", "data_loaded": true}
```

### Logs Estruturados
```bash
# Filtrar por boundary
grep "boundary.*map" logs/app.log

# Filtrar erros
grep "ERROR" logs/app.log | jq .

# Métricas customizadas
grep "metrics:" logs/app.log | jq .
```

---

## 🚀 Checklists de Deploy/Rollback

### Pre-Deploy Checklist
- [ ] Tests pass: `pytest tests/ -v` (59 passed)
- [ ] Benchmark: `python scripts/benchmark.py` (P95 < 50ms click)
- [ ] Lint: `ruff check src/` / `mypy src/`
- [ ] GeoParquet files valid: `python scripts/validate_parquet.py`
- [ ] Build React map: `cd src/sigweb/map && npm run build`
- [ ] Docker build: `docker build -t asi:latest .`
- [ ] Health check local: `streamlit run app.py & sleep 10 && curl localhost:8501/?_health=1`

### Deploy Steps
```bash
# 1. Tag release
git tag -a v3.2.0 -m "Release v3.2.0"
git push origin v3.2.0

# 2. CI/CD pipeline (GitHub Actions)
# - Run tests
# - Build Docker image
# - Push to registry
# - Deploy to staging

# 3. Smoke test staging
curl https://staging.asi.gov.br/?_health=1

# 4. Promote to production
# - Blue/Green ou Rolling update
```

### Rollback Procedure
```bash
# 1. Identificar último tag estável
git tag -l | tail -5

# 2. Rollback deploy
kubectl rollout undo deployment/asi  # se k8s
# OU
docker service update --image asi:v3.1.0 asi  # se docker swarm

# 3. Verificar health
curl https://asi.gov.br/?_health=1

# 4. Notificar equipe
# Slack #deployments: "Rollback to v3.1.0 completed"
```

---

## 📞 Contatos de Emergência

| Papel | Nome | Slack | Telefone (Plantão) | Email |
|-------|------|-------|-------------------|-------|
| **Tech Lead** | [Nome] | @techlead | +55 XX 9XXXX-XXXX | techlead@asi.gov.br |
| **Eng. Sênior (On-call)** | [Nome] | @senioreng | +55 XX 9XXXX-XXXX | senior@asi.gov.br |
| **Eng. Responsável (Mapa)** | [Nome] | @mapeng | +55 XX 9XXXX-XXXX | map@asi.gov.br |
| **Eng. Responsável (Analytics)** | [Nome] | @analyticseng | +55 XX 9XXXX-XXXX | analytics@asi.gov.br |
| **DevOps/Infra** | [Nome] | @devops | +55 XX 9XXXX-XXXX | devops@asi.gov.br |
| **Gerente de Engenharia** | [Nome] | @engmanager | +55 XX 9XXXX-XXXX | engmanager@asi.gov.br |

### Canais de Comunicação
| Canal | Finalidade | Link |
|-------|------------|------|
| **#incidents** | Incidentes ativos (SEV-1/2) | Slack |
| **#deployments** | Deploys e rollbacks | Slack |
| **#team-asi** | Discussão geral da equipe | Slack |
| **#alerts** | Alertas Prometheus/Grafana | Slack |

---

## 📝 Notas de Atualização do Runbook

| Data | Versão | Autor | Mudanças |
|------|--------|-------|----------|
| 2025-01-XX | 1.0 | [Autor] | Versão inicial |

---

> **⚠️ Importante:** Este runbook deve ser revisado a cada deploy major e após cada incidente SEV-1/2. Mantenha os contatos e procedimentos atualizados.