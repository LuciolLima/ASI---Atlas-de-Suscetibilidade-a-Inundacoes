"""SISTEMA ASI — CLIENTE CPRM WFS
Versão: 1.0 — Cliente para CPRM/SGB via WFS (Web Feature Service)
Provedor: CPRM - Serviço Geológico do Brasil
Endpoint: https://geoservicos.cprm.gov.br/geoserver/wfs
Camadas: Geologia 1:250k/1:M, Pedologia, Geomorfologia, Áreas risco MAE
"""

from __future__ import annotations

import logging
from typing import Any
import sys

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import shape

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ════════════════════════════════════════════════════════════════════════════════

CPRM_WFS_BASE_URL = "https://geoservicos.cprm.gov.br/geoserver/wfs"

# Camadas prioritárias para ASI (nomes podem variar - verificar GetCapabilities)
CPRM_LAYERS = {
    "geologia_250k": "cprm:geologia_250k",           # Geologia 1:250.000
    "geologia_1M": "cprm:geologia_1M",               # Geologia 1:1.000.000
    "pedologia": "cprm:pedologia",                   # Pedologia (classes de solo, drenagem, textura)
    "geomorfologia": "cprm:geomorfologia",           # Geomorfologia (compartimentos, feições)
    "areas_risco": "cprm:areas_risco_mae",           # Áreas de risco oficial (setorização MAE/CPRM)
}

# Parâmetros WFS padrão
WFS_PARAMS = {
    "service": "WFS",
    "version": "2.0.0",
    "request": "GetFeature",
    "outputFormat": "application/json",  # GeoJSON
    "srsName": "EPSG:4326",
}

# Bounding box aproximado de Pernambuco (minx, miny, maxx, maxy) em EPSG:4326
PE_BBOX = (-41.5, -10.0, -34.5, -7.0)

# ════════════════════════════════════════════════════════════════════════════════
# CLIENTE CPRM WFS
# ════════════════════════════════════════════════════════════════════════════════

