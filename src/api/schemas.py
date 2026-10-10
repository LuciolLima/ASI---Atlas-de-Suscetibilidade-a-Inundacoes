"""SISTEMA ASI — SCHEMAS PANDERA PARA VALIDA VALIDAÇÃO DE DADOS DE API
Versão: 1.0 — Validação de entrada/saída para APIs externas
"""

from __future__ import annotations

import logging
from typing import Any

import pandera.pandas as pa
from pandera.typing import DataFrame, Series

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# SCHEMAS — CEMADEN
# ════════════════════════════════════════════════════════════════════════════════

class CemadenAlertSchema(pa.DataFrameModel):
    """Schema para alertas CEMADEN (inundação, deslizamento, etc.)."""

    id_alerta: Series[str] = pa.Field(nullable=True, description="ID único do alerta")
    tipo_alerta: Series[str] = pa.Field(
        nullable=True,
        isin=["INUNDACAO", "DESLIZAMENTO", "ENXURRADA", "ALAGAMENTO", "OUTRO"],
        description="Tipo de alerta"
    )
    nivel_risco: Series[str] = pa.Field(
        nullable=True,
        isin=["CRITICO", "ALTO", "MODERADO", "BAIXO", "OBSERVACAO", "NORMAL"],
        description="Nível de risco do alerta"
    )
    data_alerta: Series[Any] = pa.Field(nullable=True, description="Data do alerta (date)")
    hora_alerta: Series[str] = pa.Field(nullable=True, description="Hora do alerta")
    municipio: Series[str] = pa.Field(nullable=True, description="Nome do município")
    uf: Series[str] = pa.Field(nullable=True, isin=["PE"], description="UF")
    latitude: Series[float] = pa.Field(ge=-90, le=90, nullable=True)
    longitude: Series[float] = pa.Field(ge=-180, le=180, nullable=True)
    descricao: Series[str] = pa.Field(nullable=True, description="Descrição do alerta")
    municipio_norm: Series[str] = pa.Field(nullable=True, description="Município normalizado para joins")

    class Config:
        strict = False
        coerce = True


class CemadenPluvioSchema(pa.DataFrameModel):
    """Schema para dados pluviométricos CEMADEN."""

    codigo_estacao: Series[str] = pa.Field(nullable=True, description="Código da estação CEMADEN")
    nome_estacao: Series[str] = pa.Field(nullable=True, description="Nome da estação")
    municipio: Series[str] = pa.Field(nullable=True, description="Nome do município")
    uf: Series[str] = pa.Field(nullable=True, isin=["PE"], description="UF")
    latitude: Series[float] = pa.Field(ge=-90, le=90, nullable=True)
    longitude: Series[float] = pa.Field(ge=-180, le=180, nullable=True)
    chuva_1h_mm: Series[float] = pa.Field(ge=0, nullable=True, description="Chuva acumulada 1h (mm)")
    chuva_6h_mm: Series[float] = pa.Field(ge=0, nullable=True, description="Chuva acumulada 6h (mm)")
    chuva_24h_mm: Series[float] = pa.Field(ge=0, nullable=True, description="Chuva acumulada 24h (mm)")
    chuva_72h_mm: Series[float] = pa.Field(ge=0, nullable=True, description="Chuva acumulada 72h (mm)")
    data_medicao: Series[Any] = pa.Field(nullable=True, description="Data da medição (date)")
    hora_medicao: Series[str] = pa.Field(nullable=True, description="Hora da medição")
    municipio_norm: Series[str] = pa.Field(nullable=True, description="Município normalizado para joins")
    classe_risco_chuva: Series[str] = pa.Field(
        nullable=True,
        isin=["CRITICO", "ALTO", "MODERADO", "BAIXO", "NORMAL"],
        description="Classe de risco baseada em limiares de chuva"
    )

    class Config:
        strict = False
        coerce = True


# ═════════════════════════════════════════════════════════════════════════════════
# SCHEMAS — INMET
# ════════════════════════════════════════════════════════════════════════════════

