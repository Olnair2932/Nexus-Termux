#!/usr/bin/env python3

import os
import sys
import json
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

PASTA_HTML = Path(__file__).resolve().parent.parent / "html_gerados"
arquivo_original = PASTA_HTML / nome_html

if not arquivo_original.exists():
    print("ERRO: HTML não encontrado:")
    print(str(arquivo_original))
    raise SystemExit(1)

html_original = arquivo_original.read_text(encoding="utf-8")

print("HTML original:")
print(str(arquivo_original))
print()
print("Alteração solicitada:")
print(alteracao)
print()
print("Enviando HTML existente para Nexus/Gemini...")
print()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO: variável GEMINI_API_KEY não encontrada.")
    raise SystemExit(1)

prompt = f"""
Você é o EDITOR DE HTML do Nexus SRE.

O usuário quer modificar um HTML que já foi criado anteriormente pelo Nexus.

ALTERAÇÃO SOLICITADA:
{alteracao}

REGRA PRINCIPAL E OBRIGATÓRIA:

"Preserve todas as funcionalidades existentes e faça somente as alterações solicitadas."

Não recrie a página do zero.
Não remova funcionalidades existentes.
Não remova JavaScript existente que não esteja relacionado à alteração.
Não remova estilos existentes sem necessidade.
Não remova integração existente com /api/chat.
Não altere comandos existentes.
Não substitua funcionalidades por simulações.
Não invente novas funcionalidades que o usuário não pediu.

O resultado deve ser o HTML COMPLETO já editado.

REGRAS:

- Responda somente com código HTML.
- Não use Markdown.
- Não use ```html.
- Use HTML5.
- Preserve o idioma pt-BR.
- Preserve responsividade.
- Preserve funcionalidades existentes.
- CSS dentro de <style>.
- JavaScript dentro de <script>.
- Não use dependências externas.
- Não use bibliotecas CDN.
- Nunca coloque GEMINI_API_KEY no HTML.
- Nunca coloque qualquer chave de API no JavaScript do navegador.
- Não use eval().
- Quando textContent for suficiente, não use innerHTML para inserir dados externos.
- Se existir integração com /api/chat, preserve-a exatamente, salvo se a alteração solicitada exigir modificá-la.

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
    with urllib.request.urlopen(requisicao, timeout=120) as resposta:
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

except (KeyError, IndexError, TypeError):
    print("ERRO: Gemini não retornou HTML válido.")
    print(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2
        )
    )
    raise SystemExit(1)

# Remove cercas Markdown caso o modelo eventualmente envie.
if codigo_html.startswith("```"):
    linhas = codigo_html.splitlines()

    if linhas and linhas[0].strip().startswith("```"):
        linhas = linhas[1:]

    if linhas and linhas[-1].strip() == "```":
        linhas = linhas[:-1]

    codigo_html = "\n".join(linhas).strip()

if "<html" not in codigo_html.lower():
    print("ERRO: resposta não parece ser um HTML completo.")
    raise SystemExit(1)

# ============================================================
# SALVAR NOVA VERSÃO
# ============================================================

PASTA_HTML.mkdir(
    parents=True,
    exist_ok=True
)

nome_novo = (
    "nexus_editado_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".html"
)

arquivo_novo = PASTA_HTML / nome_novo

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
print(str(arquivo_novo))
print("=== HTML ORIGINAL PRESERVADO ===")
print(str(arquivo_original))
print("=== FIM DA EDIÇÃO ===")
