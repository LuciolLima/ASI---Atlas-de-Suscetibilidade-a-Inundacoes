"""
SISTEMA ASI - DATA LOADER (ETL)
Versão: 2.8 — Precipitação, Eventos Históricos e Índice de Risco por Bairro
"""

import pandas as pd
import unicodedata
from pyproj import Transformer
import streamlit as st
import os
from src.sigweb import config
import requests
from datetime import date

# ══════════════════════════════════════════════════════════════
#  DATASET PRINCIPAL (v2.7 — inalterado)
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Processando base de dados vetorial...", ttl=3600)
def load_geospatial_dataset() -> pd.DataFrame:
    path = config.PATH_DATA_TABLE

    try:
        if not os.path.exists(path):
            st.error(f"ERRO DE I/O: Arquivo não encontrado em: {path}")
            st.stop()
        df = pd.read_csv(path, sep=';', decimal=',', low_memory=False, encoding='utf-8')
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Erro fatal ao ler dados: {e}")
        st.stop()

    try:
        transformer = Transformer.from_crs("EPSG:31985", "EPSG:4326", always_xy=True)
        if 'Coord_X' in df.columns and 'Coord_Y' in df.columns:
            lon, lat = transformer.transform(df['Coord_X'].values, df['Coord_Y'].values)
            df['longitude'] = lon
            df['latitude']  = lat
            df = df[df['latitude'].between(-90, 90) & df['longitude'].between(-180, 180)]
        else:
            st.warning("Colunas de coordenadas (Coord_X, Coord_Y) não encontradas.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro de Geoprocessamento: {e}")
        st.stop()

    df['Uso_Solo_Desc'] = (
        df['RASTERVALU'].fillna(0).astype(int)
        .map(config.MAPBIOMAS_CODES).fillna('Outros')
    )

    if 'SITUACAO' in df.columns:
        s_numeric = pd.to_numeric(df['SITUACAO'], errors='coerce')
        if s_numeric.notna().any():
            df['Situacao_Urbana'] = (
                s_numeric.fillna(0).astype(int)
                .map(config.IBGE_SITUACAO_CODES).fillna('Não Informado')
            )
        else:
            df['Situacao_Urbana'] = df['SITUACAO'].fillna('Não Informado').astype(str).str.strip()
    else:
        df['Situacao_Urbana'] = 'Não Informado'

    bins   = [-1, config.TWI_THRESHOLD_LOW, config.TWI_THRESHOLD_MODERATE,
               config.TWI_THRESHOLD_HIGH, config.TWI_THRESHOLD_CRITICAL, 1000]
    labels = ['MUITO_BAIXO', 'BAIXO', 'MODERADO', 'ALTO', 'CRITICO']
    df['Classe_Risco_Cod']   = pd.cut(df['twi'], bins=bins, labels=labels)
    df['Classe_Risco_Label'] = df['Classe_Risco_Cod'].map(config.CLASS_LABELS)

    if 'NM_BAIRRO' in df.columns:
        df['NM_BAIRRO'] = df['NM_BAIRRO'].fillna('NÃO IDENTIFICADO').str.upper().str.strip()

    return df


