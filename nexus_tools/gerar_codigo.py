#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import urllib.error

print("=== NEXUS GERADOR DE CÓDIGO ===")

if len(sys.argv) < 2:
    print("Erro: nenhuma solicitação recebida.")
    raise SystemExit(1)

solicitacao = " ".join(sys.argv[1:]).strip()

print(f"Solicitação: {solicitacao}")
print()
print("Gerando código com Nexus/Gemini...")
print()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO: variável GEMINI_API_KEY não encontrada.")
    raise SystemExit(1)

prompt = f"""
Você é o gerador de código do Nexus.

O usuário solicitou:

{solicitacao}

Gere uma página HTML completa, pronta para copiar e colar em um arquivo
.html e abrir diretamente no navegador.

Regras:
- Responda somente com o código HTML.
- Não use Markdown.
- Não coloque o código entre ```html e ```.
- Use HTML5.
- Pode incluir CSS dentro de <style>.
- Pode incluir JavaScript dentro de <script> quando necessário.
- A página deve funcionar sem dependências externas.
- O resultado deve ser visualmente organizado e funcional.
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
        "temperature": 0.4,
        "maxOutputTokens": 8192
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
    with urllib.request.urlopen(requisicao, timeout=90) as resposta:
        resultado = json.loads(
            resposta.read().decode("utf-8")
        )

except urllib.error.HTTPError as erro:
    corpo = erro.read().decode(
        "utf-8",
        errors="replace"
    )
    print(f"ERRO HTTP Gemini: {erro.code}")
    print(corpo)
    raise SystemExit(1)

except Exception as erro:
    print(f"ERRO ao chamar Gemini: {erro}")
    raise SystemExit(1)

try:
    codigo_html = (
        resultado["candidates"][0]
        ["content"]["parts"][0]["text"]
        .strip()
    )

except (KeyError, IndexError, TypeError):
    print("ERRO: Gemini não retornou código válido.")
    print(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2
        )
    )
    raise SystemExit(1)

# Remove cercas Markdown caso o modelo eventualmente as envie.
if codigo_html.startswith("```"):
    linhas = codigo_html.splitlines()

    if linhas and linhas[0].strip().startswith("```"):
        linhas = linhas[1:]

    if linhas and linhas[-1].strip() == "```":
        linhas = linhas[:-1]

    codigo_html = "\n".join(linhas).strip()

print("=== CÓDIGO GERADO ===")
print()
print(codigo_html)
print()
print("=== FIM DO CÓDIGO ===")
