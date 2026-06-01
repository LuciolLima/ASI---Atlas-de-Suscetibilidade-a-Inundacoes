"""
SISTEMA ASI — MÓDULO DE API EXTERNA
Provedor: NASA POWER (Prediction Of Worldwide Energy Resources)
URL: https://power.larc.nasa.gov/api/temporal/daily/point
Descrição: Parâmetros agrometeorológicos diários para estações de referência
           em Pernambuco — umidade do solo, precipitação, temperatura,
           evapotranspiração e índices de saturação pedológica.
Protocolo: REST/JSON | Sem autenticação | Gratuito
Versão: 1.0 — Integração ao Hub de Dados Externos do ASI
"""

import requests
import pandas as pd
from datetime import date, timedelta
import streamlit as st


# ══════════════════════════════════════════════════════════════
#  ESTAÇÕES DE REFERÊNCIA — PERNAMBUCO (mesmas do Open-Meteo)
# ══════════════════════════════════════════════════════════════

ESTACOES_PE = [
    {'estacao': 'RECIFE',                  'lat': -8.0539,  'lon': -34.8811},
    {'estacao': 'CABO DE SANTO AGOSTINHO', 'lat': -8.2897,  'lon': -35.0349},
    {'estacao': 'JABOATAO DOS GUARARAPES', 'lat': -8.1131,  'lon': -35.0014},
    {'estacao': 'CARUARU',                 'lat': -8.3561,  'lon': -36.0283},
    {'estacao': 'GARANHUNS',               'lat': -8.9108,  'lon': -36.4933},
    {'estacao': 'PETROLINA',               'lat': -9.3880,  'lon': -40.5002},
    {'estacao': 'SALGUEIRO',               'lat': -8.0727,  'lon': -39.1136},
    {'estacao': 'SERRA TALHADA',           'lat': -7.9855,  'lon': -38.2938},
    {'estacao': 'ARCOVERDE',               'lat': -8.4186,  'lon': -37.0539},
    {'estacao': 'PALMARES',                'lat': -8.6838,  'lon': -35.5891},
    {'estacao': 'SURUBIM',                 'lat': -7.8338,  'lon': -35.7580},
    {'estacao': 'OURICURI',                'lat': -7.8797,  'lon': -40.0811},
]

# ── Parâmetros NASA POWER solicitados ─────────────────────────
# PRECTOTCORR : Precipitação corrigida (mm/dia)         — MERRA-2
# T2M         : Temperatura a 2m (°C)                   — MERRA-2
# T2M_MAX     : Temperatura máxima a 2m (°C)            — MERRA-2
# T2M_MIN     : Temperatura mínima a 2m (°C)            — MERRA-2
# RH2M        : Umidade relativa a 2m (%)               — MERRA-2
# T2MDEW      : Ponto de orvalho a 2m (°C)              — MERRA-2
# GWETTOP     : Umidade superficial do solo (0–5 cm, %) — MERRA-2 LAND
# GWETROOT    : Umidade zona radicular (0–100 cm, %)    — MERRA-2 LAND
# GWETPROF    : Umidade perfil total do solo (%)        — MERRA-2 LAND
# EVPTRNS     : Evapotranspiração (mm/dia)              — MERRA-2 LAND
# WS2M        : Velocidade do vento a 2m (m/s)          — MERRA-2
NASA_PARAMS = (
    "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,T2MDEW,"
    "GWETTOP,GWETROOT,GWETPROF,EVPTRNS,WS2M"
)

NASA_ENDPOINT = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Limiares de saturação de solo (fração volumétrica, 0–1)
LIMIAR_ATENCAO_SOLO  = 0.60   # 60% da capacidade de campo
LIMIAR_SATURACAO_SOLO = 0.80  # 80% — risco de escoamento superficial


# ══════════════════════════════════════════════════════════════
#  FUNÇÃO PRINCIPAL DE COLETA
# ══════════════════════════════════════════════════════════════

