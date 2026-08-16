#!/usr/bin/env python3

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

print("=== NEXUS LEITOR DE HTML ===")
print()

if len(sys.argv) < 2:
    print("Uso:")
    print("python3 abrir_html.py <nome_html>")
    raise SystemExit(1)

nome_html = " ".join(sys.argv[1:]).strip()

if not nome_html.endswith(".html"):
    nome_html += ".html"

BASE = Path(__file__).resolve().parent.parent
PASTA_HTML = BASE / "html_gerados"

arquivo_local = PASTA_HTML / nome_html

print("HTML solicitado:")
print(nome_html)
print()

# ==========================================
# 1. TENTAR LOCALMENTE
# ==========================================

if arquivo_local.exists():

    print("✅ HTML encontrado localmente.")
    print()
    print("Caminho:")
    print(arquivo_local.resolve())
    print()

    try:
        html = arquivo_local.read_text(
            encoding="utf-8"
        )
    except Exception as erro:
        print("ERRO ao ler HTML:")
        print(erro)
        raise SystemExit(1)

else:

    # ==========================================
    # 2. BUSCAR NO NEXUS
    # ==========================================

    print("⚠️ HTML não encontrado localmente.")
    print("🌐 Buscando HTML no Nexus...")
    print()

    base_url = os.environ.get(
        "NEXUS_PUBLIC_URL",
        "https://nexus-termux.onrender.com"
    ).rstrip("/")

    url = (
        base_url
        + "/html_gerados/"
        + nome_html
    )

    print("URL:")
    print(url)
    print()

    try:

        requisicao = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Nexus-SRE"
            }
        )

        with urllib.request.urlopen(
            requisicao,
            timeout=30
        ) as resposta:

            html = resposta.read().decode(
                "utf-8"
            )

        print("✅ HTML recuperado.")
        print()

    except urllib.error.HTTPError as erro:

        print(
            f"ERRO HTTP ao buscar HTML: {erro.code}"
        )

        raise SystemExit(1)

    except Exception as erro:

        print("ERRO ao buscar HTML:")
        print(erro)

        raise SystemExit(1)

# ==========================================
# VALIDAR
# ==========================================

if not html.strip():

    print("ERRO: HTML vazio.")
    raise SystemExit(1)

if (
    "<html" not in html.lower()
    and "<!doctype" not in html.lower()
):

    print(
        "⚠️ Aviso: conteúdo não parece ser um HTML completo."
    )

# ==========================================
# RESULTADO
# ==========================================

print("=== HTML ===")
print()
print(html)
print()

print("=== FIM DO HTML ===")
