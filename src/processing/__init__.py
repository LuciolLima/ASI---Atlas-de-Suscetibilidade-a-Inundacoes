"""SISTEMA ASI - PROCESSING MODULE
Versão: 3.0 — Integração com nova arquitetura de APIs
"""

from src.processing.data_loader import (
    _normalizar_municipio,
    calcular_indice_risco_bairro,
    correlacionar_datasets,
    load_defesa_civil,
    load_eventos_inundacao,
    load_geospatial_dataset,
    load_ibge_sidra,
    load_precipitacao,
    load_precipitacao_realtime,
)

__all__ = [
    "load_geospatial_dataset",
    "load_precipitacao",
    "load_eventos_inundacao",
    "load_precipitacao_realtime",
    "load_ibge_sidra",
    "load_defesa_civil",
    "calcular_indice_risco_bairro",
    "correlacionar_datasets",
    "_normalizar_municipio",
]