class InmetRecordSchema(pa.DataFrameModel):
    """Schema para registro meteorológico INMET."""

    codigo_estacao: Series[str] = pa.Field(nullable=False, description="Código da estação INMET")
    nome_estacao: Series[str] = pa.Field(nullable=True, description="Nome da estação")
    municipio: Series[str] = pa.Field(nullable=True, description="Nome do município")
    uf: Series[str] = pa.Field(nullable=True, description="UF")
    latitude: Series[float] = pa.Field(ge=-90, le=90, nullable=True)
    longitude: Series[float] = pa.Field(ge=-180, le=180, nullable=True)
    data_medicao: Series[Any] = pa.Field(nullable=True, description="Data da medição (datetime)")
    hora_medicao: Series[str] = pa.Field(nullable=True, description="Hora da medição")
    # Temperatura
    temp_instantanea: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="Temperatura instantânea (°C)")
    temp_maxima: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="Temperatura máxima (°C)")
    temp_minima: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="Temperatura mínima (°C)")
    # Umidade
    umidade_instantanea: Series[float] = pa.Field(ge=0, le=100, nullable=True, description="Umidade relativa instantânea (%)")
    umidade_maxima: Series[float] = pa.Field(ge=0, le=100, nullable=True, description="Umidade relativa máxima (%)")
    umidade_minima: Series[float] = pa.Field(ge=0, le=100, nullable=True, description="Umidade relativa mínima (%)")
    # Vento
    vento_velocidade: Series[float] = pa.Field(ge=0, nullable=True, description="Velocidade do vento (m/s)")
    vento_direcao: Series[float] = pa.Field(ge=0, le=360, nullable=True, description="Direção do vento (graus)")
    # Radiação
    radiacao_global: Series[float] = pa.Field(ge=0, nullable=True, description="Radiação global (W/m²)")
    # Precipitação
    precipitacao: Series[float] = pa.Field(ge=0, nullable=True, description="Precipitação (mm)")
    # Ponto de orvalho
    ponto_orvalho_instantaneo: Series[float] = pa.Field(nullable=True, description="Ponto de orvalho instantâneo (°C)")
    ponto_orvalho_maximo: Series[float] = pa.Field(nullable=True, description="Ponto de orvalho máximo (°C)")
    ponto_orvalho_minimo: Series[float] = pa.Field(nullable=True, description="Ponto de orvalho mínimo (°C)")
    # Pressão
    pressao_instantanea: Series[float] = pa.Field(ge=800, le=1100, nullable=True, description="Pressão atmosférica instantânea (hPa)")
    pressao_maxima: Series[float] = pa.Field(ge=800, le=1100, nullable=True, description="Pressão atmosférica máxima (hPa)")
    pressao_minima: Series[float] = pa.Field(ge=800, le=1100, nullable=True, description="Pressão atmosférica mínima (hPa)")
    # Evapotranspiração
    etp: Series[float] = pa.Field(ge=0, nullable=True, description="Evapotranspiração de referência (mm)")

    class Config:
        strict = False
        coerce = True


# ═════════════════════════════════════════════════════════════════════════════════
# SCHEMAS — IBGE SIDRA
# ═════════════════════════════════════════════════════════════════════════════════

class SidraPopulacaoSchema(pa.DataFrameModel):
    """Schema para população por município (Tabela 9514)."""

    municipio: Series[str] = pa.Field(nullable=False, description="Nome do município normalizado")
    populacao_total: Series[int] = pa.Field(ge=0, description="População total Censo 2022")

    class Config:
        strict = False
        coerce = True


class SidraSaneamentoSchema(pa.DataFrameModel):
    """Schema para saneamento por município (Tabela 9860)."""

    municipio: Series[str] = pa.Field(nullable=False)
    dom_total: Series[float] = pa.Field(ge=0, description="Total de domicílios")
    dom_adequado_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True, description="% domicílios com saneamento adequado")
    perc_saneamento_adequado: Series[float] = pa.Field(
        ge=0, le=100, nullable=True, description="% saneamento adequado"
    )

    class Config:
        strict = False
        coerce = True


