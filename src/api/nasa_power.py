"""SISTEMA ASI — CLIENTE NASA POWER
Versão: 2.0 — Dados agrometeorológicos completos MERRA-2 com rate limiting, cache e validação
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from src.api.base import APIClient, APIConfig, APIResponse, streamlit_cache_data
from src.api.schemas import NasaPowerRecordSchema, validate_or_warn

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO NASA POWER
# ════════════════════════════════════════════════════════════════════════════════

# Parâmetros padrão para requisições (os mais essenciais)
DEFAULT_PARAMS = [
    "PRECTOTCORR",      # Precipitação
    "T2M",              # Temperatura média
    "T2M_MAX",          # Temperatura máxima
    "T2M_MIN",          # Temperatura mínima
    "RH2M",             # Umidade relativa
    "T2MDEW",           # Ponto de orvalho
    "GWETTOP",          # Umidade solo superficial
    "GWETROOT",         # Umidade solo radicular
    "GWETPROF",         # Umidade solo perfil
    "ALLSKY_SFC_SW_DWN", # Radiação solar todo céu
    "CLRSKY_SFC_SW_DWN", # Radiação solar céu limpo
    "WS10M",            # Vento 10m
    "WS50M",            # Vento 50m
    "WD10M",            # Direção vento 10m
    "WD50M",            # Direção vento 50m
    "PS",               # Pressão
]

# Parâmetros expandidos (todos disponíveis - removendo os que dão erro 422)
ALL_PARAMS = [
    "PRECTOTCORR",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "T2MDEW",
    "T2MWET",
    "TS",
    "QV2M",
    "GWETTOP",
    "GWETROOT",
    "GWETPROF",
    "ALLSKY_SFC_SW_DWN",
    "CLRSKY_SFC_SW_DWN",
    "ALLSKY_SFC_LW_DWN",
    "ALLSKY_KT",
    "WS10M",
    "WS50M",
    "WD10M",
    "WD50M",
    "WS10M_MAX",
    "WS10M_MIN",
    "PS",
]

# Parâmetros disponíveis na NASA POWER (conforme documentação)
NASA_POWER_PARAMS = {
    # Radiação Solar e Energia
    "ALLSKY_SFC_SW_DWN": "rad_solar_todo_céu_kwh_m2_dia",
    "CLRSKY_SFC_SW_DWN": "rad_solar_céu_limpo_kwh_m2_dia",
    "ALLSKY_SFC_LW_DWN": "rad_onda_longa_kwh_m2_dia",
    "ALLSKY_KT": "indice_claridade_insolacao",
    # Temperatura
    "T2M": "t2m_media",
    "T2M_MAX": "t2m_max",
    "T2M_MIN": "t2m_min",
    "T2MDEW": "t2m_orvalho",
    "T2MWET": "t2m_bulbo_umido",
    "TS": "ts_superficie",
    # Umidade
    "RH2M": "rh2m",
    "QV2M": "qv2m",
    # Precipitação e Solo
    "PRECTOTCORR": "precipitacao_mm",
    "GWETTOP": "umidade_solo_superficial",
    "GWETROOT": "umidade_solo_radicular",
    "GWETPROF": "umidade_solo_perfil",
    # Vento
    "WS10M": "vento_velocidade_10m",
    "WS50M": "vento_velocidade_50m",
    "WD10M": "vento_direcao_10m",
    "WD50M": "vento_direcao_50m",
    "WS10M_MAX": "vento_10m_max",
    "WS10M_MIN": "vento_10m_min",
    # Pressão
    "PS": "pressao_superficie_kpa",
}

# Estações de referência para PE
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


NASA_POWER_CONFIG = APIConfig(
    name="nasa_power",
    base_url="https://power.larc.nasa.gov/api/temporal/daily/point",
    timeout=120,
    max_retries=3,
    backoff_factor=2.0,
    rate_limit_rps=0.5,      # 1 req a cada 2s - conservador
    rate_limit_rpm=15,       # 15 req/min
    cache_ttl_seconds=86400, # 24h - dados históricos mudam pouco
    headers={
        "User-Agent": "ASI-Flood-Susceptibility/2.0 (https://github.com/LuciolLima/ASI)",
        "Accept": "application/json",
    },
)

NASA_POWER_METADATA = {
    "name": "nasa_power",
    "display_name": "NASA POWER",
    "description": "Prediction Of Worldwide Energy Resources - Dados MERRA-2 reanálise global",
    "version": "2.0",
    "provider_url": "https://power.larc.nasa.gov/",
    "auth_required": False,
    "rate_limit_info": "0.5 req/s, 15 req/min (auto-limitado)",
    "parameters": [
        "Radiação solar (ALLSKY, CLRSKY, onda longa, índice claridade)",
        "Temperatura (T2M, max, min, orvalho, bulbo úmido, superfície)",
        "Umidade (RH2M, QV2M)",
        "Precipitação corrigida (PRECTOTCORR)",
        "Umidade solo (GWETTOP, GWETROOT, GWETPROF)",
        "Evapotranspiração (EVAP)",
        "Vento (WS10M, WS50M, WD10M, WD50M, max/min)",
        "Pressão superfície (PS)",
    ],
}


# ════════════════════════════════════════════════════════════════════════════════
# CLIENTE NASA POWER
# ════════════════════════════════════════════════════════════════════════════════

class NASA_POWER_Client(APIClient):
    """Cliente para NASA POWER API (temporal daily point)."""

    def __init__(self, config: APIConfig = NASA_POWER_CONFIG):
        super().__init__(config)

    def health_check(self) -> APIResponse:
        """Verifica se a API está acessível."""
        resp = self.get(
            endpoint="",
            params={
                "parameters": "PRECTOTCORR",
                "community": "AG",
                "longitude": -34.8811,
                "latitude": -8.0539,
                "start": "20240101",
                "end": "20240101",
                "format": "JSON",
            },
            use_cache=False,
        )
        if resp.success:
            return APIResponse(
                success=True,
                data={"status": "healthy", "api": "nasa_power"},
                status_code=resp.status_code,
                response_time_ms=resp.response_time_ms,
                correlation_id=resp.correlation_id,
            )
        return resp

    def fetch_data(self, **kwargs: Any) -> APIResponse:
        """Método abstrato obrigatório."""
        return self.fetch_agrometeorologia(**kwargs)

    def _fetch_raw(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        parameters: list[str] | None = None,
    ) -> APIResponse:
        """Requisição bruta para NASA POWER."""
        if parameters is None:
            parameters = DEFAULT_PARAMS

        # NASA POWER usa datas no formato YYYYMMDD
        params = {
            "parameters": ",".join(parameters),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date.replace("-", ""),
            "end": end_date.replace("-", ""),
            "format": "JSON",
        }

        return self.get(endpoint="", params=params)

    def fetch_agrometeorologia(
        self,
        station_name: str = "RECIFE",
        start_date: str | None = None,
        end_date: str | None = None,
        parameters: list[str] | None = None,
    ) -> APIResponse:
        """Busca dados agrometeorológicos para uma estação."""
        if station_name not in PE_STATIONS:
            return APIResponse(
                success=False,
                error=f"Estação desconhecida: {station_name}. Disponíveis: {list(PE_STATIONS.keys())}",
            )

        coords = PE_STATIONS[station_name]

        # Datas padrão: últimos 30 dias se não especificado
        if end_date is None:
            end_date = date.today() - timedelta(days=1)  # NASA tem lag de ~1-2 dias
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        resp = self._fetch_raw(
            latitude=coords["lat"],
            longitude=coords["lon"],
            start_date=start_date,
            end_date=end_date,
            parameters=parameters,
        )

        if not resp.success:
            return resp

        return self._transform_raw_to_df(resp, station_name, coords)

    def fetch_historico_completo(
        self,
        station_name: str = "RECIFE",
        years_back: int = 5,
        parameters: list[str] | None = None,
    ) -> APIResponse:
        """Busca histórico completo (últimos N anos) - divide em chunks de 20 parâmetros."""
        if station_name not in PE_STATIONS:
            return APIResponse(
                success=False,
                error=f"Estação desconhecida: {station_name}",
            )

        coords = PE_STATIONS[station_name]
        end_date = date.today() - timedelta(days=2)
        start_date = end_date - timedelta(days=years_back * 365)

        params_to_use = parameters or ALL_PARAMS
        max_params_per_request = 20  # Limite da API NASA POWER

        all_data = []
        errors = []

        # Divide parâmetros em chunks de 20
        for i in range(0, len(params_to_use), max_params_per_request):
            chunk = params_to_use[i:i + max_params_per_request]
            logger.info(f"[nasa_power] Buscando chunk {i//max_params_per_request + 1}/{(len(params_to_use)-1)//max_params_per_request + 1} ({len(chunk)} parâmetros)")

            resp = self._fetch_raw(
                latitude=coords["lat"],
                longitude=coords["lon"],
                start_date=start_date.isoformat().replace("-", ""),
                end_date=end_date.isoformat().replace("-", ""),
                parameters=chunk,
            )

            if not resp.success:
                errors.append(f"Chunk {i//max_params_per_request + 1}: {resp.error}")
                continue

            df_chunk = self._transform_raw_to_df(resp, station_name, coords, janela="historico", only_fetched_cols=True)
            if df_chunk.success and df_chunk.data is not None and not df_chunk.data.empty:
                all_data.append(df_chunk.data)

            # Pausa entre chunks
            import time
            time.sleep(1.0)

        if not all_data:
            return APIResponse(
                success=False,
                error=f"Todos os chunks falharam: {errors}",
            )

        # Merge todos os chunks pelo timestamp
        combined = all_data[0]
        for df in all_data[1:]:
            combined = combined.merge(df, on=["estacao", "latitude", "longitude", "data", "janela"], how="outer")

        combined = validate_or_warn(combined, NasaPowerRecordSchema, f"nasa_power_all_{station_name}")

        return APIResponse(
            success=True,
            data=combined,
            error="; ".join(errors) if errors else None,
        )

    def _transform_raw_to_df(
        self,
        resp: APIResponse,
        station_name: str,
        coords: dict[str, float],
        janela: str = "recente",
        only_fetched_cols: bool = False,
    ) -> APIResponse:
        """Transforma resposta JSON da NASA POWER em DataFrame validado.
        
        Args:
            only_fetched_cols: Se True, retorna apenas as colunas que vieram na resposta
                              (útil para merge de chunks). Se False, completa com todas
                              colunas do schema (padrão).
        """
        try:
            data = resp.data
            properties = data.get("properties", {})
            parameters_data = properties.get("parameter", {})

            if not parameters_data:
                return APIResponse(
                    success=False,
                    error="Resposta sem parâmetros válidos",
                    correlation_id=resp.correlation_id,
                )

            # Extrai datas do primeiro parâmetro disponível
            first_param = next(iter(parameters_data.values()))
            if not isinstance(first_param, dict):
                return APIResponse(
                    success=False,
                    error="Formato de dados inesperado",
                    correlation_id=resp.correlation_id,
                )

            dates = list(first_param.keys())
            records = []

            for date_str in dates:
                record = {
                    "estacao": station_name,
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "data": pd.to_datetime(date_str, format="%Y%m%d"),
                    "janela": janela,
                }

                # Mapeia cada parâmetro
                for nasa_param, values in parameters_data.items():
                    schema_name = NASA_POWER_PARAMS.get(nasa_param)
                    if schema_name and date_str in values:
                        val = values[date_str]
                        # NASA POWER usa -999 para dados faltando
                        if val == -999 or val == -999.0:
                            val = None
                        record[schema_name] = val

                # Calcula índice de saturação baseado em umidade solo
                gwet = record.get("umidade_solo_superficial") or record.get("umidade_solo_radicular") or 0
                if gwet is not None:
                    record["indice_saturacao"] = gwet
                    if gwet >= 0.85:
                        record["classe_saturacao"] = "CRITICO"
                    elif gwet >= 0.7:
                        record["classe_saturacao"] = "ATENCAO"
                    elif gwet >= 0.3:
                        record["classe_saturacao"] = "NORMAL"
                    else:
                        record["classe_saturacao"] = "SEM DADOS"
                else:
                    record["indice_saturacao"] = None
                    record["classe_saturacao"] = "SEM DADOS"

                records.append(record)

            df = pd.DataFrame(records)

            # Garante todas as colunas do schema apenas se não estiver no modo "only_fetched_cols"
            if not only_fetched_cols:
                schema_columns = list(NasaPowerRecordSchema.to_schema().columns.keys())
                for col in schema_columns:
                    if col not in df.columns:
                        df[col] = None
                df = df[schema_columns]

            # Valida com schema
            df_validated = validate_or_warn(df, NasaPowerRecordSchema, f"nasa_power_{station_name}")

            logger.info(
                f"[nasa_power] {station_name} | {janela} | {len(df)} registros "
                f"({df.get('precipitacao_mm', pd.Series([0])).sum():.1f} mm total) [{resp.correlation_id}]"
            )

            return APIResponse(
                success=True,
                data=df_validated,
                status_code=resp.status_code,
                response_time_ms=resp.response_time_ms,
                correlation_id=resp.correlation_id,
            )

        except Exception as e:
            logger.exception(f"[nasa_power] Erro transformando dados: {e}")
            return APIResponse(
                success=False,
                error=f"Transformação falhou: {e}",
                correlation_id=resp.correlation_id,
            )

    def fetch_multiple_stations(
        self,
        station_names: list[str] | None = None,
        days_back: int = 30,
        parameters: list[str] | None = None,
    ) -> APIResponse:
        """Busca dados de múltiplas estações sequencialmente."""
        if station_names is None:
            station_names = list(PE_STATIONS.keys())[:5]

        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=days_back)

        all_data = []
        errors = []

        for i, station in enumerate(station_names):
            logger.info(f"[nasa_power] Buscando estação {i+1}/{len(station_names)}: {station}")
            resp = self.fetch_agrometeorologia(
                station_name=station,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                parameters=parameters,
            )

            if resp.success and resp.data is not None:
                all_data.append(resp.data)
            else:
                errors.append(f"{station}: {resp.error}")

            if i < len(station_names) - 1:
                import time
                time.sleep(1.0)  # Pausa extra entre estações

        if not all_data:
            return APIResponse(
                success=False,
                error=f"Todas as estações falharam: {errors}",
            )

        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = validate_or_warn(combined_df, NasaPowerRecordSchema, "nasa_power_multi")

        return APIResponse(
            success=True,
            data=combined_df,
            error="; ".join(errors) if errors else None,
        )


# ════════════════════════════════════════════════════════════════════════════════
# FUNÇÕES CACHED PARA STREAMLIT
# ════════════════════════════════════════════════════════════════════════════════

@streamlit_cache_data(ttl_seconds=86400, show_spinner="Carregando dados agrometeorológicos NASA POWER (últimos 30 dias)...")
def fetch_nasa_power_pe_cached(
    station_name: str = "RECIFE",
    days_back: int = 30,
) -> APIResponse:
    """Função cached para Streamlit - dados agrometeorológicos recentes (parâmetros padrão)."""
    client = NASA_POWER_Client()
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    return client.fetch_agrometeorologia(
        station_name=station_name,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )


@streamlit_cache_data(ttl_seconds=604800, show_spinner="Carregando histórico NASA POWER (últimos 5 anos)...")
def fetch_nasa_power_historico_cached(
    station_name: str = "RECIFE",
    years_back: int = 5,
) -> APIResponse:
    """Função cached para Streamlit - histórico completo (cache 7 dias)."""
    client = NASA_POWER_Client()
    return client.fetch_historico_completo(station_name=station_name, years_back=years_back)


@streamlit_cache_data(ttl_seconds=172800, show_spinner="Carregando múltiplas estações NASA POWER...")
def fetch_nasa_power_multi_cached(
    station_names: list[str] | None = None,
    days_back: int = 30,
) -> APIResponse:
    """Função cached para Streamlit - múltiplas estações."""
    client = NASA_POWER_Client()
    return client.fetch_multiple_stations(station_names=station_names, days_back=days_back)