# ══════════════════════════════════════════════════════════════
#  PRECIPITAÇÃO HISTÓRICA — v2.8
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Carregando dados de precipitação (APAC)...", ttl=3600)
def load_precipitacao() -> pd.DataFrame:
    """
    Lê precipitacao_historica.csv da APAC.
    Colunas esperadas: data;estacao;precipitacao_mm;latitude;longitude

    Retorna DataFrame vazio sem quebrar o app caso o arquivo não exista.
    """
    path = config.PATH_PRECIPITACAO
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, sep=';', decimal=',', encoding='utf-8')
        df.columns = df.columns.str.strip().str.lower()

        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')

        for col in ['precipitacao_mm', 'latitude', 'longitude']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=['latitude', 'longitude'])
        return df

    except Exception as e:
        st.warning(f"Precipitação: arquivo encontrado mas com erro de leitura — {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  EVENTOS HISTÓRICOS DE INUNDAÇÃO — v2.8
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Carregando histórico de eventos de inundação...", ttl=3600)
def load_eventos_inundacao() -> pd.DataFrame:
    """
    Lê historico_inundacoes.csv.
    Colunas esperadas: data;bairro;descricao;severidade;latitude;longitude;fonte

    Severidade deve conter: LEVE | MODERADA | GRAVE
    Retorna DataFrame vazio sem quebrar o app caso o arquivo não exista.
    """
    path = config.PATH_EVENTOS
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, sep=';', decimal=',', encoding='utf-8')
        df.columns = df.columns.str.strip().str.lower()

        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')

        for col in ['latitude', 'longitude']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=['latitude', 'longitude'])

        if 'severidade' in df.columns:
            df['severidade'] = df['severidade'].str.upper().str.strip()
        else:
            df['severidade'] = 'NÃO INFORMADA'

        if 'bairro' in df.columns:
            df['bairro'] = df['bairro'].str.upper().str.strip()

        return df

    except Exception as e:
        st.warning(f"Eventos: arquivo encontrado mas com erro de leitura — {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  ÍNDICE DE RISCO AGREGADO POR BAIRRO — v2.8
# ══════════════════════════════════════════════════════════════

def calcular_indice_risco_bairro(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o Índice de Risco Agregado (IRA) por bairro.

    IRA = média ponderada das classes de risco dos pontos do bairro.
    Pesos: CRITICO=5 | ALTO=4 | MODERADO=3 | BAIXO=2 | MUITO_BAIXO=1

    Retorna DataFrame ordenado por IRA decrescente com colunas:
        NM_BAIRRO | total_pontos | twi_medio | ira | criticos | altos | classe_dominante
    """
    if df.empty or 'NM_BAIRRO' not in df.columns:
        return pd.DataFrame()

    PESOS = {'CRITICO': 5, 'ALTO': 4, 'MODERADO': 3, 'BAIXO': 2, 'MUITO_BAIXO': 1}

    df = df.copy()
    # pd.cut gera dtype 'category' — converte para str para evitar erros de agregação
    df['Classe_Risco_Cod'] = df['Classe_Risco_Cod'].astype(str)
    df['_peso'] = df['Classe_Risco_Cod'].map(PESOS).fillna(1)

    agg = df.groupby('NM_BAIRRO').agg(
        total_pontos = ('twi',            'count'),
        twi_medio    = ('twi',            'mean'),
        ira          = ('_peso',          'mean'),
        criticos     = ('Classe_Risco_Cod', lambda x: (x == 'CRITICO').sum()),
        altos        = ('Classe_Risco_Cod', lambda x: (x == 'ALTO').sum()),
    ).reset_index()

    classe_dom = (
        df.groupby('NM_BAIRRO')['Classe_Risco_Cod']
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={'Classe_Risco_Cod': 'classe_dominante'})
    )

    agg = agg.merge(classe_dom, on='NM_BAIRRO', how='left')
    agg['pct_critico_alto'] = ((agg['criticos'] + agg['altos']) / agg['total_pontos'] * 100).round(1)
    agg = agg.sort_values('ira', ascending=False).reset_index(drop=True)

    return agg


# ══════════════════════════════════════════════════════════════
#  DEFESA CIVIL PE — CONSOLIDADO — v2.8
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Carregando dados da Defesa Civil PE...", ttl=3600)
def load_defesa_civil() -> pd.DataFrame:
    """
    Lê defesacivil_pe_consolidado.csv — tabela completa com danos humanos
    e materiais por município (Defesa Civil PE / SEPDEC).

    Formato do arquivo: separador=';', decimal=','
    Colunas principais:
        municipio, latitude, longitude, severidade, registros,
        dh_obitos, dh_desabrigados, dh_desalojados, dh_feridos, dh_total,
        dm_total, dm_estradas, dm_comercial, dm_residencial, ...

    Retorna DataFrame vazio sem quebrar o app se o arquivo não existir.
    """
    path = config.PATH_DEFESA_CIVIL
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        # Lê o arquivo respeitando separador de colunas=';' e decimal=','
        df = pd.read_csv(
            path,
            sep=';',
            decimal=',',
            encoding='utf-8',
            thousands=None
        )
        df.columns = df.columns.str.strip()

        if df.empty or len(df.columns) < 3:
            st.warning("Defesa Civil: arquivo lido mas sem dados válidos.")
            return pd.DataFrame()

        # Converte colunas numéricas — substitui vírgula por ponto se necessário
        cols_num = [
            'dh_obitos','dh_desabrigados','dh_desalojados','dh_feridos','dh_total',
            'dm_total','dm_estradas','dm_comercial','dm_residencial','dm_est_ensino',
            'dm_industrial','dm_p_publico','dm_area_prot_ambiental',
            'dm_estab_saude','dm_pontes','dm_outros','latitude','longitude'
        ]
        for col in cols_num:
            if col in df.columns:
                # Garante que vírgula decimal seja convertida mesmo se decimal=',' não pegou
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        if 'registros' in df.columns:
            df['registros'] = pd.to_numeric(
                df['registros'].astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            ).fillna(0).astype(int)

        if 'severidade' in df.columns:
            df['severidade'] = df['severidade'].str.upper().str.strip()

        if 'municipio' in df.columns:
            df['municipio'] = df['municipio'].str.upper().str.strip()

        return df

    except Exception as e:
        st.warning(f"Defesa Civil: erro de leitura — {e}")
        return pd.DataFrame()
    
# ══════════════════════════════════════════════════════════════
#  CORRELAÇÃO CRUZADA DE DATASETS — v2.9
# ══════════════════════════════════════════════════════════════

def _normalizar_municipio(nome: str) -> str:
    """
    Normaliza nome de município para join entre datasets.
    Remove acentos, converte para maiúsculo, strip.
    Ex: 'Caruarú' → 'CARUARU' | 'água Preta' → 'AGUA PRETA'
    """
    if not isinstance(nome, str):
        return ''
    nfkd = unicodedata.normalize('NFKD', nome)
    sem_acento = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.upper().strip()


def correlacionar_datasets(
    df_twi: pd.DataFrame,
    df_dc: pd.DataFrame,
    df_precip: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Cruza TWI × Defesa Civil × Precipitação por município.

    Parâmetros:
        df_twi    → retorno de load_geospatial_dataset()
        df_dc     → retorno de load_defesa_civil()
        df_precip → retorno de load_precipitacao() (opcional)

    Retorna DataFrame com uma linha por município contendo:
        municipio, twi_medio, pct_critico_alto, ira_medio,
        total_pontos_twi, dh_total, dm_total, severidade_dc,
        precip_media_mm (se disponível)
    """

    if df_twi.empty or df_dc.empty:
        return pd.DataFrame()

    PESOS = {'CRITICO': 5, 'ALTO': 4, 'MODERADO': 3, 'BAIXO': 2, 'MUITO_BAIXO': 1}

    # ── 1. Agrega TWI por município ────────────────────────────
    twi = df_twi.copy()
    twi['Classe_Risco_Cod'] = twi['Classe_Risco_Cod'].astype(str)
    twi['_peso'] = twi['Classe_Risco_Cod'].map(PESOS).fillna(1)
    twi['_municipio'] = twi['NM_MUN'].apply(_normalizar_municipio)

    agg_twi = twi.groupby('_municipio').agg(
        twi_medio        = ('twi',             'mean'),
        ira_medio        = ('_peso',            'mean'),
        total_pontos_twi = ('twi',             'count'),
        criticos         = ('Classe_Risco_Cod', lambda x: (x == 'CRITICO').sum()),
        altos            = ('Classe_Risco_Cod', lambda x: (x == 'ALTO').sum()),
    ).reset_index()

    agg_twi['pct_critico_alto'] = (
        (agg_twi['criticos'] + agg_twi['altos']) / agg_twi['total_pontos_twi'] * 100
    ).round(1)
    agg_twi['twi_medio'] = agg_twi['twi_medio'].round(2)
    agg_twi['ira_medio'] = agg_twi['ira_medio'].round(2)

    # ── 2. Normaliza Defesa Civil ──────────────────────────────
    dc = df_dc.copy()
    dc['_municipio'] = dc['municipio'].apply(_normalizar_municipio)

    cols_dc = ['_municipio', 'severidade', 'dh_total', 'dm_total',
               'dh_obitos', 'dh_desabrigados', 'dh_desalojados']
    cols_dc = [c for c in cols_dc if c in dc.columns]
    dc = dc[cols_dc]

    # ── 3. Merge TWI × Defesa Civil ───────────────────────────
    merged = agg_twi.merge(dc, on='_municipio', how='inner')
    merged = merged.rename(columns={'_municipio': 'municipio'})

    # ── 4. Precipitação (opcional) ────────────────────────────
    if df_precip is not None and not df_precip.empty:
        precip = df_precip.copy()

        if 'estacao' in precip.columns:
            precip['_municipio'] = (
                precip['estacao']
                .str.extract(r'^([^(]+)')[0]
                .apply(_normalizar_municipio)
            )

            col_mm = next(
                (c for c in precip.columns if 'precip' in c or '_mm' in c),
                None
            )
            if col_mm:
                agg_precip = (
                    precip[precip['_municipio'] != '']
                    .groupby('_municipio')[col_mm]
                    .agg(
                        precip_media_mm='mean',
                        precip_max_mm='max',
                        precip_total_mm='sum'
                    )
                    .reset_index()
                    .rename(columns={'_municipio': 'municipio'})
                )
                agg_precip['precip_media_mm']  = agg_precip['precip_media_mm'].round(1)
                agg_precip['precip_max_mm']    = agg_precip['precip_max_mm'].round(1)
                agg_precip['precip_total_mm']  = agg_precip['precip_total_mm'].round(1)

                merged = merged.merge(agg_precip, on='municipio', how='left')
    
    # ── 5. Ordena por risco ───────────────────────────────────
    merged = merged.sort_values('ira_medio', ascending=False).reset_index(drop=True)

    return merged