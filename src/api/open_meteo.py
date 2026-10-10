"""SISTEMA ASI — CLIENTE OPEN-METEO
Versão: 2.0 — Dados meteorológicos completos com rate limiting, cache e validação
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from src.api.base import APIClient, APIConfig, APIResponse, streamlit_cache_data
from src.api.schemas import OpenMeteoRecordSchema, validate_or_warn

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO OPEN-METEO
# ════════════════════════════════════════════════════════════════════════════════

# Parâmetros horários disponíveis na Open-Meteo (conforme documentação)
HOURLY_PARAMS = {
    # Precipitação
    "precipitation": "precipitacao_mm",
    "precipitation_probability": "probabilidade_precipitacao_pct",
    "precipitation_hours": "horas_precipitacao",
    "snowfall": "neve_mm",
    "snowfall_water_equivalent": "neve_equivalente_agua_mm",
    # Temperatura
    "temperature_2m": "temperatura_2m",
    "temperature_2m_max": "temperatura_2m_max",
    "temperature_2m_min": "temperatura_2m_min",
    "apparent_temperature": "sensacao_termica",
    "dew_point_2m": "ponto_orvalho_2m",
    # Umidade
    "relative_humidity_2m": "umidade_relativa_2m",
    "relative_humidity_2m_mean": "umidade_relativa_2m_media",
    # Pressão
    "pressure_msl": "pressao_nivel_mar_hpa",
    "surface_pressure": "pressao_superficie_hpa",
    # Nuvens
    "cloud_cover": "nebulosidade_total_pct",
    "cloud_cover_low": "nebulosidade_baixa_pct",
    "cloud_cover_mid": "nebulosidade_media_pct",
    "cloud_cover_high": "nebulosidade_alta_pct",
    # Visibilidade e tempo
    "visibility": "visibilidade_m",
    "weather_code": "codigo_tempo_wmo",
    # Solo - Temperatura
    "soil_temperature_0cm": "solo_temperatura_0cm",
    "soil_temperature_6cm": "solo_temperatura_6cm",
    "soil_temperature_18cm": "solo_temperatura_18cm",
    "soil_temperature_54cm": "solo_temperatura_54cm",
    # Solo - Umidade volumétrica
    "soil_moisture_0_to_1cm": "solo_umidade_0_1cm",
    "soil_moisture_1_to_3cm": "solo_umidade_1_3cm",
    "soil_moisture_3_to_9cm": "solo_umidade_3_9cm",
    "soil_moisture_9_to_27cm": "solo_umidade_9_27cm",
    "soil_moisture_27_to_81cm": "solo_umidade_27_81cm",
    # Agrometeorologia
    "et0_fao_evapotranspiration": "et0_fao_evapotranspiracao_mm",
    "vapor_pressure_deficit": "deficit_pressao_vapor_kpa",
    "leaf_wetness_probability": "prob_molhamento_foliar_pct",
    "growing_degree_days": "graus_dia_crescimento",
    # Radiação Solar
    "shortwave_radiation": "radiacao_curta_wm2",  # GHI
    "direct_radiation": "radiacao_direta_wm2",  # DNI
    "diffuse_radiation": "radiacao_difusa_wm2",  # DHI
    "direct_normal_irradiance": "radiacao_inclinada_wm2",  # GTI (aprox)
    "sunshine_duration": "duracao_insolacao_s",
    "uv_index": "indice_uv",
    "uv_index_clear_sky": "indice_uv_ceu_limpo",
    # Vento - 10m
    "wind_speed_10m": "vento_velocidade_10m_ms",
    "wind_direction_10m": "vento_direcao_10m_graus",
    "wind_gusts_10m": "vento_rajada_10m_ms",
    # Vento - 80m
    "wind_speed_80m": "vento_velocidade_80m_ms",
    "wind_direction_80m": "vento_direcao_80m_graus",
    # Vento - 120m
    "wind_speed_120m": "vento_velocidade_120m_ms",
    "wind_direction_120m": "vento_direcao_120m_graus",
    # Vento - 180m
    "wind_speed_180m": "vento_velocidade_180m_ms",
    "wind_direction_180m": "vento_direcao_180m_graus",
}

# Parâmetros padrão para requisições leves (histórico - archive API)
# Note: archive API usa nomes diferentes de forecast API
DEFAULT_HOURLY_HISTORICAL = [
    "precipitation",
    "precipitation_probability",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m",      # Archive usa relative_humidity_2m (não _mean)
    "wind_speed_10m",
    "et0_fao_evapotranspiration",
    "shortwave_radiation",
    "surface_pressure",
    "cloud_cover",
    "dew_point_2m",
    "soil_temperature_0cm",
    "soil_moisture_0_to_1cm",
]

# Parâmetros padrão para previsão (forecast API)
DEFAULT_HOURLY_FORECAST = [
    "precipitation",
    "precipitation_probability",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m",  # Forecast usa relative_humidity_2m (não _mean)
    "wind_speed_10m",
    "wind_gusts_10m",
    "et0_fao_evapotranspiration",
    "shortwave_radiation",
    "cloud_cover",
    "weather_code",
]

# Parâmetros completos (todos - para análise profunda)
ALL_HOURLY_PARAMS = list(HOURLY_PARAMS.keys())


OPEN_METEO_CONFIG = APIConfig(
    name="open_meteo",
    base_url="https://archive-api.open-meteo.com/v1/archive",
    timeout=60,
    max_retries=3,
    backoff_factor=1.0,
    rate_limit_rps=2.0,      # 2 req/s - conservador
    rate_limit_rpm=60,       # 60 req/min
    cache_ttl_seconds=3600,  # 1 hora
    headers={
        "User-Agent": "ASI-Flood-Susceptibility/2.0 (https://github.com/LuciolLima/ASI)"
    },
)

OPEN_METEO_FORECAST_CONFIG = APIConfig(
    name="open_meteo_forecast",
    base_url="https://api.open-meteo.com/v1/forecast",
    timeout=60,
    max_retries=3,
    backoff_factor=1.0,
    rate_limit_rps=2.0,
    rate_limit_rpm=60,
    cache_ttl_seconds=1800,  # 30 min para previsão
    headers={
        "User-Agent": "ASI-Flood-Susceptibility/2.0 (https://github.com/LuciolLima/ASI)"
    },
)

OPEN_METEO_METADATA = {
    "name": "open_meteo",
    "display_name": "Open-Meteo",
    "description": "API meteorológica open-source para dados históricos, previsão e agrometeorologia",
    "version": "2.0",
    "provider_url": "https://open-meteo.com/",
    "auth_required": False,
    "rate_limit_info": "2 req/s, 60 req/min (auto-limitado pelo cliente)",
    "parameters": [
        "Precipitação (mm, probabilidade, neve)",
        "Temperatura (2m, max, min, sensação, ponto de orvalho)",
        "Umidade relativa (2m, média)",
        "Pressão (superfície, nível do mar)",
        "Nuvens (total, baixa, média, alta)",
        "Visibilidade, código tempo WMO",
        "Solo (temperatura 0/6/18/54cm, umidade 5 camadas)",
        "Agrometeorologia (ET0, VPD, molhamento foliar, graus-dia)",
        "Radiação solar (GHI, DNI, DHI, UV, insolação)",
        "Vento (10m, 80m, 120m, 180m - velocidade, direção, rajada)",
    ],
}

# Estações de referência para PE (municípios-chave)
PE_STATIONS = {
    "RECIFE": {"lat": -8.0539, "lon": -34.8811},
    "CABO_DE_SANTO_AGOSTINHO": {"lat": -8.2833, "lon": -35.0333},
    "JABOATAO_DOS_GUARARAPES": {"lat": -8.1167, "lon": -34.8667},
    "OLINDA": {"lat": -7.9833, "lon": -34.8500},
    "PAULISTA": {"lat": -7.9333, "lon": -34.8833},
    "CARUARU": {"lat": -8.2833, "lon": -35.9667},
    "PETROLINA": {"lat": -9.3833, "lon": -40.5000},
    "GARANHUNS": {"lat": -8.8833, "lon": -36.5000},
    "VITORIA_DE_SANTO_ANTAO": {"lat": -8.1167, "lon": -35.3000},
    "GOIANA": {"lat": -7.5667, "lon": -34.9833},
}


# ════════════════════════════════════════════════════════════════════════════════
# CLIENTE OPEN-METEO
# ════════════════════════════════════════════════════════════════════════════════

class OpenMeteoClient(APIClient):
    """Cliente para Open-Meteo API (histórico + previsão + agrometeorologia)."""

    def __init__(self, config: APIConfig = OPEN_METEO_CONFIG):
        super().__init__(config)

    def health_check(self) -> APIResponse:
        """Verifica se a API está acessível com uma requisição mínima."""
        resp = self.get(
            endpoint="",
            params={
                "latitude": -8.0539,
                "longitude": -34.8811,
                "hourly": "precipitation",
                "forecast_days": 1,
            },
            use_cache=False,
        )
        if resp.success:
            return APIResponse(
                success=True,
                data={"status": "healthy", "api": "open_meteo"},
                status_code=resp.status_code,
                response_time_ms=resp.response_time_ms,
                correlation_id=resp.correlation_id,
            )
        return resp

    def fetch_data(self, **kwargs: Any) -> APIResponse:
        """Método abstrato obrigatório - delega para fetch_precipitation."""
        return self.fetch_precipitation(**kwargs)

    def _fetch_raw(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        hourly_params: list[str] | None = None,
        use_archive: bool = True,
        daily_params: list[str] | None = None,
    ) -> APIResponse:
        """Requisição bruta para Open-Meteo (archive ou forecast)."""
        if hourly_params is None:
            hourly_params = DEFAULT_HOURLY_HISTORICAL if use_archive else DEFAULT_HOURLY_FORECAST

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(hourly_params),
            "timezone": "America/Recife",
        }

        if daily_params:
            params["daily"] = ",".join(daily_params)

        config = self.config if use_archive else OPEN_METEO_FORECAST_CONFIG
        original_config = self.config
        self.config = config
        try:
            return self.get(endpoint="", params=params)
        finally:
            self.config = original_config

    def fetch_precipitation(
        self,
        station_name: str = "RECIFE",
        days_back: int = 30,
        hourly_params: list[str] | None = None,
        daily_params: list[str] | None = None,
    ) -> APIResponse:
        """Busca dados meteorológicos históricos para uma estação."""
        if station_name not in PE_STATIONS:
            return APIResponse(
                success=False,
                error=f"Estação desconhecida: {station_name}. Disponíveis: {list(PE_STATIONS.keys())}",
            )

        coords = PE_STATIONS[station_name]
        end_date = date.today() - timedelta(days=1)  # Ontem (dados completos)
        start_date = end_date - timedelta(days=days_back)

        resp = self._fetch_raw(
            latitude=coords["lat"],
            longitude=coords["lon"],
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            hourly_params=hourly_params,
            daily_params=daily_params,
            use_archive=True,
        )

        if not resp.success:
            return resp

        return self._transform_to_dataframe(resp, station_name, coords)

    def fetch_forecast(
        self,
        station_name: str = "RECIFE",
        forecast_days: int = 7,
        hourly_params: list[str] | None = None,
        daily_params: list[str] | None = None,
    ) -> APIResponse:
        """Busca previsão meteorológica."""
        if station_name not in PE_STATIONS:
            return APIResponse(
                success=False,
                error=f"Estação desconhecida: {station_name}",
            )

        if forecast_days > 16:
            forecast_days = 16  # Limite da API

        coords = PE_STATIONS[station_name]

        if hourly_params is None:
            hourly_params = DEFAULT_HOURLY_FORECAST

        resp = self._fetch_raw(
            latitude=coords["lat"],
            longitude=coords["lon"],
            start_date=date.today().isoformat(),
            end_date=(date.today() + timedelta(days=forecast_days - 1)).isoformat(),
            hourly_params=hourly_params,
            daily_params=daily_params,
            use_archive=False,
        )

        if not resp.success:
            return resp

        return self._transform_to_dataframe(resp, station_name, coords, tipo="previsao")

    def fetch_all_parameters(
        self,
        station_name: str = "RECIFE",
        days_back: int = 7,
    ) -> APIResponse:
        """Busca TODOS os parâmetros disponíveis (requisição pesada - use com parcimônia)."""
        if station_name not in PE_STATIONS:
            return APIResponse(
                success=False,
                error=f"Estação desconhecida: {station_name}",
            )

        coords = PE_STATIONS[station_name]
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=days_back)

        # Open-Meteo limita parâmetros por requisição - divide em chunks
        chunk_size = 50
        all_params = ALL_HOURLY_PARAMS
        all_data = []

        for i in range(0, len(all_params), chunk_size):
            chunk = all_params[i:i + chunk_size]
            logger.info(f"[open_meteo] Buscando chunk {i//chunk_size + 1}/{(len(all_params)-1)//chunk_size + 1} ({len(chunk)} parâmetros)")

            resp = self._fetch_raw(
                latitude=coords["lat"],
                longitude=coords["lon"],
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                hourly_params=chunk,
                use_archive=True,
            )

            if not resp.success:
                logger.warning(f"[open_meteo] Chunk falhou: {resp.error}")
                continue

            df_chunk = self._transform_raw_to_df(resp.data, station_name, coords)
            if df_chunk is not None and not df_chunk.empty:
                all_data.append(df_chunk)

            # Pausa entre chunks
            import time
            time.sleep(1.0)

        if not all_data:
            return APIResponse(
                success=False,
                error="Todos os chunks falharam",
            )

        # Merge todos os chunks pelo timestamp
        combined = all_data[0]
        for df in all_data[1:]:
            combined = combined.merge(df, on=["estacao", "latitude", "longitude", "data", "tipo"], how="outer")

        combined = validate_or_warn(combined, OpenMeteoRecordSchema, f"open_meteo_all_{station_name}")

        return APIResponse(
            success=True,
            data=combined,
        )

    def _transform_raw_to_df(
        self,
        data: dict,
        station_name: str,
        coords: dict[str, float],
        tipo: str = "historico",
    ) -> pd.DataFrame | None:
        """Transforma resposta JSON bruta em DataFrame (sem validação)."""
        try:
            hourly = data.get("hourly", {})
            if not hourly or "time" not in hourly:
                return None

            times = hourly["time"]
            records = []

            for i, timestamp in enumerate(times):
                record = {
                    "estacao": station_name,
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "data": pd.to_datetime(timestamp),
                    "tipo": tipo,
                }

                for param, values in hourly.items():
                    if param != "time" and i < len(values):
                        col_name = HOURLY_PARAMS.get(param, param.lower().replace("-", "_"))
                        record[col_name] = values[i]

                records.append(record)

            return pd.DataFrame(records)

        except Exception as e:
            logger.exception(f"[open_meteo] Erro transformando dados brutos: {e}")
            return None

    def _transform_to_dataframe(
        self,
        resp: APIResponse,
        station_name: str,
        coords: dict[str, float],
        tipo: str = "historico",
    ) -> APIResponse:
        """Transforma resposta JSON da Open-Meteo em DataFrame validado."""
        try:
            data = resp.data
            hourly = data.get("hourly", {})

            if not hourly or "time" not in hourly:
                return APIResponse(
                    success=False,
                    error="Resposta sem dados horários válidos",
                    correlation_id=resp.correlation_id,
                )

            times = hourly["time"]
            records = []

            for i, timestamp in enumerate(times):
                record = {
                    "estacao": station_name,
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "data": pd.to_datetime(timestamp),
                    "tipo": tipo,
                }

                # Mapeia todos os parâmetros disponíveis
                for param, values in hourly.items():
                    if param != "time" and i < len(values):
                        col_name = HOURLY_PARAMS.get(param, param.lower().replace("-", "_"))
                        record[col_name] = values[i]

                records.append(record)

            df = pd.DataFrame(records)

            # Garante que todas as colunas do schema existam (preenche com None se faltando)
            schema_columns = list(OpenMeteoRecordSchema.to_schema().columns.keys())
            for col in schema_columns:
                if col not in df.columns:
                    df[col] = None

            # Reordena colunas conforme schema
            df = df[schema_columns]

            # Valida com schema
            df_validated = validate_or_warn(df, OpenMeteoRecordSchema, f"open_meteo_{station_name}")

            # Log resumo
            precip_col = "precipitacao_mm"
            total_precip = df.get(precip_col, pd.Series([0])).sum() if precip_col in df.columns else 0

            logger.info(
                f"[open_meteo] {station_name} | {tipo} | {len(df)} registros "
                f"({total_precip:.1f} mm total) [{resp.correlation_id}]"
            )

            return APIResponse(
                success=True,
                data=df_validated,
                status_code=resp.status_code,
                response_time_ms=resp.response_time_ms,
                correlation_id=resp.correlation_id,
            )

        except Exception as e:
            logger.exception(f"[open_meteo] Erro transformando dados: {e}")
            return APIResponse(
                success=False,
                error=f"Transformação falhou: {e}",
                correlation_id=resp.correlation_id,
            )

    def fetch_multiple_stations(
        self,
        station_names: list[str] | None = None,
        days_back: int = 30,
        hourly_params: list[str] | None = None,
    ) -> APIResponse:
        """Busca dados de múltiplas estações sequencialmente (respeitando rate limit)."""
        if station_names is None:
            station_names = list(PE_STATIONS.keys())[:5]  # Limita a 5 por padrão

        all_data = []
        errors = []

        for i, station in enumerate(station_names):
            logger.info(f"[open_meteo] Buscando estação {i+1}/{len(station_names)}: {station}")
            resp = self.fetch_precipitation(
                station_name=station,
                days_back=days_back,
                hourly_params=hourly_params,
            )

            if resp.success and resp.data is not None:
                all_data.append(resp.data)
            else:
                errors.append(f"{station}: {resp.error}")

            # Pausa extra entre estações
            if i < len(station_names) - 1:
                import time
                time.sleep(0.5)

        if not all_data:
            return APIResponse(
                success=False,
                error=f"Todas as estações falharam: {errors}",
            )

        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = validate_or_warn(combined_df, OpenMeteoRecordSchema, "open_meteo_multi")

        return APIResponse(
            success=True,
            data=combined_df,
            error="; ".join(errors) if errors else None,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES CACHED PARA STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════════

@streamlit_cache_data(ttl_seconds=3600, show_spinner="Carregando dados meteorológicos históricos (Open-Meteo)...")
def fetch_precipitacao_pe_cached(
    station_name: str = "RECIFE",
    days_back: int = 30,
) -> APIResponse:
    """Função cached para Streamlit - dados meteorológicos históricos (parâmetros padrão)."""
    client = OpenMeteoClient()
    return client.fetch_precipitation(station_name=station_name, days_back=days_back)


@streamlit_cache_data(ttl_seconds=1800, show_spinner="Carregando previsão meteorológica (Open-Meteo)...")
def fetch_precipitacao_forecast_cached(
    station_name: str = "RECIFE",
    forecast_days: int = 7,
) -> APIResponse:
    """Função cached para Streamlit - previsão meteorológica."""
    client = OpenMeteoClient()
    return client.fetch_forecast(station_name=station_name, forecast_days=forecast_days)


@streamlit_cache_data(ttl_seconds=7200, show_spinner="Carregando múltiplas estações (Open-Meteo)...")
def fetch_multi_estacoes_pe_cached(
    station_names: list[str] | None = None,
    days_back: int = 30,
) -> APIResponse:
    """Função cached para Streamlit - múltiplas estações."""
    client = OpenMeteoClient()
    return client.fetch_multiple_stations(station_names=station_names, days_back=days_back)


@streamlit_cache_data(ttl_seconds=21600, show_spinner="Carregando TODOS parâmetros meteorológicos (Open-Meteo)...")
def fetch_todos_parametros_pe_cached(
    station_name: str = "RECIFE",
    days_back: int = 7,
) -> APIResponse:
    """Função cached para Streamlit - TODOS os parâmetros (pesado, cache 6h)."""
    client = OpenMeteoClient()
    return client.fetch_all_parameters(station_name=station_name, days_back=days_back)