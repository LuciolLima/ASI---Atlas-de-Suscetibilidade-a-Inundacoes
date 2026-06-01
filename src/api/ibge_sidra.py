"""
SISTEMA ASI — MÓDULO DE API EXTERNA
Provedor: IBGE — Sistema IBGE de Recuperação Automática (SIDRA)
Versão: 3.5 — Saneamento via Tabela 9860 (Censo 2022, classificação 11558)
              Tipo de esgotamento sanitário por município — dados reais do Censo 2022
"""

import sidrapy
import pandas as pd
import unicodedata
import streamlit as st


# ══════════════════════════════════════════════════════════════
#  CONSTANTES — TABELA 9860 / CLASSIFICAÇÃO 11558
# ══════════════════════════════════════════════════════════════

# Categoria de esgotamento considerada ADEQUADA
# 46290 = "Rede geral, rede pluvial ou fossa ligada à rede"
CAT_ESGOTO_ADEQUADO = "46290"
# 46292 = Total de domicílios (denominador)
CAT_ESGOTO_TOTAL    = "46292"


# ══════════════════════════════════════════════════════════════
#  UTILITÁRIOS
# ══════════════════════════════════════════════════════════════

def _normalizar_municipio(nome: str) -> str:
    if not isinstance(nome, str):
        return ''
    nome = nome.split(' - ')[0]
    nfkd = unicodedata.normalize('NFKD', nome)
    sem_acento = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.upper().strip()


def _detectar_col_valor(df: pd.DataFrame) -> str:
    for col in ['V', 'v']:
        if col in df.columns:
            return col
    raise KeyError(f"Coluna de valor não encontrada. Disponíveis: {list(df.columns)}")


def _classificar_vulnerabilidade(perc: float) -> str:
    if perc >= 60.0:
        return 'CRITICA'
    elif perc >= 40.0:
        return 'ALTA'
    elif perc >= 20.0:
        return 'MODERADA'
    else:
        return 'BAIXA'


# ══════════════════════════════════════════════════════════════
#  COLETA: POPULAÇÃO (Tabela 9514, Variável 93)
# ══════════════════════════════════════════════════════════════

@st.cache_data(
    show_spinner="Consultando base demográfica — IBGE SIDRA (Censo 2022)...",
    ttl=86400
)
def fetch_populacao_pe() -> pd.DataFrame:
    try:
        df_raw = sidrapy.get_table(
            table_code="9514",
            territorial_level="6",
            ibge_territorial_code="all",
            variable="93",
            period="2022"
        )
        df = df_raw.iloc[1:].copy()
        df = df[df['D1N'].str.contains('- PE', na=False)]
        col = _detectar_col_valor(df)
        df = df.rename(columns={col: 'populacao_total', 'D1N': 'municipio_ibge'})
        df = df[['municipio_ibge', 'populacao_total']].copy()
        df['populacao_total'] = (
            pd.to_numeric(df['populacao_total'], errors='coerce').fillna(0).astype(int)
        )
        df['municipio'] = df['municipio_ibge'].apply(_normalizar_municipio)
        return df[['municipio', 'populacao_total']].reset_index(drop=True)
    except Exception as e:
        st.warning(f"Falha na conexão com o servidor IBGE/SIDRA: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  COLETA CONSOLIDADA: POPULAÇÃO + SANEAMENTO
# ══════════════════════════════════════════════════════════════

@st.cache_data(
    show_spinner="Integrando bases censitárias — População e Saneamento (IBGE SIDRA)...",
    ttl=86400
)
def fetch_sidra_pe() -> pd.DataFrame:
    """
    Coleta população (Tabela 9514) e saneamento (Tabela 9860, Censo 2022).

    O percentual de saneamento adequado é calculado como:
        domicílios com rede geral/pluvial ou fossa ligada à rede (cat. 46290)
        ÷ total de domicílios (cat. 46292) × 100

    Fonte: IBGE, Censo Demográfico 2022.
    Tabela 9860 — Classificação 11558 (Tipo de esgotamento sanitário).
    """
    try:
        # ── População ─────────────────────────────────────────
        df_pop_raw = sidrapy.get_table(
            table_code="9514",
            territorial_level="6",
            ibge_territorial_code="all",
            variable="93",
            period="2022"
        )
        df_pop = df_pop_raw.iloc[1:].copy()
        df_pop = df_pop[df_pop['D1N'].str.contains('- PE', na=False)]
        col_pop = _detectar_col_valor(df_pop)
        df_pop = (
            df_pop[['D1N', col_pop]]
            .rename(columns={'D1N': 'municipio', col_pop: 'populacao'})
            .copy()
        )
        df_pop['populacao'] = pd.to_numeric(
            df_pop['populacao'], errors='coerce'
        ).fillna(0).astype(int)

        # ── Saneamento — Total de domicílios ──────────────────
        df_total_raw = sidrapy.get_table(
            table_code="9860",
            territorial_level="6",
            ibge_territorial_code="all",
            variable="381",
            period="2022",
            classifications={"11558": CAT_ESGOTO_TOTAL}
        )
        df_total = df_total_raw.iloc[1:].copy()
        df_total = df_total[df_total['D1N'].str.contains('- PE', na=False)]
        col_t = _detectar_col_valor(df_total)
        df_total = (
            df_total[['D1N', col_t]]
            .rename(columns={'D1N': 'municipio', col_t: 'dom_total'})
            .copy()
        )
        df_total['dom_total'] = pd.to_numeric(
            df_total['dom_total'], errors='coerce'
        ).fillna(0)

        # ── Saneamento — Domicílios com esgoto adequado ───────
        df_adeq_raw = sidrapy.get_table(
            table_code="9860",
            territorial_level="6",
            ibge_territorial_code="all",
            variable="381",
            period="2022",
            classifications={"11558": CAT_ESGOTO_ADEQUADO}
        )
        df_adeq = df_adeq_raw.iloc[1:].copy()
        df_adeq = df_adeq[df_adeq['D1N'].str.contains('- PE', na=False)]
        col_a = _detectar_col_valor(df_adeq)
        df_adeq = (
            df_adeq[['D1N', col_a]]
            .rename(columns={'D1N': 'municipio', col_a: 'dom_adequado'})
            .copy()
        )
        df_adeq['dom_adequado'] = pd.to_numeric(
            df_adeq['dom_adequado'], errors='coerce'
        ).fillna(0)

        # ── Cálculo do percentual de saneamento ───────────────
        df_san = pd.merge(df_total, df_adeq, on='municipio', how='inner')
        df_san['perc_saneamento_adequado'] = (
            df_san['dom_adequado'] / df_san['dom_total'] * 100
        ).clip(0, 100).where(df_san['dom_total'] > 0, other=None)

        # ── Merge final ───────────────────────────────────────
        df = pd.merge(df_pop, df_san[['municipio', 'perc_saneamento_adequado']],
                      on='municipio', how='left')

        df['perc_saneamento_adequado'] = pd.to_numeric(
            df['perc_saneamento_adequado'], errors='coerce'
        )
        df['perc_vulnerabilidade'] = (
            100.0 - df['perc_saneamento_adequado']
        ).clip(lower=0.0)

        df['municipio'] = df['municipio'].apply(_normalizar_municipio)
        df['classe_vulnerabilidade'] = df['perc_vulnerabilidade'].apply(
            lambda x: _classificar_vulnerabilidade(x) if pd.notna(x) else 'SEM DADOS'
        )

        return df.sort_values('populacao', ascending=False).reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro na integração IBGE SIDRA: {e}")
        return pd.DataFrame()