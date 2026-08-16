#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from datetime import datetime

print("=== NEXUS EDITOR DE HTML ===")

if len(sys.argv) < 3:
    print("Uso:")
    print("python3 editar_html.py <nome_html> <alteração>")
    raise SystemExit(1)

nome_html = sys.argv[1].strip()
alteracao = " ".join(sys.argv[2:]).strip()

if not nome_html.endswith(".html"):
    nome_html += ".html"

BASE = Path(__file__).resolve().parent.parent
PASTA_HTML = BASE / "html_gerados"
PASTA_TEMP = PASTA_HTML / "temporarios"
PASTA_VERSOES = PASTA_HTML / "versoes"

PASTA_HTML.mkdir(parents=True, exist_ok=True)
PASTA_TEMP.mkdir(parents=True, exist_ok=True)
PASTA_VERSOES.mkdir(parents=True, exist_ok=True)

arquivo_original = PASTA_HTML / nome_html

print("HTML solicitado:")
print(nome_html)
print()

# ============================================================
# 1. PROCURAR LOCALMENTE
# ============================================================

html_original = None

if arquivo_original.exists():
    print("✅ HTML encontrado localmente:")
    print(arquivo_original)

    html_original = arquivo_original.read_text(
        encoding="utf-8"
    )

# ============================================================
# 2. SE NÃO EXISTIR LOCALMENTE, BUSCAR NO NEXUS
# ============================================================

if html_original is None:

    print("⚠️ HTML não encontrado localmente.")
    print("🌐 Buscando HTML no Nexus/Firebase...")
    print()

    base_url = os.environ.get(
        "NEXUS_PUBLIC_URL",
        "https://nexus-termux.onrender.com"
    ).rstrip("/")

    url = (
        base_url
        + "/html_gerados/"
        + urllib.parse.quote(nome_html)
    )

    print("URL:")
    print(url)
    print()

    try:
        requisicao = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Nexus-HTML-Editor/1.0"
            },
            method="GET"
        )

        with urllib.request.urlopen(
            requisicao,
            timeout=60
        ) as resposta:

            conteudo = resposta.read().decode(
                "utf-8",
                errors="replace"
            )

        # A rota pode retornar uma página de erro HTML.
        # Verificamos se parece realmente ser o documento solicitado.
        if (
            "<html" not in conteudo.lower()
            and "<!doctype" not in conteudo.lower()
        ):
            print("ERRO: resposta não parece ser HTML.")
            print(conteudo[:2000])
            raise SystemExit(1)

        html_original = conteudo

        print("✅ HTML recuperado do Nexus/Firebase.")

    except urllib.error.HTTPError as erro:

        corpo = erro.read().decode(
            "utf-8",
            errors="replace"
        )

        print("ERRO HTTP ao buscar HTML:", erro.code)
        print(corpo[:3000])
        raise SystemExit(1)

    except Exception as erro:

        print("ERRO ao buscar HTML no Nexus:")
        print(erro)
        raise SystemExit(1)

# ============================================================
# 3. CRIAR CÓPIA TEMPORÁRIA
# ============================================================

agora = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

nome_temporario = (
    Path(nome_html).stem
    + "_"
    + agora
    + ".html"
)

arquivo_temporario = (
    PASTA_TEMP / nome_temporario
)

arquivo_temporario.write_text(
    html_original,
    encoding="utf-8"
)

print()
print("Cópia temporária criada:")
print(arquivo_temporario)
print()

# ============================================================
# 4. ALTERAÇÃO
# ============================================================

print("Alteração solicitada:")
print(alteracao)
print()

# ============================================================
# 5. GEMINI
# ============================================================

print("Enviando HTML existente para Nexus/Gemini...")
print()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print(
        "ERRO: variável GEMINI_API_KEY não encontrada."
    )
    print(
        "No Render ela deve existir nas Environment Variables."
    )
    raise SystemExit(1)

