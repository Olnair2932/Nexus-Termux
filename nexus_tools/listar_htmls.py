#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
PASTA_HTML = BASE / "html_gerados"
PASTA_VERSOES = PASTA_HTML / "versoes"

print("=== NEXUS LISTADOR DE HTML ===")
print()

if not PASTA_HTML.exists():
    print("ERRO: pasta html_gerados não encontrada.")
    raise SystemExit(1)

arquivos = sorted(
    PASTA_HTML.glob("*.html"),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

versoes = []
if PASTA_VERSOES.exists():
    versoes = sorted(
        PASTA_VERSOES.glob("*.html"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

print("=== HTMLs PUBLICADOS ===")
print()

if not arquivos:
    print("Nenhum HTML publicado encontrado.")
else:
    for i, arquivo_html in enumerate(arquivos, 1):
        data = datetime.fromtimestamp(
            arquivo_html.stat().st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")

        print(f"{i}. {arquivo_html.name}")
        print(f"   Data: {data}")
        print(f"   Caminho: {arquivo_html}")
        print()

print("=== VERSÕES ===")
print()

if not versoes:
    print("Nenhuma versão encontrada.")
else:
    for i, arquivo_html in enumerate(versoes, 1):
        data = datetime.fromtimestamp(
            arquivo_html.stat().st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")

        print(f"{i}. {arquivo_html.name}")
        print(f"   Data: {data}")
        print(f"   Caminho: {arquivo_html}")
        print()

print("=== FIM DA LISTAGEM ===")
