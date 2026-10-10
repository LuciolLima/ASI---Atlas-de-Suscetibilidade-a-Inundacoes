# scripts/validate_data.py — Validação completa do pipeline de dados

"""Script para validar integridade e schema dos dados do ASI.
Uso: python scripts/validate_data.py
"""

import json
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from src.validation.schemas import (
    DefesaCivilSchema,
    EventosInundacaoSchema,
    GeoSpatialSchema,
    PrecipitacaoSchema,
)


def validate_file(path: Path, schema, name: str) -> bool:
    """Valida um arquivo CSV contra seu schema Pandera."""
    if not path.exists():
        print(f"  [SKIP] {name}: arquivo nao encontrado em {path}")
        return True  # Não é erro se arquivo opcional não existe

    try:
        df = pd.read_csv(path, sep=';', decimal=',', encoding='utf-8')
        df.columns = df.columns.str.strip()
        schema.validate(df, lazy=True)
        print(f"  [OK]   {name}: {len(df)} linhas, {len(df.columns)} colunas")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def main():
    print("=" * 60)
    print("VALIDACAO DE DADOS ASI")
    print("=" * 60)

    base = Path("data")
    all_ok = True

    # Dataset principal (obrigatório)
    print("\n[1/5] Dataset Principal (data_table.txt)")
    all_ok &= validate_file(
        base / "curated" / "attribute_tables" / "data_table.txt",
        GeoSpatialSchema(),
        "data_table.txt"
    )

    # Precipitação (opcional mas recomendado)
    print("\n[2/5] Precipitacao Historica (APAC)")
    all_ok &= validate_file(
        base / "raw" / "apac_exports" / "precipitacao_pernambuco.csv",
        PrecipitacaoSchema(),
        "precipitacao_pernambuco.csv"
    )

    # Eventos históricos (opcional)
    print("\n[3/5] Eventos Historicos de Inundacao")
    all_ok &= validate_file(
        base / "raw" / "events" / "historico_inundacoes.csv",
        EventosInundacaoSchema(),
        "historico_inundacoes.csv"
    )

    # Defesa Civil (opcional mas recomendado)
    print("\n[4/5] Defesa Civil PE Consolidado")
    all_ok &= validate_file(
        base / "raw" / "events" / "defesacivil_pe_consolidado.csv",
        DefesaCivilSchema(),
        "defesacivil_pe_consolidado.csv"
    )

    # Checksums
    print("\n[5/5] Verificacao de Checksums")
    checksums_path = base / "checksums.json"
    if checksums_path.exists():
        try:
            import hashlib
            expected = json.loads(checksums_path.read_text(encoding='utf-8'))
            for fname, expected_hash in expected.items():
                fpath = Path(fname)
                if fpath.exists():
                    h = hashlib.sha256()
                    with open(fpath, "rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            h.update(chunk)
                    actual = h.hexdigest()
                    if actual == expected_hash:
                        print(f"  [OK]   {fname}")
                    else:
                        print(f"  [FAIL] {fname}: checksum mismatch")
                        all_ok = False
                else:
                    print(f"  [WARN] {fname}: arquivo nao encontrado (pode ser opcional)")
        except Exception as e:
            print(f"  [FAIL] Erro ao verificar checksums: {e}")
            all_ok = False
    else:
        print("  [WARN] checksums.json nao encontrado")

    print("\n" + "=" * 60)
    if all_ok:
        print("TODAS VALIDACOES PASSARAM ✓")
        return 0
    print("ALGUMAS VALIDACOES FALHARAM ✗")
    return 1


if __name__ == "__main__":
    sys.exit(main())
