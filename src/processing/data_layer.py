"""ASI Data Layer — DuckDB + Polars + GeoParquet para queries espaciais sub-ms.

Singleton thread-safe com @st.cache_resource. Zero I/O no hot path.
"""

from __future__ import annotations

import duckdb
import polars as pl
from pathlib import Path
from typing import Optional
import streamlit as st


class ASIDataLayer:
    """Camada de dados geoespacial em memória (DuckDB + Spatial)."""

    _instance: Optional["ASIDataLayer"] = None
    _initialized: bool = False

    def __new__(cls) -> "ASIDataLayer":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.conn = duckdb.connect(":memory:")
        self._setup_extensions()
        self._load_all_data()
        self._initialized = True

    def _setup_extensions(self) -> None:
        """Carrega extensão spatial e configura limites de memória."""
        self.conn.install_extension("spatial")
        self.conn.load_extension("spatial")
        # Limite seguro para Streamlit Cloud (1GB)
        self.conn.execute("PRAGMA memory_limit='1GB'")
        self.conn.execute("PRAGMA threads=4")

    @st.cache_resource(show_spinner="Carregando base geoespacial ASI...")
    def _load_all_data(_self) -> None:
        """Carrega todas as tabelas GeoParquet uma única vez no startup."""
        base = Path("data/curated")

        tables = {
            "twi_points": base / "twi_points.parquet",
            "bairros": base / "bairros.parquet",
            "hidro": base / "hidro.parquet",
            "eventos": base / "eventos.parquet",
            "defesa_civil": base / "defesa_civil.parquet",
        }

        for table, path in tables.items():
            if path.exists():
                _self.conn.execute(
                    f"CREATE TABLE {table} AS SELECT * FROM read_parquet('{path}')"
                )
            else:
                # Tabela vazia com schema compatível para evitar erros
                _self.conn.execute(
                    f"CREATE TABLE {table} AS SELECT * FROM (VALUES (1)) WHERE false"
                )

        # Índices espaciais RTREE para queries de buffer/interseção
        for table in ("twi_points", "eventos"):
            _self.conn.execute(
                f"CREATE INDEX idx_{table}_geom ON {table} USING RTREE(geometry)"
            )

    # ════════════════════════════════════════════════════════════════════════════
    # QUERIES OTIMIZADAS (sub-ms a poucos ms)
    # ══════════════════════════════════════════════════════════════════════════════

    def get_twi_points(
        self,
        twi_min: float = 0.0,
        bairro: Optional[str] = None,
        bbox: Optional[tuple[float, float, float, float]] = None,
    ) -> pl.DataFrame:
        """Retorna pontos TWI filtrados por threshold, bairro e/ou bounding box."""
        sql = "SELECT * FROM twi_points WHERE twi >= ?"
        params: list = [twi_min]

        if bairro and bairro != "Todos":
            sql += " AND NM_BAIRRO = ?"
            params.append(bairro)

        if bbox:
            minx, miny, maxx, maxy = bbox
            sql += " AND ST_Intersects(geometry, ST_MakeEnvelope(?, ?, ?, ?))"
            params.extend([minx, miny, maxx, maxy])

        return pl.from_arrow(self.conn.execute(sql, params).arrow())

    def get_buffer_analysis(
        self, lat: float, lon: float, radius_m: float = 500
    ) -> dict:
        """Análise de buffer 500m — 100% no DuckDB (C++ nativo).

        Nota: coordenadas de entrada são WGS84 (lat/lon), dados são UTM 25S.
        Conversão necessária via ST_Transform.
        """
        point_wkt = f"POINT({lon} {lat})"

        sql = f"""
            WITH center AS (
                SELECT ST_Transform(ST_GeomFromText('{point_wkt}'), 'EPSG:4326', 'EPSG:31985') AS geom
            ),
            nearby AS (
                SELECT
                    twi,
                    ST_Distance(geometry, (SELECT geom FROM center)) AS dist_m
                FROM twi_points
                WHERE ST_DWithin(geometry, (SELECT geom FROM center), ?)
            )
            SELECT
                COUNT(*) AS total_pontos,
                COUNT(*) FILTER (WHERE twi >= 16) AS criticos_altos,
                COUNT(*) FILTER (WHERE twi < 16) AS seguros,
                AVG(twi) AS twi_medio,
                MAX(twi) AS twi_max
            FROM nearby
        """
        result = self.conn.execute(sql, [radius_m]).fetchone()
        return {
            "total_pontos": result[0] or 0,
            "criticos_altos": result[1] or 0,
            "seguros": result[2] or 0,
            "twi_medio": float(result[3]) if result[3] is not None else 0.0,
            "twi_max": float(result[4]) if result[4] is not None else 0.0,
        }

    def get_events_nearby(
        self, lat: float, lon: float, radius_m: float = 500
    ) -> pl.DataFrame:
        """Eventos históricos dentro do raio (ordenados por distância).

        Coordenadas de entrada WGS84, dados eventos já em WGS84.
        """
        point_wkt = f"POINT({lon} {lat})"

        sql = f"""
            SELECT
                data, bairro, descricao, severidade, fonte,
                ST_Distance(geometry, ST_GeomFromText('{point_wkt}')) AS dist_m
            FROM eventos
            WHERE ST_DWithin(geometry, ST_GeomFromText('{point_wkt}'), ?)
            ORDER BY dist_m
        """
        return pl.from_arrow(self.conn.execute(sql, [radius_m]).arrow())

    def get_ranking_bairros(self) -> pl.DataFrame:
        """Ranking IRA por bairro — computado 1x, cached.

        Nota: usa threshold TWI >= 16 para CRITICO/ALTO já que não temos coluna Classe_Risco_Cod.
        """
        sql = """
            SELECT
                NM_BAIRRO,
                COUNT(*) AS total_pontos,
                AVG(twi) AS twi_medio,
                MAX(twi) AS twi_max,
                COUNT(*) FILTER (WHERE twi >= 16) AS criticos,
                COUNT(*) FILTER (WHERE twi >= 12 AND twi < 16) AS altos,
                COUNT(*) FILTER (WHERE twi >= 16) * 100.0 / COUNT(*) AS pct_critico_alto,
                MODE(twi) AS classe_dominante,
                AVG(CASE
                    WHEN twi >= 16 THEN 5
                    WHEN twi >= 12 THEN 4
                    WHEN twi >= 8 THEN 3
                    WHEN twi >= 4 THEN 2
                    ELSE 1 END) AS ira
            FROM twi_points
            WHERE NM_BAIRRO IS NOT NULL
            GROUP BY NM_BAIRRO
            ORDER BY ira DESC
        """
        return pl.from_arrow(self.conn.execute(sql).arrow())

    def get_unique_bairros(self) -> list[str]:
        """Lista de bairros únicos para selectbox."""
        sql = "SELECT DISTINCT NM_BAIRRO FROM twi_points WHERE NM_BAIRRO IS NOT NULL ORDER BY NM_BAIRRO"
        return [row[0] for row in self.conn.execute(sql).fetchall()]


@st.cache_resource
def get_data_layer() -> ASIDataLayer:
    """Factory cached — singleton real no Streamlit."""
    return ASIDataLayer()