@st.cache_data(
    show_spinner="Consultando NASA POWER — Parâmetros Agrometeorológicos...",
    ttl=3600  # Cache de 1 hora
)
def fetch_nasa_power_pe() -> pd.DataFrame:
    """
    Busca parâmetros agrometeorológicos diários via NASA POWER API
    para as estações de referência de Pernambuco.

    Período coletado
    ----------------
    - Histórico longo  : últimos 365 dias (análise de tendência sazonal)
    - Janela recente   : últimos 30 dias são destacados nas análises

    Parâmetros retornados
    ---------------------
    precipitacao_mm, temp_media, temp_max, temp_min,
    umidade_relativa, ponto_orvalho,
    umidade_solo_superficial (GWETTOP),
    umidade_solo_radicular   (GWETROOT),
    umidade_solo_perfil      (GWETPROF),
    evapotranspiracao_mm, vento_ms

    Retorna
    -------
    pd.DataFrame vazio se a API estiver indisponível.
    """
    hoje      = date.today()
    data_ini  = hoje - timedelta(days=365)
    registros = []

    for est in ESTACOES_PE:
        try:
            params = {
                "parameters": NASA_PARAMS,
                "community":  "AG",
                "longitude":  est['lon'],
                "latitude":   est['lat'],
                "start":      data_ini.strftime("%Y%m%d"),
                "end":        hoje.strftime("%Y%m%d"),
                "format":     "JSON"
            }
            resp = requests.get(NASA_ENDPOINT, params=params, timeout=30)
            if resp.status_code != 200:
                continue

            payload    = resp.json()
            parametros = payload.get('properties', {}).get('parameter', {})
            if not parametros:
                continue

            # Datas como chaves dos dicts internos (formato YYYYMMDD)
            datas = list(next(iter(parametros.values())).keys())

            for dt_str in datas:
                try:
                    dt = date(int(dt_str[:4]), int(dt_str[4:6]), int(dt_str[6:8]))
                except ValueError:
                    continue

                def _val(chave):
                    v = parametros.get(chave, {}).get(dt_str, -999)
                    return float(v) if v not in (-999, -999.0, None) else None

                registros.append({
                    'estacao':                    est['estacao'],
                    'latitude':                   est['lat'],
                    'longitude':                  est['lon'],
                    'data':                       dt,
                    'precipitacao_mm':            _val('PRECTOTCORR'),
                    'temp_media':                 _val('T2M'),
                    'temp_max':                   _val('T2M_MAX'),
                    'temp_min':                   _val('T2M_MIN'),
                    'umidade_relativa':           _val('RH2M'),
                    'ponto_orvalho':              _val('T2MDEW'),
                    'umidade_solo_superficial':   _val('GWETTOP'),
                    'umidade_solo_radicular':     _val('GWETROOT'),
                    'umidade_solo_perfil':        _val('GWETPROF'),
                    'evapotranspiracao_mm':       _val('EVPTRNS'),
                    'vento_ms':                   _val('WS2M'),
                })

        except requests.exceptions.Timeout:
            continue
        except Exception:
            continue

    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)
    df['data'] = pd.to_datetime(df['data'])

    # Período da janela recente (últimos 30 dias)
    corte_recente = pd.Timestamp(hoje - timedelta(days=30))
    df['janela'] = df['data'].apply(
        lambda d: 'recente' if d >= corte_recente else 'historico'
    )

    # Índice de saturação pedológica — combina umidade superficial e radicular
    # Valores NASA POWER GWETTOP/GWETROOT são frações de 0 a 1
    df['indice_saturacao'] = df.apply(
        lambda r: (
            (r['umidade_solo_superficial'] * 0.4 + r['umidade_solo_radicular'] * 0.6)
            if pd.notna(r['umidade_solo_superficial']) and pd.notna(r['umidade_solo_radicular'])
            else None
        ),
        axis=1
    )

    # Classificação de risco de saturação
    def _classe_saturacao(v):
        if v is None or pd.isna(v):
            return 'SEM DADOS'
        if v >= LIMIAR_SATURACAO_SOLO:
            return 'CRITICO'
        elif v >= LIMIAR_ATENCAO_SOLO:
            return 'ATENCAO'
        else:
            return 'NORMAL'

    df['classe_saturacao'] = df['indice_saturacao'].apply(_classe_saturacao)

    return df.sort_values(['estacao', 'data']).reset_index(drop=True)