#!/usr/bin/env python3
# scripts/generate_checksum.py — Gera checksums SHA256 dos assets de dados

"""Gera arquivo data/checksums.json com SHA256 dos principais arquivos de dados.
Executar antes de criar release no GitHub.
"""

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Calcula SHA256 de um arquivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # Arquivos a verificar (relativos à raiz do projeto)
    assets = {
        "data_V3.0-System.zip": "data_V3.0-System.zip",
        "data/curated/attribute_tables/data_table.txt": "data/curated/attribute_tables/data_table.txt",
        "data/raw/apac_exports/precipitacao_pernambuco.csv": "data/raw/apac_exports/precipitacao_pernambuco.csv",
        "data/raw/events/historico_inundacoes.csv": "data/raw/events/historico_inundacoes.csv",
        "data/raw/events/defesacivil_pe_consolidado.csv": "data/raw/events/defesacivil_pe_consolidado.csv",
        "data/raw/arcmap_exports/pe_municipios_2024.json": "data/raw/arcmap_exports/pe_municipios_2024.json",
        "data/raw/arcmap_exports/bairros_cabo_oficial.json": "data/raw/arcmap_exports/bairros_cabo_oficial.json",
        "data/raw/qgis_exports/Hidrografia_Pernambuco.geojson": "data/raw/qgis_exports/Hidrografia_Pernambuco.geojson",
    }

    checksums = {}
    missing = []

    for name, rel_path in assets.items():
        path = Path(rel_path)
        if path.exists():
            checksums[name] = sha256_file(path)
            print(f"OK  {name}: {checksums[name][:16]}...")
        else:
            missing.append(name)
            print(f"MISSING {name}: {rel_path}")

    # Salva checksums
    output_path = Path("data/checksums.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(checksums, indent=2))
    print(f"\nChecksums salvos em: {output_path}")

    if missing:
        print(f"\nAviso: {len(missing)} arquivo(s) nao encontrados (podem ser opcionais)")

    return 0 if not missing else 1


if __name__ == "__main__":
    exit(main())
