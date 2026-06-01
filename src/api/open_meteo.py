"""
SISTEMA ASI — MÓDULO DE API EXTERNA
Provedor: Open-Meteo (https://open-meteo.com)
Descrição: Consumo de precipitação diária (histórico 7d + previsão 7d)
           para estações meteorológicas de referência em Pernambuco.
Protocolo: REST/JSON | Sem autenticação | Uso não-comercial gratuito
Versão: 3.0 — Refatoração para o Hub de Integração de Dados Externos
"""

import requests
import pandas as pd
from datetime import date
import streamlit as st


# ══════════════════════════════════════════════════════════════
#  ESTAÇÕES DE REFERÊNCIA — PERNAMBUCO
#  Coordenadas geográficas (WGS84) das principais estações
#  meteorológicas do estado, utilizadas como pontos de consulta
#  à API Open-Meteo quando o CSV da APAC não está disponível.
# ══════════════════════════════════════════════════════════════

ESTACOES_PE_REFERENCIA = [
    # Região Metropolitana do Recife
    {'estacao': 'RECIFE',                   'lat': -8.0539,  'lon': -34.8811},
    {'estacao': 'CABO DE SANTO AGOSTINHO',  'lat': -8.2897,  'lon': -35.0349},
    {'estacao': 'JABOATAO DOS GUARARAPES',  'lat': -8.1131,  'lon': -35.0014},
    {'estacao': 'OLINDA',                   'lat': -7.9994,  'lon': -34.8450},
    {'estacao': 'CARUARU',                  'lat': -8.3561,  'lon': -36.0283},
    {'estacao': 'PAULISTA',                 'lat': -7.9403,  'lon': -34.8730},
    {'estacao': 'CAMARAGIBE',               'lat': -8.0228,  'lon': -35.0528},
    {'estacao': 'SAO LOURENCO DA MATA',     'lat': -8.0044,  'lon': -35.1731},
    {'estacao': 'IPOJUCA',                  'lat': -8.3978,  'lon': -35.0617},
    # Zona da Mata
    {'estacao': 'PALMARES',                 'lat': -8.6838,  'lon': -35.5891},
    {'estacao': 'VITORIA DE SANTO ANTAO',   'lat': -8.1189,  'lon': -35.2950},
    {'estacao': 'ESCADA',                   'lat': -8.3589,  'lon': -35.2258},
    {'estacao': 'RIBEIRAO',                 'lat': -8.5189,  'lon': -35.3689},
    {'estacao': 'CATENDE',                  'lat': -8.6742,  'lon': -35.7181},
    {'estacao': 'AGUA PRETA',               'lat': -8.7078,  'lon': -35.5242},
    # Agreste
    {'estacao': 'SURUBIM',                  'lat': -7.8338,  'lon': -35.7580},
    {'estacao': 'GARANHUNS',                'lat': -8.9108,  'lon': -36.4933},
    {'estacao': 'CAETES',                   'lat': -8.7742,  'lon': -36.6219},
    {'estacao': 'BEZERROS',                 'lat': -8.2389,  'lon': -35.7531},
    {'estacao': 'GRAVATA',                  'lat': -8.2019,  'lon': -35.5658},
    {'estacao': 'BELO JARDIM',              'lat': -8.3361,  'lon': -36.4239},
    {'estacao': 'PESQUEIRA',                'lat': -8.3597,  'lon': -36.6961},
    {'estacao': 'ARCOVERDE',                'lat': -8.4186,  'lon': -37.0539},
    {'estacao': 'BUIQUE',                   'lat': -8.6208,  'lon': -37.1561},
    {'estacao': 'VENTUROSA',                'lat': -8.5739,  'lon': -36.8722},
    # Sertão
    {'estacao': 'PETROLINA',                'lat': -9.3880,  'lon': -40.5002},
    {'estacao': 'SALGUEIRO',                'lat': -8.0727,  'lon': -39.1136},
    {'estacao': 'SERRA TALHADA',            'lat': -7.9855,  'lon': -38.2938},
    {'estacao': 'OURICURI',                 'lat': -7.8797,  'lon': -40.0811},
    {'estacao': 'FLORESTA',                 'lat': -8.5988,  'lon': -38.5841},
    {'estacao': 'IBIMIRIM',                 'lat': -8.5388,  'lon': -37.6997},
    {'estacao': 'CABROBO',                  'lat': -8.5038,  'lon': -39.3152},
    {'estacao': 'BELEM DE SAO FRANCISCO',   'lat': -8.7558,  'lon': -38.9669},
    {'estacao': 'SANTA MARIA DA BOA VISTA', 'lat': -8.8028,  'lon': -39.8239},
    {'estacao': 'TRINDADE',                 'lat': -7.7578,  'lon': -40.2658},
    {'estacao': 'EXU',                      'lat': -7.5139,  'lon': -39.7228},
    {'estacao': 'ARARIPINA',                'lat': -7.5761,  'lon': -40.4989},
    # Sertão do São Francisco
    {'estacao': 'AFRANIO',                  'lat': -8.5158,  'lon': -41.0050},
    {'estacao': 'LAGOA GRANDE',             'lat': -8.9939,  'lon': -40.2711},
    {'estacao': 'OROCO',                    'lat': -8.6108,  'lon': -39.6028},
]