prompt = f"""
Você é o EDITOR DE HTML do Nexus SRE.

O usuário quer modificar um HTML existente.

ALTERAÇÃO SOLICITADA:
{alteracao}

REGRA PRINCIPAL:

Preserve TODAS as funcionalidades existentes e faça
somente as alterações solicitadas.

Não recrie a página do zero.

Não remova:
- HTML existente
- CSS existente
- JavaScript existente
- funcionalidades existentes
- integração existente com /api/chat
- botões existentes
- formulários existentes

Não invente funcionalidades que não foram solicitadas.

O resultado deve ser o HTML COMPLETO já editado.

REGRAS:
- Responda somente com código HTML.
- Não use Markdown.
- Não use ```html.
- Use HTML5.
- Preserve pt-BR.
- Preserve responsividade.
- CSS dentro de <style>.
- JavaScript dentro de <script>.
- Não use dependências externas.
- Não use bibliotecas CDN.
- Nunca coloque GEMINI_API_KEY no HTML.
- Nunca coloque chaves de API no JavaScript do navegador.
- Não use eval().
- Preserve integrações existentes.

HTML ORIGINAL:
--- INÍCIO HTML ---

{html_original}

--- FIM HTML ---

Retorne somente o HTML completo após a alteração.
"""

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.1-flash-lite:generateContent"
    "?key=" + api_key
)

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.2,
        "maxOutputTokens": 16384
    }
}

dados = json.dumps(payload).encode("utf-8")

requisicao = urllib.request.Request(
    url,
    data=dados,
    headers={
        "Content-Type": "application/json"
    },
    method="POST"
)

try:

    with urllib.request.urlopen(
        requisicao,
        timeout=120
    ) as resposta:

        resultado = json.loads(
            resposta.read().decode("utf-8")
        )

except urllib.error.HTTPError as erro:

    corpo = erro.read().decode(
        "utf-8",
        errors="replace"
    )

    print("ERRO HTTP Gemini:", erro.code)
    print(corpo)
    raise SystemExit(1)

except Exception as erro:

    print("ERRO ao chamar Gemini:", erro)
    raise SystemExit(1)

# ============================================================
# 6. EXTRAIR HTML
# ============================================================

try:

    codigo_html = (
        resultado["candidates"][0]
        ["content"]["parts"][0]["text"]
        .strip()
    )

except (
    KeyError,
    IndexError,
    TypeError
):

    print(
        "ERRO: Gemini não retornou HTML válido."
    )

    print(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2
        )
    )

    raise SystemExit(1)

# Remover cercas Markdown caso apareçam.

if codigo_html.startswith("```"):

    linhas = codigo_html.splitlines()

    if (
        linhas
        and linhas[0].strip().startswith("```")
    ):
        linhas = linhas[1:]

    if (
        linhas
        and linhas[-1].strip() == "```"
    ):
        linhas = linhas[:-1]

    codigo_html = "\n".join(
        linhas
    ).strip()

if (
    "<html" not in codigo_html.lower()
    and "<!doctype" not in codigo_html.lower()
):

    print(
        "ERRO: resposta do Gemini não parece "
        "ser um HTML completo."
    )

    raise SystemExit(1)

# ============================================================
# 7. SALVAR NOVA VERSÃO
# ============================================================

nome_novo = (
    "nexus_editado_"
    + datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    + ".html"
)

arquivo_novo = (
    PASTA_VERSOES / nome_novo
)

arquivo_novo.write_text(
    codigo_html,
    encoding="utf-8"
)

# Também salva uma cópia na pasta principal
# para o servidor poder servir o arquivo.

arquivo_publicado = (
    PASTA_HTML / nome_novo
)

arquivo_publicado.write_text(
    codigo_html,
    encoding="utf-8"
)

print()
print("=== HTML EDITADO ===")
print()
print(codigo_html)
print()

print("=== NOVA VERSÃO SALVA ===")
print(arquivo_novo)

print()
print("=== CÓPIA PUBLICADA ===")
print(arquivo_publicado)

print()
print("=== HTML ORIGINAL PRESERVADO ===")
print(nome_html)

print()
print("=== FIM DA EDIÇÃO ===")
