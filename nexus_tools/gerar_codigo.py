#!/usr/bin/env python3

import os
from pathlib import Path
import sys
import json
import urllib.request
import urllib.error
import time

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

prompt = """
Você é o gerador de código do Nexus.

O usuário solicitou:

__SOLICITACAO__

Gere uma página HTML completa, profissional e funcional, pronta para ser salva como arquivo .html.

REGRAS GERAIS:
- Responda somente com código HTML.
- Não use Markdown.
- Não use ```html.
- Use HTML5.
- CSS deve ficar dentro de <style>.
- JavaScript deve ficar dentro de <script>.
- Não use dependências externas.
- Não use bibliotecas CDN.
- A página deve funcionar em celular e computador.
- O visual deve ser moderno, profissional e futurista quando solicitado.

INTEGRAÇÃO REAL COM O NEXUS:

O HTML será servido pelo mesmo domínio do backend Nexus.

O endpoint obrigatório é:

/api/chat

Envie comandos usando:

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

NUNCA coloque GEMINI_API_KEY no HTML.
NUNCA coloque qualquer chave de API no JavaScript do navegador.
O navegador conversa somente com /api/chat.

RESPOSTA DO BACKEND:

O JavaScript deve aceitar tanto:

data.nexus

quanto:

data.resposta

Use uma lógica equivalente a:

const resposta = data.nexus || data.resposta || JSON.stringify(data);

Depois mostre essa resposta na área do terminal.

TRATAMENTO HTTP:

Verifique response.ok.

Se response.ok for falso, mostre uma mensagem informando o erro HTTP.

Também trate erros de conexão usando try/catch.

EXEMPLO DE COMPORTAMENTO:

try {
    const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            texto: comando,
            voz: false
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.nexus ||
            data.resposta ||
            "Erro HTTP " + response.status
        );
    }

    const resposta =
        data.nexus ||
        data.resposta ||
        JSON.stringify(data);

    // mostrar resposta no terminal

} catch (erro) {
    // mostrar erro de comunicação no terminal
}

RECURSOS OBRIGATÓRIOS DO PAINEL:

- Campo para digitar comandos.
- Botão EXECUTAR.
- Enter deve executar o comando.
- Área de resposta da IA.
- Histórico dos comandos.
- Botão LIMPAR HISTÓRICO.
- Rolagem automática para a última resposta.
- Indicador visual ONLINE.
- Indicador visual PROCESSANDO enquanto aguarda o backend.
- Botões de ação quando fizer sentido.
- Cards de status quando solicitados.
- Interface responsiva.
- Não bloquear a interface durante uma requisição.
- Desabilitar o botão de execução enquanto uma requisição estiver em andamento e reativá-lo depois.
- Não perder o histórico durante uma requisição.

SEGURANÇA:

Nunca usar innerHTML para inserir diretamente comandos ou respostas recebidas do usuário/backend quando textContent for suficiente.

Não executar código recebido da IA com eval().

Não expor variáveis de ambiente.

O objetivo é gerar uma interface REAL para o Nexus, conectada ao backend através de /api/chat, e não uma demonstração simulada.

__FIM_DAS_REGRAS__
""".replace("__SOLICITACAO__", solicitacao)



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

tentativas = 3
resultado = None

for tentativa in range(1, tentativas + 1):
    try:
        print(f"Tentativa Gemini {tentativa}/{tentativas}...")

        with urllib.request.urlopen(requisicao, timeout=90) as resposta:
            resultado = json.loads(
                resposta.read().decode("utf-8")
            )

        break

    except urllib.error.HTTPError as erro:
        corpo = erro.read().decode(
            "utf-8",
            errors="replace"
        )

        if erro.code == 503 and tentativa < tentativas:
            espera = tentativa * 5

            print(
                f"Gemini indisponível (503). "
                f"Nova tentativa em {espera}s..."
            )

            time.sleep(espera)
            continue

        print(f"ERRO HTTP Gemini: {erro.code}")
        print(corpo)
        raise SystemExit(1)

    except Exception as erro:
        print(f"ERRO ao chamar Gemini: {erro}")
        raise SystemExit(1)

if resultado is None:
    print("ERRO: Gemini não retornou resultado.")
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