class SidraConsolidadoSchema(pa.DataFrameModel):
    """Schema consolidado: população + saneamento + vulnerabilidade."""

    municipio: Series[str] = pa.Field(nullable=False)
    populacao_total: Series[int] = pa.Field(ge=0)
    perc_saneamento_adequado: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    perc_vulnerabilidade: Series[float] = pa.Field(ge=0, le=100)
    classe_vulnerabilidade: Series[str] = pa.Field(
        isin=["CRITICA", "ALTA", "MODERADA", "BAIXA", "SEM DADOS"]
    )

    class Config:
        strict = False
        coerce = True


# ════════════════════════════════════════════════════════════════════════════════
# SCHEMAS — NASA POWER
# ════════════════════════════════════════════════════════════════════════════════

class NasaPowerRecordSchema(pa.DataFrameModel):
    """Schema para cada registro diário NASA POWER."""

    estacao: Series[str] = pa.Field(nullable=False)
    latitude: Series[float] = pa.Field(ge=-90, le=90)
    longitude: Series[float] = pa.Field(ge=-180, le=180)
    data: Series[Any] = pa.Field(description="Data do registro (datetime)")
    
    # Radiação Solar e Energia (o forte da NASA)
    rad_solar_todo_céu_kwh_m2_dia: Series[float] = pa.Field(ge=0, nullable=True, description="ALLSKY_SFC_SW_DWN - Radiação solar incidente onda curta céu aberto")
    rad_solar_céu_limpo_kwh_m2_dia: Series[float] = pa.Field(ge=0, nullable=True, description="CLRSKY_SFC_SW_DWN - Radiação solar céu limpo")
    rad_onda_longa_kwh_m2_dia: Series[float] = pa.Field(ge=0, nullable=True, description="ALLSKY_SFC_LW_DWN - Radiação onda longa incidente")
    indice_claridade_insolacao: Series[float] = pa.Field(ge=0, le=1, nullable=True, description="ALLSKY_KT - Índice de claridade (Clearness Index)")
    rad_direta_superficie: Series[float] = pa.Field(ge=0, nullable=True, description="Radiação direta na superfície")
    rad_difusa_superficie: Series[float] = pa.Field(ge=0, nullable=True, description="Radiação difusa na superfície")
    
    # Temperatura e Umidade
    t2m_media: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="T2M - Temperatura média ar 2m (°C)")
    t2m_max: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="T2M_MAX - Temperatura máxima ar 2m (°C)")
    t2m_min: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="T2M_MIN - Temperatura mínima ar 2m (°C)")
    t2m_orvalho: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="T2MDEW - Ponto de orvalho 2m (°C)")
    t2m_bulbo_umido: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="T2MWET - Bulbo úmido 2m (°C)")
    ts_superficie: Series[float] = pa.Field(ge=-60, le=60, nullable=True, description="TS - Temperatura pele/superfície solo (°C)")
    rh2m: Series[float] = pa.Field(ge=0, le=100, nullable=True, description="RH2M - Umidade relativa 2m (%)")
    qv2m: Series[float] = pa.Field(ge=0, nullable=True, description="QV2M - Umidade específica 2m (g/kg)")
    
    # Precipitação e Umidade do Solo (Balanço Hídrico)
    precipitacao_mm: Series[float] = pa.Field(ge=0, nullable=True, description="PRECTOTCORR - Precipitação total corrigida (mm/dia)")
    umidade_solo_superficial: Series[float] = pa.Field(ge=0, le=1, nullable=True, description="GWETTOP - Umidade solo 0-5cm (adimensional)")
    umidade_solo_radicular: Series[float] = pa.Field(ge=0, le=1, nullable=True, description="GWETROOT - Umidade solo zona radicular 0-100cm")
    umidade_solo_perfil: Series[float] = pa.Field(ge=0, le=1, nullable=True, description="GWETPROF - Umidade solo perfil total")
    evaporacao_mm: Series[float] = pa.Field(ge=0, nullable=True, description="EVAP - Evaporação/evapotranspiração (mm/dia)")
    
    # Vento e Pressão Atmosférica
    vento_velocidade_10m: Series[float] = pa.Field(ge=0, nullable=True, description="WS10M - Velocidade vento 10m (m/s)")
    vento_velocidade_50m: Series[float] = pa.Field(ge=0, nullable=True, description="WS50M - Velocidade vento 50m (m/s)")
    vento_direcao_10m: Series[float] = pa.Field(ge=0, le=360, nullable=True, description="WD10M - Direção vento 10m (graus)")
    vento_direcao_50m: Series[float] = pa.Field(ge=0, le=360, nullable=True, description="WD50M - Direção vento 50m (graus)")
    vento_10m_max: Series[float] = pa.Field(ge=0, nullable=True, description="WS10M_MAX - Máxima velocidade vento 10m")
    vento_10m_min: Series[float] = pa.Field(ge=0, nullable=True, description="WS10M_MIN - Mínima velocidade vento 10m")
    pressao_superficie_kpa: Series[float] = pa.Field(ge=80, le=110, nullable=True, description="PS - Pressão atmosférica superfície (kPa)")
    
    # Metadados
    indice_saturacao: Series[float] = pa.Field(ge=0, le=1, nullable=True)
    classe_saturacao: Series[str] = pa.Field(
        isin=["CRITICO", "ATENCAO", "NORMAL", "SEM DADOS"]
    )
    janela: Series[str] = pa.Field(isin=["historico", "recente"])

    class Config:
        strict = False
        coerce = True


