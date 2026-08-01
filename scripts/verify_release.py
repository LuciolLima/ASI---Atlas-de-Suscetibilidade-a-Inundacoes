# scripts/verify_release.py — Verificação de assets do release GitHub

"""Verifica se os assets do release GitHub estão corretos.
Uso: python scripts/verify_release.py (requer GITHUB_TOKEN no ambiente)
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com"
REPO = "LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes"


def get_release_assets(tag: str, token: str) -> list:
    """Busca assets de uma release pela tag."""
    headers = {"Authorization": f"token {token}"}
    url = f"{GITHUB_API}/repos/{REPO}/releases/tags/{tag}"

    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print(f"Release {tag} nao encontrada")
        return []
    resp.raise_for_status()

    return resp.json().get("assets", [])


def download_asset(asset: dict, token: str) -> bytes:
    """Baixa um asset do GitHub."""
    headers = {"Authorization": f"token {token}", "Accept": "application/octet-stream"}
    resp = requests.get(asset["browser_download_url"], headers=headers)
    resp.raise_for_status()
    return resp.content


def sha256_bytes(data: bytes) -> str:
    """Calcula SHA256 de bytes."""
    return hashlib.sha256(data).hexdigest()


def main():
    # Tag da release (padrão: última tag)
    tag = os.environ.get("RELEASE_TAG")
    if not tag:
        # Tenta pegar a última tag local
        import subprocess
        try:
            tag = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=Path(__file__).parent.parent,
                text=True
            ).strip()
        except:
            print("Erro: RELEASE_TAG nao definida e nao foi possivel obter tag local")
            return 1

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: GITHUB_TOKEN nao definido no ambiente")
        return 1

    print(f"Verificando release: {tag}")

    assets = get_release_assets(tag, token)
    if not assets:
        print("Nenhum asset encontrado na release")
        return 1

    print(f"Assets encontrados: {len(assets)}")
    for asset in assets:
        print(f"  - {asset['name']} ({asset['size']} bytes)")

    # Verifica se data_V3.0-System.zip existe
    zip_asset = next((a for a in assets if a["name"] == "data_V3.0-System.zip"), None)
    if not zip_asset:
        print("ERRO: data_V3.0-System.zip nao encontrado na release")
        return 1

    # Baixa e verifica checksum
    print("\nBaixando e verificando data_V3.0-System.zip...")
    zip_data = download_asset(zip_asset, token)
    actual_hash = sha256_bytes(zip_data)

    # Carrega checksums.json local (se existir)
    checksums_path = Path("data/checksums.json")
    expected_hash = None
    if checksums_path.exists():
        expected = json.loads(checksums_path.read_text(encoding='utf-8'))
        expected_hash = expected.get("data_V3.0-System.zip")

    if expected_hash:
        if actual_hash == expected_hash:
            print(f"[OK] Checksum confere: {actual_hash[:16]}...")
        else:
            print("[FAIL] Checksum NAO confere!")
            print(f"  Esperado: {expected_hash[:16]}...")
            print(f"  Atual:    {actual_hash[:16]}...")
            return 1
    else:
        print(f"[INFO] Checksum calculado: {actual_hash[:16]}... (sem referencia local)")

    print("\nTodas verificacoes passaram!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