class CPRM_WFS_Client:
    """Cliente para CPRM WFS (Web Feature Service)."""

    def __init__(self, base_url: str = CPRM_WFS_BASE_URL, timeout: int = 60):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ASI-Atlas/3.1 (+https://github.com/LuciolLima/ASI)"
        })

    def get_capabilities(self) -> dict[str, Any] | None:
        """Obtém GetCapabilities do WFS."""
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetCapabilities",
        }
        try:
            resp = self.session.get(self.base_url, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                return {"status": "ok", "content_type": resp.headers.get("Content-Type")}
            logger.warning(f"CPRM WFS GetCapabilities falhou: HTTP {resp.status_code}")
            return None
        except Exception as e:
            logger.exception("Erro GetCapabilities")
            return None

    def describe_feature_type(self, type_name: str) -> dict[str, Any] | None:
        """Obtém DescribeFeatureType para uma camada."""
        params = {
            **WFS_PARAMS,
            "typeName": type_name,
            "request": "DescribeFeatureType",
        }
        try:
            resp = self.session.get(self.base_url, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                return {"status": "ok", "content": resp.text}
            logger.warning(f"CPRM WFS DescribeFeatureType falhou: HTTP {resp.status_code}")
            return None
        except Exception as e:
            logger.exception(f"Erro DescribeFeatureType {type_name}")
            return None

    def get_features(
        self,
        layer_key: str,
        bbox: tuple[float, float, float, float] | None = None,
        cql_filter: str | None = None,
        max_features: int | None = None,
    ) -> gpd.GeoDataFrame | None:
        """Busca features de uma camada WFS.

        Args:
            layer_key: Chave da camada (ex: 'geologia_250k')
            bbox: Bounding box (minx, miny, maxx, maxy) em EPSG:4326
            cql_filter: Filtro CQL (ex: "ESTADO = 'PE'")
            max_features: Limite máximo de features

        Returns:
            GeoDataFrame ou None se erro
        """
        if layer_key not in CPRM_LAYERS:
            logger.error(f"Camada desconhecida: {layer_key}. Disponíveis: {list(CPRM_LAYERS.keys())}")
            return None

        type_name = CPRM_LAYERS[layer_key]
        params = {
            **WFS_PARAMS,
            "typeName": type_name,
        }

        if bbox:
            minx, miny, maxx, maxy = bbox
            params["bbox"] = f"{minx},{miny},{maxx},{maxy},EPSG:4326"

        if cql_filter:
            params["cql_filter"] = cql_filter

        if max_features:
            params["maxFeatures"] = str(max_features)

        try:
            logger.info(f"CPRM WFS GetFeature: {type_name}")
            resp = self.session.get(self.base_url, params=params, timeout=self.timeout)

            if resp.status_code != 200:
                logger.warning(f"CPRM WFS {type_name}: HTTP {resp.status_code} - {resp.text[:200]}")
                return None

            # Parse GeoJSON
            geojson = resp.json()
            if "features" not in geojson or not geojson["features"]:
                logger.info(f"CPRM WFS {type_name}: Nenhuma feature retornada")
                return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

            gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")
            logger.info(f"CPRM WFS {type_name}: {len(gdf)} features obtidas")
            return gdf

        except requests.exceptions.Timeout:
            logger.warning(f"CPRM WFS {type_name}: Timeout")
            return None
        except Exception as e:
            logger.exception(f"Erro GetFeature {type_name}")
            return None

    def get_geologia_pe(self) -> gpd.GeoDataFrame | None:
        """Busca geologia 1:250k para PE."""
        return self.get_features("geologia_250k", bbox=PE_BBOX)

    def get_pedologia_pe(self) -> gpd.GeoDataFrame | None:
        """Busca pedologia para PE."""
        return self.get_features("pedologia", bbox=PE_BBOX)

    def get_geomorfologia_pe(self) -> gpd.GeoDataFrame | None:
        """Busca geomorfologia para PE."""
        return self.get_features("geomorfologia", bbox=PE_BBOX)

    def get_areas_risco_pe(self) -> gpd.GeoDataFrame | None:
        """Busca áreas de risco oficial para PE."""
        return self.get_features("areas_risco", bbox=PE_BBOX)


# ════════════════════════════════════════════════════════════════════════════════
# SCRIPT DE ENRIQUECIMENTO TWI
# ════════════════════════════════════════════════════════════════════════════════

def enriquecer_twi_com_geologia(
    twi_gdf: gpd.GeoDataFrame,
    client: CPRM_WFS_Client | None = None,
) -> gpd.GeoDataFrame:
    """Enriquece grade TWI com variáveis geológicas da CPRM.

    Args:
        twi_gdf: GeoDataFrame com grade TWI (pontos com geometria Point)
        client: Cliente CPRM WFS (opcional, cria novo se None)

    Returns:
        GeoDataFrame enriquecido com colunas geológicas
    """
    if client is None:
        client = CPRM_WFS_Client()

    # Garante CRS correto
    if twi_gdf.crs is None:
        twi_gdf = twi_gdf.set_crs("EPSG:4326")
    elif twi_gdf.crs != "EPSG:4326":
        twi_gdf = twi_gdf.to_crs("EPSG:4326")

    resultado = twi_gdf.copy()

    # 1. Geologia
    logger.info("Buscando geologia CPRM...")
    geologia = client.get_geologia_pe()
    if geologia is not None and not geologia.empty:
        # Spatial join: cada ponto TWI pega atributos da feição geológica que o contém
        cols_geol = [c for c in geologia.columns if c not in ["geometry"]]
        if cols_geol:
            join_geol = gpd.sjoin(resultado, geologia[cols_geol + ["geometry"]],
                                   how="left", predicate="within")
            # Renomeia colunas para evitar conflito
            join_geol = join_geol.rename(columns={c: f"geol_{c}" for c in cols_geol})
            join_geol = join_geol.drop(columns=["index_right"], errors="ignore")
            resultado = join_geol

    # 2. Pedologia
    logger.info("Buscando pedologia CPRM...")
    pedologia = client.get_pedologia_pe()
    if pedologia is not None and not pedologia.empty:
        cols_ped = [c for c in pedologia.columns if c not in ["geometry"]]
        if cols_ped:
            join_ped = gpd.sjoin(resultado, pedologia[cols_ped + ["geometry"]],
                                  how="left", predicate="within")
            join_ped = join_ped.rename(columns={c: f"ped_{c}" for c in cols_ped})
            join_ped = join_ped.drop(columns=["index_right"], errors="ignore")
            resultado = join_ped

    # 3. Geomorfologia
    logger.info("Buscando geomorfologia CPRM...")
    geomorf = client.get_geomorfologia_pe()
    if geomorf is not None and not geomorf.empty:
        cols_geom = [c for c in geomorf.columns if c not in ["geometry"]]
        if cols_geom:
            join_geom = gpd.sjoin(resultado, geomorf[cols_geom + ["geometry"]],
                                   how="left", predicate="within")
            join_geom = join_geom.rename(columns={c: f"geom_{c}" for c in cols_geom})
            join_geom = join_geom.drop(columns=["index_right"], errors="ignore")
            resultado = join_geom

    # 4. Áreas de risco
    logger.info("Buscando áreas de risco CPRM...")
    risco = client.get_areas_risco_pe()
    if risco is not None and not risco.empty:
        cols_risco = [c for c in risco.columns if c not in ["geometry"]]
        if cols_risco:
            join_risco = gpd.sjoin(resultado, risco[cols_risco + ["geometry"]],
                                    how="left", predicate="within")
            join_risco = join_risco.rename(columns={c: f"risco_{c}" for c in cols_risco})
            join_risco = join_risco.drop(columns=["index_right"], errors="ignore")
            # Flag binária: está em área de risco?
            risco_cols = [c for c in join_risco.columns if c.startswith("risco_")]
            if risco_cols:
                join_risco["em_area_risco_cprm"] = join_risco[risco_cols].notna().any(axis=1)
            resultado = join_risco

    logger.info("Enriquecimento TWI concluído")
    return resultado


# ════════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL PARA SCRIPT
# ════════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """Script principal: enriquece grade TWI e salva parquet."""
    import sys
    from pathlib import Path

    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Caminhos
    twi_path = Path("data/twi_enriched.parquet")
    output_path = Path("data/twi_enriched.parquet")

    if not twi_path.exists():
        logger.error(f"Arquivo TWI não encontrado: {twi_path}")
        return 1

    logger.info(f"Carregando TWI de {twi_path}...")
    twi_gdf = gpd.read_parquet(twi_path)

    logger.info(f"TWI carregado: {len(twi_gdf)} pontos")
    logger.info(f"Colunas: {list(twi_gdf.columns)}")

    # Enriquece
    client = CPRM_WFS_Client()
    twi_enriched = enriquecer_twi_com_geologia(twi_gdf, client)

    # Salva
    output_path.parent.mkdir(parents=True, exist_ok=True)
    twi_enriched.to_parquet(output_path, index=False)
    logger.info(f"TWI enriquecido salvo em {output_path}")
    logger.info(f"Novas colunas: {[c for c in twi_enriched.columns if c not in twi_gdf.columns]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())