# Limiares de classificação pluviométrica (mm acumulados em 7 dias)
LIMIAR_ATENCAO_MM = 30.0
LIMIAR_ALERTA_MM  = 60.0

# Endpoint base da API Open-Meteo
OPEN_METEO_ENDPOINT = "https://api.open-meteo.com/v1/forecast"


# ══════════════════════════════════════════════════════════════
#  FUNÇÃO PRINCIPAL DE COLETA
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Consultando API Open-Meteo (precipitação em tempo real)...", ttl=3600)
def fetch_precipitacao_pe(df_precip_csv=None) -> pd.DataFrame:
    """
    Realiza requisições à API Open-Meteo para cada estação de referência
    e retorna um DataFrame consolidado com precipitação diária.

    Parâmetros
    ----------
    df_precip_csv : pd.DataFrame, opcional
        DataFrame de precipitação do CSV da APAC. Se disponível e contendo
        coordenadas, substitui as estações de fallback como pontos de consulta.

    Retorna
    -------
    pd.DataFrame com colunas:
        estacao         — Nome da estação de referência
        latitude        — Latitude WGS84
        longitude       — Longitude WGS84
        data            — Data de referência (datetime)
        precipitacao_mm — Volume precipitado diário (mm)
        tipo            — 'historico' (passado 7d) ou 'previsao' (próximos 7d)
    """
    estacoes = _resolver_estacoes(df_precip_csv)
    hoje     = date.today()
    registros = []

    for est in estacoes:
        try:
            params = {
                'latitude':      est['lat'],
                'longitude':     est['lon'],
                'daily':         'precipitation_sum',
                'timezone':      'America/Recife',
                'past_days':     7,
                'forecast_days': 7
            }
            resposta = requests.get(OPEN_METEO_ENDPOINT, params=params, timeout=10)
            if resposta.status_code != 200:
                continue

            payload = resposta.json()
            datas   = payload.get('daily', {}).get('time', [])
            precips = payload.get('daily', {}).get('precipitation_sum', [])

            for dt_str, mm in zip(datas, precips):
                dt = date.fromisoformat(dt_str)
                registros.append({
                    'estacao':         est['estacao'],
                    'latitude':        est['lat'],
                    'longitude':       est['lon'],
                    'data':            dt,
                    'precipitacao_mm': float(mm) if mm is not None else 0.0,
                    'tipo':            'historico' if dt <= hoje else 'previsao'
                })

        except requests.exceptions.Timeout:
            continue
        except Exception:
            continue

    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)
    df['data'] = pd.to_datetime(df['data'])
    return df


# ══════════════════════════════════════════════════════════════
#  FUNÇÃO LEGADA (mantida para compatibilidade com Sessão 3f)
# ══════════════════════════════════════════════════════════════

def fetch_precipitacao_realtime(df_precip_csv=None) -> pd.DataFrame:
    """
    Alias de compatibilidade. Redireciona para fetch_precipitacao_pe().
    Mantida para não quebrar referências legadas no app.py v2.9.
    """
    return fetch_precipitacao_pe(df_precip_csv=df_precip_csv)


# ══════════════════════════════════════════════════════════════
#  FUNÇÃO AUXILIAR PRIVADA
# ══════════════════════════════════════════════════════════════

def _resolver_estacoes(df_precip_csv) -> list:
    """
    Determina a lista de estações a ser consultada.
    Sempre retorna a lista de referência completa para garantir que todas
    as estações esperadas sejam incluídas, independentemente do conteúdo do CSV.
    O CSV é utilizado apenas para carregar dados de precipitação quando disponível
    via load_precipitacao() em data_loader.py.
    """
    # Sempre retorna a lista de referência de estações para garantir consistência
    # e evitar que estações faltantes no CSV sejam omitidas das consultas à API
    return ESTACOES_PE_REFERENCIA