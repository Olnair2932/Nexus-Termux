#!/usr/bin/env python3

import os
import sys
import json
import shutil
import urllib.request
import urllib.error
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

PASTA_TEMP.mkdir(parents=True, exist_ok=True)
PASTA_VERSOES.mkdir(parents=True, exist_ok=True)

arquivo_original = PASTA_HTML / nome_html

if not arquivo_original.exists():
    print("ERRO: HTML não encontrado:")
    print(arquivo_original)
    raise SystemExit(1)

html_original = arquivo_original.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

arquivo_temp = PASTA_TEMP / f"{Path(nome_html).stem}_{timestamp}.html"

arquivo_temp.write_text(
    html_original,
    encoding="utf-8"
)

print("HTML original:")
print(arquivo_original)

print()
print("Cópia temporária criada:")
print(arquivo_temp)

print()
print("Alteração solicitada:")
print(alteracao)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO: variável GEMINI_API_KEY não encontrada.")
    raise SystemExit(1)

prompt = f"""
Você é o EDITOR DE HTML do Nexus SRE.

O usuário quer modificar um HTML existente.

ALTERAÇÃO SOLICITADA:
{alteracao}

REGRAS OBRIGATÓRIAS:

1. Preserve todas as funcionalidades existentes.
2. Faça somente as alterações solicitadas.
3. Não recrie a página do zero.
4. Não remova JavaScript existente sem necessidade.
5. Não remova CSS existente sem necessidade.
6. Não remova integração existente com /api/chat.
7. Não altere comandos existentes.
8. Preserve responsividade para celular.
9. Preserve o idioma pt-BR.
10. Retorne o HTML COMPLETO.
11. Responda somente com HTML.
12. Não use Markdown.
13. Não use ```html.
14. Não coloque GEMINI_API_KEY no HTML.
15. Não coloque qualquer chave de API no JavaScript do navegador.
16. Não use eval().
17. Não use bibliotecas CDN.
18. Use HTML5.
19. Preserve as funcionalidades existentes mesmo quando adicionar novas funcionalidades.

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

    print("ERRO: Gemini não retornou HTML válido.")

    print(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2
        )
    )

    raise SystemExit(1)

# Remove Markdown caso Gemini envie cercas.
if codigo_html.startswith("```"):

    linhas = codigo_html.splitlines()

    if linhas and linhas[0].strip().startswith("```"):
        linhas = linhas[1:]

    if linhas and linhas[-1].strip() == "```":
        linhas = linhas[:-1]

    codigo_html = "\n".join(linhas).strip()

if "<html" not in codigo_html.lower():

    print(
        "ERRO: resposta não parece ser um HTML completo."
    )

    raise SystemExit(1)

# ============================================================
# SALVAR NOVA VERSÃO
# ============================================================

nome_novo = (
    Path(nome_html).stem
    + "_editado_"
    + timestamp
    + ".html"
)

arquivo_novo = PASTA_VERSOES / nome_novo

arquivo_novo.write_text(
    codigo_html,
    encoding="utf-8"
)

print()
print("=== HTML EDITADO ===")
print()

print(codigo_html)

print()
print("=== HTML EDITADO SALVO ===")
print(arquivo_novo)

print()
print("=== HTML ORIGINAL PRESERVADO ===")
print(arquivo_original)

print()
print("=== TEMPORÁRIO ===")
print(arquivo_temp)

print()
print("=== FIM DA EDIÇÃO ===")
