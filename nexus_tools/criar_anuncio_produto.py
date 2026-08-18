#!/usr/bin/env python3

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime


BASE = Path(__file__).resolve().parent.parent

HTML_DIR = BASE / "html_gerados"
VERSOES_DIR = HTML_DIR / "versoes"

FIREBASE_PATH = "nexus/html_gerados"

DATABASE_URL = (
    "https://finance-master-629d1-default-rtdb.firebaseio.com"
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

def obter_env(nome):
    valor = os.getenv(nome)

    if not valor:
        raise RuntimeError(
            f"Variável {nome} não encontrada no ambiente."
        )

    return valor


# ============================================================
# GEMINI
# ============================================================

def gerar_html_gemini(produto):
    """
    Gera a página de anúncio usando Gemini.

    GEMINI_API_KEY existe somente no Render.
    """

    import urllib.request
    import urllib.error

    api_key = obter_env("GEMINI_API_KEY")

    prompt = f"""
Crie uma página HTML completa, moderna e responsiva
para anúncio e venda de um produto.

Produto:
{produto.get("nome", "")}

Preço:
{produto.get("preco", "")}

Descrição:
{produto.get("descricao", "")}

Benefícios:
{produto.get("beneficios", "")}

WhatsApp:
{produto.get("whatsapp", "")}

Imagens:
{json.dumps(produto.get("imagens", []), ensure_ascii=False)}

Requisitos:

1. HTML completo.
2. CSS dentro do próprio HTML.
3. Responsivo para celular.
4. Visual profissional de página de vendas.
5. Mostrar nome, preço e descrição.
6. Mostrar as imagens recebidas.
7. Criar botão de compra pelo WhatsApp.
8. Usar as URLs reais das imagens.
9. Não usar imagens externas fictícias.
10. Não inventar informações do produto.
11. Não colocar chaves de API no HTML.
12. Retornar somente HTML.
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.1-flash-lite:generateContent"
        "?key="
        + api_key
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
        ]
    }

    requisicao = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
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

            dados = json.loads(
                resposta.read().decode("utf-8")
            )

    except urllib.error.HTTPError as erro:

        corpo = erro.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            "Erro Gemini: "
            + corpo
        )

    candidatos = dados.get("candidates", [])

    if not candidatos:
        raise RuntimeError(
            "Gemini não retornou conteúdo."
        )

    partes = candidatos[0].get(
        "content",
        {}
    ).get(
        "parts",
        []
    )

    texto = "".join(
        parte.get("text", "")
        for parte in partes
    ).strip()

    texto = re.sub(
        r"^```html\s*",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r"\s*```$",
        "",
        texto
    )

    if "<html" not in texto.lower():
        raise RuntimeError(
            "Gemini não retornou um HTML válido."
        )

    return texto


# ============================================================
# CLOUDINARY
# ============================================================

def upload_imagem_cloudinary(caminho):
    """
    Envia uma imagem para Cloudinary.

    CLOUDINARY_URL existe somente no Render.
    """

    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError:
        raise RuntimeError(
            "Dependência cloudinary não instalada no Render."
        )

    cloudinary_url = obter_env(
        "CLOUDINARY_URL"
    )

    caminho = Path(caminho)

    if not caminho.exists():
        raise RuntimeError(
            f"Imagem não encontrada: {caminho}"
        )

    cloudinary.config(
        cloudinary_url=cloudinary_url
    )

    resultado = cloudinary.uploader.upload(
        str(caminho),
        folder="nexus/anuncios"
    )

    return {
        "url": resultado.get(
            "secure_url"
        ),
        "public_id": resultado.get(
            "public_id"
        ),
        "format": resultado.get(
            "format"
        ),
        "width": resultado.get(
            "width"
        ),
        "height": resultado.get(
            "height"
        )
    }


# ============================================================
# FIREBASE
# ============================================================

def conectar_firebase():

    try:
        import firebase_admin
        from firebase_admin import (
            credentials,
            db
        )
    except ImportError:
        raise RuntimeError(
            "Dependência firebase_admin não instalada no Render."
        )

    if firebase_admin._apps:
        return db

    cred_json = obter_env(
        "private_key"
    )

    try:
        cred_data = json.loads(
            cred_json
        )
    except json.JSONDecodeError as erro:
        raise RuntimeError(
            "private_key não contém JSON válido."
        ) from erro

    if cred_data.get("private_key"):
        cred_data["private_key"] = (
            cred_data["private_key"]
            .replace("\\\\n", "\\n")
        )

    firebase_admin.initialize_app(
        credentials.Certificate(
            cred_data
        ),
        {
            "databaseURL":
                DATABASE_URL
        }
    )

    return db


# ============================================================
# SALVAR E SINCRONIZAR
# ============================================================

def salvar_html(produto, html, imagens):

    HTML_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    VERSOES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    agora = datetime.now()

    nome = (
        "nexus_anuncio_"
        + agora.strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".html"
    )

    arquivo = HTML_DIR / nome

    arquivo_versao = (
        VERSOES_DIR / nome
    )

    arquivo.write_text(
        html,
        encoding="utf-8"
    )

    arquivo_versao.write_text(
        html,
        encoding="utf-8"
    )

    db = conectar_firebase()

    dados = {
        "nome": nome,
        "tipo": "anuncio_produto",
        "titulo_produto": produto.get(
            "nome",
            ""
        ),
        "preco": produto.get(
            "preco",
            ""
        ),
        "descricao": produto.get(
            "descricao",
            ""
        ),
        "html": html,
        "imagens": imagens,
        "criado_em": agora.isoformat(),
        "sincronizado_em": datetime.now().isoformat()
    }

    db.reference(
        FIREBASE_PATH
    ).child(
        Path(nome).stem
    ).set(dados)

    return arquivo


# ============================================================
# EXECUTOR PRINCIPAL
# ============================================================

def criar_anuncio(produto):

    print(
        "=== NEXUS CRIADOR DE ANÚNCIO ==="
    )

    print()

    print(
        "Produto:",
        produto.get("nome", "")
    )

    print()

    imagens = []

    for caminho in produto.get(
        "imagens",
        []
    ):

        print(
            "☁️ Enviando imagem:",
            caminho
        )

        imagem = upload_imagem_cloudinary(
            caminho
        )

        imagens.append(
            imagem
        )

        print(
            "✅ Imagem enviada:"
        )

        print(
            imagem.get("url")
        )

    produto["imagens"] = imagens

    print()

    print(
        "🤖 Gerando página com Gemini..."
    )

    html = gerar_html_gemini(
        produto
    )

    print(
        "✅ HTML gerado."
    )

    print()

    arquivo = salvar_html(
        produto,
        html,
        imagens
    )

    print(
        "=== ANÚNCIO CRIADO ==="
    )

    print()

    print(
        "HTML:",
        arquivo
    )

    print(
        "Firebase:",
        FIREBASE_PATH
    )

    print(
        "Cloudinary:",
        len(imagens),
        "imagem(ns)"
    )

    print()

    print(
        "URL:",
        "https://nexus-termux.onrender.com/html_gerados/"
        + arquivo.name
    )

    print()

    return arquivo


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Uso:"
        )

        print(
            "python3 criar_anuncio_produto.py "
            "'{\"nome\":\"Produto\", ...}'"
        )

        raise SystemExit(1)

    try:

        produto = json.loads(
            sys.argv[1]
        )

        criar_anuncio(
            produto
        )

    except Exception as erro:

        print(
            "❌ ERRO:",
            erro
        )

        raise SystemExit(1)
