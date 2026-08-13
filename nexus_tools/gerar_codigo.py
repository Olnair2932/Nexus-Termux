#!/usr/bin/env python3

import os
from pathlib import Path
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
.html e abrir no navegador.

REGRAS GERAIS:
- Responda somente com o código HTML.
- Não use Markdown.
- Não coloque o código entre ```html e ```.
- Use HTML5.
- CSS deve ficar dentro de <style>.
- JavaScript deve ficar dentro de <script>.
- Não use frameworks, bibliotecas, CDN ou dependências externas.
- O resultado deve ser visualmente organizado, profissional, responsivo
  e funcional.
- Nunca invente APIs que não foram solicitadas.

INTEGRAÇÃO REAL COM O NEXUS:
Se a solicitação for para criar um painel, interface, dashboard ou site
do Nexus SRE, a interface deve possuir comunicação REAL com o backend
Nexus através de:

POST /api/chat

O JavaScript deve enviar comandos usando exatamente este formato:

fetch("/api/chat", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        texto: comando,
        voz: false
    })
})

A resposta deve ser processada como JSON.

Use a propriedade "nexus" da resposta para exibir a resposta da IA
na interface.

Não simule respostas da IA.
Não escreva mensagens falsas como "Execução concluída com sucesso".
O campo de comandos deve realmente enviar o comando ao backend.

Para o painel Nexus SRE, quando solicitado, inclua:
- cabeçalho NEXUS SRE;
- indicador ONLINE;
- terminal futurista;
- campo para comandos;
- botão EXECUTAR;
- envio também pelo Enter;
- área de resposta da IA;
- histórico de comandos;
- cards de status;
- botões de ações rápidas;
- layout responsivo para celular;
- tratamento visual de carregamento;
- tratamento de erros de comunicação;
- rolagem automática do terminal;
- botão para limpar o histórico.

IMPORTANTE:
O HTML será servido pelo mesmo domínio do backend Nexus.
Portanto utilize "/api/chat" como endpoint relativo.
Não coloque chave de API Gemini no HTML.
Nunca exponha GEMINI_API_KEY no código do navegador.

O objetivo é gerar uma interface real para o Nexus, e não apenas uma
demonstração visual.
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

# ============================================================
# SALVAR HTML GERADO LOCALMENTE
# ============================================================

from datetime import datetime

PASTA_HTML = Path(__file__).resolve().parent.parent / "html_gerados"
PASTA_HTML.mkdir(parents=True, exist_ok=True)

nome_html = (
    "nexus_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".html"
)

arquivo_html = PASTA_HTML / nome_html

arquivo_html.write_text(
    codigo_html,
    encoding="utf-8"
)

print()
print("=== HTML SALVO ===")
print(str(arquivo_html))
print("=== FIM DO HTML SALVO ===")

print("=== FIM DO CÓDIGO ===")
