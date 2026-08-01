"""Conversão CSV/TXT/GeoJSON → GeoParquet (ZSTD compression).

Roda uma vez no setup. Gera arquivos em data/curated/ para o DuckDB.
"""

from __future__ import annotations

import polars as pl
import geopandas as gpd
from pathlib import Path


def convert_all() -> None:
    """Converte todos os datasets brutos para GeoParquet."""
    raw = Path("data/raw")
    curated = Path("data/curated")
    curated.mkdir(parents=True, exist_ok=True)

    print("=== Conversão ASI: Raw → GeoParquet ===\n")

    # 1. TWI Points (mdt_points_tables.txt → twi_points.parquet)
    print("1/5 Convertendo TWI Points...")
    twi_path = raw / "arcmap_exports" / "mdt_points_tables.txt"
    if twi_path.exists():
        df = pl.read_csv(twi_path, separator=";", decimal_comma=True)
        # Coordenadas estão em Coord_X, Coord_Y (projetadas UTM zone 25S)
        gdf = gpd.GeoDataFrame(
            df.to_pandas(),
            geometry=gpd.points_from_xy(df["Coord_X"], df["Coord_Y"]),
            crs="EPSG:31985",  # SIRGAS 2000 / UTM zone 25S (Brasil)
        )
        gdf.to_parquet(curated / "twi_points.parquet", compression="zstd")
        print(f"   ✓ {len(gdf):,} pontos → data/curated/twi_points.parquet")
    else:
        print(f"   ⚠ Arquivo não encontrado: {twi_path}")

    # 2. Bairros (GeoJSON → Parquet)
    print("2/5 Convertendo Bairros...")
    bairros_path = raw / "arcmap_exports" / "pe_municipios_2024.json"
    if bairros_path.exists():
        bairros = gpd.read_file(bairros_path)
        bairros.to_parquet(curated / "bairros.parquet", compression="zstd")
        print(f"   ✓ {len(bairros):,} feições → data/curated/bairros.parquet")
    else:
        print(f"   ⚠ Arquivo não encontrado: {bairros_path}")

    # 3. Hidrografia
    print("3/5 Convertendo Hidrografia...")
    hidro_path = raw / "qgis_exports" / "Hidrografia_Pernambuco.geojson"
    if hidro_path.exists():
        hidro = gpd.read_file(hidro_path)
        hidro.to_parquet(curated / "hidro.parquet", compression="zstd")
        print(f"   ✓ {len(hidro):,} feições → data/curated/hidro.parquet")
    else:
        print(f"   ⚠ Arquivo não encontrado: {hidro_path}")

    # 4. Eventos históricos
    print("4/5 Convertendo Eventos Históricos...")
    eventos_path = raw / "events" / "historico_inundacoes.csv"
    if eventos_path.exists():
        # CSV tem latitude/longitude em string com vírgula decimal (português)
        df = pl.read_csv(eventos_path, separator=";", truncate_ragged_lines=True)
        # Converte vírgula para ponto e cast para float
        df = df.with_columns([
            pl.col("latitude").str.replace(",", ".").cast(pl.Float64).alias("lat"),
            pl.col("longitude").str.replace(",", ".").cast(pl.Float64).alias("lon"),
        ])
        gdf_ev = gpd.GeoDataFrame(
            df.to_pandas(),
            geometry=gpd.points_from_xy(df["lon"], df["lat"]),
            crs="EPSG:4326",
        )
        gdf_ev.to_parquet(curated / "eventos.parquet", compression="zstd")
        print(f"   ✓ {len(gdf_ev):,} eventos → data/curated/eventos.parquet")
    else:
        print(f"   ⚠ Arquivo não encontrado: {eventos_path}")

    # 5. Defesa Civil
    print("5/5 Convertendo Defesa Civil...")
    dc_path = raw / "events" / "defesacivil_pe_consolidado.csv"
    if dc_path.exists():
        dc = pl.read_csv(dc_path, separator=";", truncate_ragged_lines=True)
        dc.write_parquet(curated / "defesa_civil.parquet", compression="zstd")
        print(f"   ✓ {len(dc):,} registros → data/curated/defesa_civil.parquet")
    else:
        print(f"   ⚠ Arquivo não encontrado: {dc_path}")

    print("\n=== Conversão concluída ===")


if __name__ == "__main__":
    convert_all()