#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db

def conectar_firebase():
    if firebase_admin._apps:
        return

    cred_json = os.getenv("private_key")

    if not cred_json:
        raise RuntimeError(
            "Variável private_key não encontrada."
        )

    try:
        cred_data = json.loads(cred_json)
    except json.JSONDecodeError as erro:
        raise RuntimeError(
            "A variável private_key não contém um JSON válido."
        ) from erro

    campos_obrigatorios = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "token_uri"
    ]

    faltando = [
        campo
        for campo in campos_obrigatorios
        if not cred_data.get(campo)
    ]

    if faltando:
        raise RuntimeError(
            "Campos ausentes na credencial Firebase: "
            + ", ".join(faltando)
        )

    cred_data["private_key"] = (
        cred_data["private_key"]
        .replace("\\\\n", "\\n")
    )

    firebase_admin.initialize_app(
        credentials.Certificate(cred_data),
        {
            "databaseURL":
                "https://finance-master-629d1-default-rtdb.firebaseio.com"
        }
    )


def sincronizar_html_firebase(arquivo_html):
    conectar_firebase()

    html = arquivo_html.read_text(encoding="utf-8")

    dados = {
        "nome": arquivo_html.name,
        "html": html,
        "criado_em": datetime.fromtimestamp(
            arquivo_html.stat().st_mtime
        ).isoformat(),
        "sincronizado_em": datetime.now().isoformat()
    }

    db.reference(
        "nexus/html_gerados"
    ).child(
        arquivo_html.stem
    ).set(dados)

    print("=== FIREBASE ===")
    print(f"✅ HTML sincronizado: {arquivo_html.name}")
    print("Firebase: nexus/html_gerados")
    print()


print("=== NEXUS GERADOR DE HTML ===")
print()

if len(sys.argv) < 2:
    print("Uso:")
    print("python3 criar_html.py <descrição_do_site>")
    raise SystemExit(1)

descricao = " ".join(sys.argv[1:]).strip()

if not descricao:
    print("ERRO: descrição não informada.")
    raise SystemExit(1)

BASE = Path(__file__).resolve().parent.parent
PASTA_HTML = BASE / "html_gerados"
PASTA_TEMP = PASTA_HTML / "temporarios"
PASTA_VERSOES = PASTA_HTML / "versoes"

PASTA_HTML.mkdir(parents=True, exist_ok=True)
PASTA_TEMP.mkdir(parents=True, exist_ok=True)
PASTA_VERSOES.mkdir(parents=True, exist_ok=True)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO: variável GEMINI_API_KEY não encontrada.")
    raise SystemExit(1)

print("Descrição solicitada:")
print(descricao)
print()

prompt = f"""
Você é o GERADOR DE HTML do Nexus SRE.

Crie um site HTML completo baseado na solicitação abaixo.

SOLICITAÇÃO:
{descricao}

REGRAS OBRIGATÓRIAS:

- Retorne somente o HTML completo.
- Não use Markdown.
- Não use ```html.
- Use HTML5.
- Idioma pt-BR.
- Interface responsiva para celular e desktop.
- CSS dentro de <style>.
- JavaScript dentro de <script>.
- Não use dependências externas.
- Não use bibliotecas CDN.
- Nunca coloque GEMINI_API_KEY no HTML.
- Nunca coloque qualquer chave de API no JavaScript do navegador.
- Não use eval().
- Use textContent quando for suficiente para inserir dados externos.
- Não invente integrações com APIs que não foram solicitadas.
- Se houver necessidade de backend, prepare a interface sem colocar segredos no navegador.
- Gere código funcional e completo.
- Não explique o código.
- Preserve segurança básica do navegador.

Retorne somente o HTML.
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

print("Enviando solicitação para Nexus/Gemini...")
print()

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
    print("ERRO ao chamar Gemini:")
    print(erro)
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

# Remover cercas Markdown caso Gemini eventualmente envie.
if codigo_html.startswith("```"):
    linhas = codigo_html.splitlines()

    if linhas and linhas[0].strip().startswith("```"):
        linhas = linhas[1:]

    if linhas and linhas[-1].strip() == "```":
        linhas = linhas[:-1]

    codigo_html = "\n".join(linhas).strip()

if (
    "<html" not in codigo_html.lower()
    and "<!doctype" not in codigo_html.lower()
):
    print("ERRO: resposta não parece ser HTML completo.")
    raise SystemExit(1)

agora = datetime.now()

nome_base = (
    "nexus_"
    + agora.strftime("%Y%m%d_%H%M%S")
    + ".html"
)

arquivo_temp = (
    PASTA_TEMP /
    (
        "criacao_"
        + agora.strftime("%Y%m%d_%H%M%S")
        + ".html"
    )
)

arquivo_versao = PASTA_VERSOES / nome_base
arquivo_publicado = PASTA_HTML / nome_base

arquivo_temp.write_text(
    codigo_html,
    encoding="utf-8"
)

arquivo_versao.write_text(
    codigo_html,
    encoding="utf-8"
)

arquivo_publicado.write_text(
    codigo_html,
    encoding="utf-8"
)

try:
    sincronizar_html_firebase(arquivo_publicado)
except Exception as erro:
    print("⚠️ HTML salvo localmente, mas não foi sincronizado com Firebase.")
    print(f"Erro Firebase: {erro}")
    print()

print("=== HTML GERADO ===")
print()
print(codigo_html)
print()

print("=== CÓPIA TEMPORÁRIA ===")
print(arquivo_temp)
print()

print("=== VERSÃO SALVA ===")
print(arquivo_versao)
print()

print("=== HTML PUBLICADO ===")
print(arquivo_publicado)
print()

print("=== FIM DA CRIAÇÃO ===")
