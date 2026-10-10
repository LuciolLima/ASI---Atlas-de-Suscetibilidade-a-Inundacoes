#!/usr/bin/env python3
# scripts/verify_checksums.py — Verifica checksums no startup do app

"""Modulo para verificar integridade dos arquivos de dados via SHA256.
Integrado no app.py durante carregamento.
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


def verificar_checksums() -> bool:
    """Verifica checksums dos arquivos de dados contra data/checksums.json.
    Retorna True se todos conferem (ou arquivo nao existe), False se falha.
    """
    checksums_path = Path("data/checksums.json")

    # Se nao existe arquivo de checksums, assume OK (dev local sem release)
    if not checksums_path.exists():
        return True

    try:
        expected = json.loads(checksums_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"[CHECKSUM] Erro ao ler checksums.json: {e}")
        return True  # Fail-open: se nao consegue ler, nao bloqueia

    for fname, expected_hash in expected.items():
        fpath = Path(fname)
        if fpath.exists():
            try:
                actual = sha256_file(fpath)
                if actual != expected_hash:
                    print(f"[CHECKSUM] FALHA: {fname}")
                    print(f"  Esperado: {expected_hash[:16]}...")
                    print(f"  Atual:    {actual[:16]}...")
                    return False
            except Exception as e:
                print(f"[CHECKSUM] Erro ao verificar {fname}: {e}")
                return False
        # Se arquivo nao existe, pula (pode ser opcional)

    return True


if __name__ == "__main__":
    ok = verificar_checksums()
    print("Checksums OK" if ok else "Checksums FALHARAM")
    exit(0 if ok else 1)