# ════════════════════════════════════════════════════════════════════════════════
# SCHEMAS — OPEN-METEO
# ════════════════════════════════════════════════════════════════════════════════

class OpenMeteoRecordSchema(pa.DataFrameModel):
    """Schema para registro de dados meteorológicos Open-Meteo."""

    estacao: Series[str] = pa.Field(nullable=False)
    latitude: Series[float] = pa.Field(ge=-90, le=90)
    longitude: Series[float] = pa.Field(ge=-180, le=180)
    data: Series[Any] = pa.Field(description="Data do registro (datetime)")
    # Precipitação
    precipitacao_mm: Series[float] = pa.Field(ge=0, nullable=True)
    probabilidade_precipitacao_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    horas_precipitacao: Series[float] = pa.Field(ge=0, nullable=True)
    neve_mm: Series[float] = pa.Field(ge=0, nullable=True)
    neve_equivalente_agua_mm: Series[float] = pa.Field(ge=0, nullable=True)
    # Temperatura
    temperatura_2m: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    temperatura_2m_max: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    temperatura_2m_min: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    sensacao_termica: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    ponto_orvalho_2m: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    # Umidade
    umidade_relativa_2m: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    umidade_relativa_2m_media: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    # Pressão
    pressao_superficie_hpa: Series[float] = pa.Field(ge=800, le=1100, nullable=True)
    pressao_nivel_mar_hpa: Series[float] = pa.Field(ge=800, le=1100, nullable=True)
    # Nuvens
    nebulosidade_total_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    nebulosidade_baixa_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    nebulosidade_media_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    nebulosidade_alta_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    # Visibilidade e tempo
    visibilidade_m: Series[float] = pa.Field(ge=0, nullable=True)
    codigo_tempo_wmo: Series[int] = pa.Field(ge=0, le=99, nullable=True)
    # Solo - Temperatura (profundidades padrão Open-Meteo)
    solo_temperatura_0cm: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    solo_temperatura_6cm: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    solo_temperatura_18cm: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    solo_temperatura_54cm: Series[float] = pa.Field(ge=-60, le=60, nullable=True)
    # Solo - Umidade volumétrica (camadas Open-Meteo)
    solo_umidade_0_1cm: Series[float] = pa.Field(ge=0, le=1, nullable=True)
    solo_umidade_1_3cm: Series[float] = pa.Field(ge=0, le=1, nullable=True)
    solo_umidade_3_9cm: Series[float] = pa.Field(ge=0, le=1, nullable=True)
    solo_umidade_9_27cm: Series[float] = pa.Field(ge=0, le=1, nullable=True)
    solo_umidade_27_81cm: Series[float] = pa.Field(ge=0, le=1, nullable=True)
    # Agrometeorologia
    et0_fao_evapotranspiracao_mm: Series[float] = pa.Field(ge=0, nullable=True)
    deficit_pressao_vapor_kpa: Series[float] = pa.Field(ge=0, nullable=True)
    prob_molhamento_foliar_pct: Series[float] = pa.Field(ge=0, le=100, nullable=True)
    graus_dia_crescimento: Series[float] = pa.Field(ge=0, nullable=True)
    # Radiação Solar
    radiacao_curta_wm2: Series[float] = pa.Field(ge=0, nullable=True)  # GHI
    radiacao_direta_wm2: Series[float] = pa.Field(ge=0, nullable=True)  # DNI
    radiacao_difusa_wm2: Series[float] = pa.Field(ge=0, nullable=True)  # DHI
    radiacao_inclinada_wm2: Series[float] = pa.Field(ge=0, nullable=True)  # GTI
    duracao_insolacao_s: Series[float] = pa.Field(ge=0, nullable=True)
    indice_uv: Series[float] = pa.Field(ge=0, nullable=True)
    indice_uv_ceu_limpo: Series[float] = pa.Field(ge=0, nullable=True)
    # Vento - Múltiplas alturas
    vento_velocidade_10m_ms: Series[float] = pa.Field(ge=0, nullable=True)
    vento_direcao_10m_graus: Series[float] = pa.Field(ge=0, le=360, nullable=True)
    vento_rajada_10m_ms: Series[float] = pa.Field(ge=0, nullable=True)
    vento_velocidade_80m_ms: Series[float] = pa.Field(ge=0, nullable=True)
    vento_direcao_80m_graus: Series[float] = pa.Field(ge=0, le=360, nullable=True)
    vento_velocidade_120m_ms: Series[float] = pa.Field(ge=0, nullable=True)
    vento_direcao_120m_graus: Series[float] = pa.Field(ge=0, le=360, nullable=True)
    vento_velocidade_180m_ms: Series[float] = pa.Field(ge=0, nullable=True)
    vento_direcao_180m_graus: Series[float] = pa.Field(ge=0, le=360, nullable=True)
    # Metadados
    tipo: Series[str] = pa.Field(isin=["historico", "previsao"])

    class Config:
        strict = False
        coerce = True


# ════════════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS DE VALIDAÇÃO
# ════════════════════════════════════════════════════════════════════════════════

def safe_validate(df: DataFrame[Any], schema: type[pa.DataFrameModel]) -> tuple[bool, DataFrame[Any] | None, str | None]:
    """Valida DataFrame com schema Pandera, retorna (sucesso, df_validado, erro)."""
    try:
        validated = schema.validate(df, lazy=True)
        return True, validated, None
    except pa.errors.SchemaErrors as e:
        error_msg = f"Validação Pandera falhou: {e.failure_cases.to_string() if hasattr(e, 'failure_cases') else str(e)}"
        logger.warning(error_msg)
        return False, None, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado na validação: {e}"
        logger.exception(error_msg)
        return False, None, error_msg


def validate_or_warn(df: DataFrame[Any], schema: type[pa.DataFrameModel], context: str = "") -> DataFrame[Any]:
    """Valida e loga warning se falhar, retorna df original."""
    ok, validated, err = safe_validate(df, schema)
    if ok and validated is not None:
        return validated
    if not ok:
        logger.warning(f"[{context}] Schema validation failed, returning unvalidated data: {err}")
    return df