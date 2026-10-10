"""SISTEMA ASI — REGISTRY CENTRALIZADO DE APIs EXTERNAS
Versão: 1.1 — Health checks, configuração unificada, discovery de APIs
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.api.base import APIClient, APIConfig, APIResponse
from src.api.ibge_sidra import IBGE_SIDRA_Client, IBGE_SIDRA_CONFIG, IBGE_SIDRA_METADATA
from src.api.nasa_power import NASA_POWER_Client, NASA_POWER_CONFIG, NASA_POWER_METADATA
from src.api.open_meteo import (
    OpenMeteoClient,
    OPEN_METEO_CONFIG,
    OPEN_METEO_FORECAST_CONFIG,
    OPEN_METEO_METADATA,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class APIMetadata:
    """Metadados descritivos de uma API registrada."""

    name: str
    display_name: str
    description: str
    version: str
    provider_url: str
    auth_required: bool = False
    rate_limit_info: str = ""
    parameters: list[str] = field(default_factory=list)


class APIRegistry:
    """Registry singleton para gerenciar todas as APIs externas do ASI."""

    _instance: APIRegistry | None = None
    _clients: dict[str, APIClient] = {}
    _metadata: dict[str, APIMetadata] = {}

    def __new__(cls) -> APIRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(
        self,
        client: APIClient,
        metadata: APIMetadata,
    ) -> None:
        """Registra um cliente de API no registry."""
        self._clients[metadata.name] = client
        self._metadata[metadata.name] = metadata
        logger.info(f"API registrada: {metadata.display_name} ({metadata.name})")

    def get_client(self, name: str) -> APIClient | None:
        """Recupera cliente por nome."""
        return self._clients.get(name)

    def get_metadata(self, name: str) -> APIMetadata | None:
        """Recupera metadados por nome."""
        return self._metadata.get(name)

    def list_apis(self) -> list[APIMetadata]:
        """Lista todas as APIs registradas."""
        return list(self._metadata.values())

    def health_check_all(self) -> dict[str, APIResponse]:
        """Executa health check em todas as APIs registradas."""
        results = {}
        for name, client in self._clients.items():
            try:
                results[name] = client.health_check()
            except Exception as e:
                logger.exception(f"Health check falhou para {name}")
                results[name] = APIResponse(
                    success=False,
                    error=f"Health check exception: {e}",
                    correlation_id="health-check",
                )
        return results

    def get_healthy_apis(self) -> list[str]:
        """Retorna nomes das APIs que responderam saudáveis no último health check."""
        healthy = []
        for name, response in self.health_check_all().items():
            if response.success:
                healthy.append(name)
        return healthy

    def register_default_apis(self) -> None:
        """Registra as APIs padrão do ASI (Open-Meteo, IBGE SIDRA, NASA POWER)."""
        # Open-Meteo (Archive)
        open_meteo_client = OpenMeteoClient(OPEN_METEO_CONFIG)
        open_meteo_meta = APIMetadata(
            name="open_meteo",
            display_name="Open-Meteo (Histórico)",
            description="API meteorológica open-source para precipitação histórica",
            version="1.0",
            provider_url="https://open-meteo.com/",
            auth_required=False,
            rate_limit_info="2 req/s, 60 req/min",
            parameters=["precipitation", "temperature_2m_max", "temperature_2m_min", "relative_humidity_2m_mean"],
        )
        self.register(open_meteo_client, open_meteo_meta)

        # Open-Meteo (Forecast)
        open_meteo_forecast_client = OpenMeteoClient(OPEN_METEO_FORECAST_CONFIG)
        open_meteo_forecast_meta = APIMetadata(
            name="open_meteo_forecast",
            display_name="Open-Meteo (Previsão)",
            description="API meteorológica open-source para previsão de precipitação",
            version="1.0",
            provider_url="https://open-meteo.com/",
            auth_required=False,
            rate_limit_info="2 req/s, 60 req/min",
            parameters=["precipitation", "temperature_2m_max", "temperature_2m_min"],
        )
        self.register(open_meteo_forecast_client, open_meteo_forecast_meta)

        # NASA POWER
        nasa_client = NASA_POWER_Client(NASA_POWER_CONFIG)
        nasa_meta = APIMetadata(
            name="nasa_power",
            display_name="NASA POWER",
            description="Dados agrometeorológicos globais MERRA-2 (radiação, temperatura, solo, vento, precipitação)",
            version="2.0",
            provider_url="https://power.larc.nasa.gov/",
            auth_required=False,
            rate_limit_info="0.5 req/s, 10 req/min",
            parameters=[
                "Radiação solar (ALLSKY_SFC_SW_DWN, CLRSKY_SFC_SW_DWN)",
                "Temperatura (T2M, T2M_MAX, T2M_MIN, T2MDEW, T2MWET, TS)",
                "Umidade (RH2M, QV2M)",
                "Precipitação (PRECTOTCORR)",
                "Umidade solo (GWETTOP, GWETROOT, GWETPROF)",
                "Evaporação (EVAP)",
                "Vento (WS10M, WS50M, WD10M, WD50M)",
                "Pressão (PS)",
            ],
        )
        self.register(nasa_client, nasa_meta)

        # IBGE SIDRA
        ibge_client = IBGE_SIDRA_Client(IBGE_SIDRA_CONFIG)
        ibge_meta = APIMetadata(
            name="ibge_sidra",
            display_name="IBGE SIDRA",
            description="Sistema IBGE de Recuperação Automática - Dados censitários e socioeconômicos",
            version="1.0",
            provider_url="https://sidra.ibge.gov.br/",
            auth_required=False,
            rate_limit_info="0.5 req/s, 15 req/min",
            parameters=[
                "População total (Censo 2022)",
                "Saneamento adequado (% domicílios)",
                "Rendimento médio",
                "Escolaridade",
            ],
        )
        self.register(ibge_client, ibge_meta)


# ════════════════════════════════════════════════════════════════════════════════
# REGISTRY GLOBAL (Singleton)
# ════════════════════════════════════════════════════════════════════════════════

registry = APIRegistry()


def get_registry() -> APIRegistry:
    """Retorna a instância singleton do registry."""
    return registry


def initialize_registry() -> APIRegistry:
    """Inicializa o registry com as APIs padrão do ASI."""
    registry.register_default_apis()
    logger.info("API Registry inicializado com APIs padrão: Open-Meteo, IBGE SIDRA")
    return registry