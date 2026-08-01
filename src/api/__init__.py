"""SISTEMA ASI — API EXTERNAS HUB
Versão: 1.3 — Interface unificada para IBGE SIDRA, NASA POWER, Open-Meteo, CEMADEN, INMET
"""

from __future__ import annotations

from src.api.base import APIClient, APIConfig, APIResponse, RateLimiter, streamlit_cache_data
from src.api.ibge_sidra import (
    IBGE_SIDRA_Client,
    fetch_populacao_pe_cached,
    fetch_saneamento_pe_cached,
    fetch_sidra_consolidado_cached,
    fetch_sidra_todos_municipios_pe_cached,
)
from src.api.nasa_power import (
    NASA_POWER_Client,
    fetch_nasa_power_pe_cached,
    fetch_nasa_power_historico_cached,
    fetch_nasa_power_multi_cached,
)
from src.api.open_meteo import (
    OpenMeteoClient,
    fetch_precipitacao_pe_cached,
    fetch_precipitacao_forecast_cached,
    fetch_multi_estacoes_pe_cached,
    fetch_todos_parametros_pe_cached,
)
from src.api.registry import (
    APIMetadata,
    APIRegistry,
    get_registry,
    initialize_registry,
)
from src.api.schemas import (
    NasaPowerRecordSchema,
    OpenMeteoRecordSchema,
    SidraConsolidadoSchema,
    SidraPopulacaoSchema,
    SidraSaneamentoSchema,
    safe_validate,
    validate_or_warn,
)

__all__ = [
    # Base
    "APIClient",
    "APIConfig",
    "APIResponse",
    "RateLimiter",
    "streamlit_cache_data",
    # IBGE SIDRA
    "IBGE_SIDRA_Client",
    "fetch_populacao_pe_cached",
    "fetch_saneamento_pe_cached",
    "fetch_sidra_consolidado_cached",
    "fetch_sidra_todos_municipios_pe_cached",
    # NASA POWER
    "NASA_POWER_Client",
    "fetch_nasa_power_pe_cached",
    "fetch_nasa_power_historico_cached",
    "fetch_nasa_power_multi_cached",
    # Open-Meteo
    "OpenMeteoClient",
    "fetch_precipitacao_pe_cached",
    "fetch_precipitacao_forecast_cached",
    "fetch_multi_estacoes_pe_cached",
    "fetch_todos_parametros_pe_cached",
    # Registry
    "APIMetadata",
    "APIRegistry",
    "get_registry",
    "initialize_registry",
    # Schemas
    "SidraConsolidadoSchema",
    "SidraPopulacaoSchema",
    "SidraSaneamentoSchema",
    "NasaPowerRecordSchema",
    "OpenMeteoRecordSchema",
    "safe_validate",
    "validate_or_warn",
]

__version__ = "1.3.0"