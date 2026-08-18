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
# CLOUDINARY
# ============================================================

def configurar_cloudinary():

    try:
        import cloudinary
    except ImportError:
        raise RuntimeError(
            "Dependência cloudinary não instalada no Render."
        )

    cloudinary_url = obter_env("CLOUDINARY_URL")

    cloudinary.config(
        cloudinary_url=cloudinary_url
    )

    return cloudinary


def upload_imagem_cloudinary(caminho):

    import cloudinary.uploader

    arquivo = Path(caminho)

    if not arquivo.exists():
        raise RuntimeError(
            f"Imagem não encontrada: {arquivo}"
        )

    if not arquivo.is_file():
        raise RuntimeError(
            f"O caminho informado não é um arquivo: {arquivo}"
        )

    resultado = cloudinary.uploader.upload(
        str(arquivo),
        folder="nexus/anuncios"
    )

    url = resultado.get("secure_url")

    if not url:
        raise RuntimeError(
            "Cloudinary não retornou secure_url para a imagem."
        )

    return {
        "url": url,
        "public_id": resultado.get("public_id"),
        "format": resultado.get("format"),
        "width": resultado.get("width"),
        "height": resultado.get("height")
    }


def upload_video_cloudinary(caminho):

    import cloudinary.uploader

    arquivo = Path(caminho)

    if not arquivo.exists():
        raise RuntimeError(
            f"Vídeo não encontrado: {arquivo}"
        )

    if not arquivo.is_file():
        raise RuntimeError(
            f"O caminho informado não é um arquivo: {arquivo}"
        )

    resultado = cloudinary.uploader.upload(
        str(arquivo),
        resource_type="video",
        folder="nexus/anuncios/videos"
    )

    url = resultado.get("secure_url")

    if not url:
        raise RuntimeError(
            "Cloudinary não retornou secure_url para o vídeo."
        )

    return {
        "url": url,
        "public_id": resultado.get("public_id"),
        "format": resultado.get("format"),
        "resource_type": resultado.get("resource_type"),
        "duration": resultado.get("duration"),
        "width": resultado.get("width"),
        "height": resultado.get("height"),
        "bytes": resultado.get("bytes")
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

    cred_json = obter_env("private_key")

    try:
        cred_data = json.loads(cred_json)
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
        credentials.Certificate(cred_data),
        {
            "databaseURL": DATABASE_URL
        }
    )

    return db


# ============================================================
# GEMINI
# ============================================================

def gerar_html_gemini(produto, imagens, video):

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

IMAGENS REAIS DO PRODUTO:
{json.dumps(imagens, ensure_ascii=False)}

VÍDEO REAL DO PRODUTO:
{json.dumps(video, ensure_ascii=False)}

Requisitos obrigatórios:

1. Retornar um HTML completo.
2. CSS dentro do próprio HTML.
3. Layout profissional de página de vendas.
4. Design moderno e responsivo para celular.
5. Mostrar nome do produto.
6. Mostrar preço.
7. Mostrar descrição.
8. Mostrar benefícios quando fornecidos.
9. Mostrar todas as imagens reais recebidas.
10. Usar exatamente as URLs reais das imagens.
11. Criar uma seção de galeria de imagens.
12. Criar uma seção de vídeo do produto.
13. Usar exatamente a URL real do vídeo.
14. O vídeo deve funcionar usando HTML5 <video>.
15. O vídeo deve possuir controles.
16. Criar botão de compra pelo WhatsApp.
17. Usar o número de WhatsApp fornecido pelo usuário.
18. Não inventar URLs de imagens.
19. Não inventar URL de vídeo.
20. Não usar imagens externas fictícias.
21. Não inventar informações do produto.
22. Não colocar chaves de API no HTML.
23. Não colocar código Python no HTML.
24. Não explicar o código.
25. Retornar somente HTML.

As imagens e o vídeo fornecidos são arquivos reais
enviados para Cloudinary.

A página deve utilizar somente as URLs reais
fornecidas nos dados acima.
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
            "Erro Gemini: " + corpo
        )

    candidatos = dados.get(
        "candidates",
        []
    )

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

    if video.get("url") and video["url"] not in texto:
        raise RuntimeError(
            "O HTML gerado não contém a URL real do vídeo."
        )

    for imagem in imagens:

        url_imagem = imagem.get("url")

        if url_imagem and url_imagem not in texto:
            raise RuntimeError(
                "O HTML gerado não contém uma das URLs reais "
                "das imagens."
            )

    return texto


# ============================================================
# SALVAR E SINCRONIZAR
# ============================================================

def salvar_html(
    produto,
    html,
    imagens,
    video
):

    HTML_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    VERSOES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    agora = datetime.now()

    nome_html = produto.get(
        "_nome_html",
        ""
    ).strip()

    if nome_html:

        if not nome_html.lower().endswith(".html"):
            nome_html += ".html"

        nome = Path(
            nome_html
        ).name

    else:

        nome = (
            "nexus_anuncio_multimidia_"
            + agora.strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".html"
        )

    arquivo = HTML_DIR / nome

    arquivo_versao = VERSOES_DIR / nome

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
        "tipo": "anuncio_produto_multimidia",
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
        "video": video,
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

def criar_anuncio_multimidia(produto):

    print(
        "=== NEXUS CRIADOR DE ANÚNCIO MULTIMÍDIA ==="
    )

    print()

    print(
        "Produto:",
        produto.get("nome", "")
    )

    # --------------------------------------------------------
    # CLOUDINARY
    # --------------------------------------------------------

    configurar_cloudinary()

    imagens = []

    caminhos_imagens = produto.get(
        "imagens",
        []
    )

    if not isinstance(
        caminhos_imagens,
        list
    ):
        raise RuntimeError(
            "O campo 'imagens' deve ser uma lista."
        )

    for caminho in caminhos_imagens:

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
            "✅ Imagem enviada:",
            imagem.get("url")
        )

    caminho_video = produto.get(
        "video"
    )

    if not caminho_video:
        raise RuntimeError(
            "Nenhum vídeo foi informado."
        )

    print()

    print(
        "☁️ Enviando vídeo:",
        caminho_video
    )

    video = upload_video_cloudinary(
        caminho_video
    )

    print(
        "✅ Vídeo enviado:",
        video.get("url")
    )

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    print()

    print(
        "🤖 Gerando página multimídia com Gemini..."
    )

    html = gerar_html_gemini(
        produto,
        imagens,
        video
    )

    print(
        "✅ HTML gerado."
    )

    # --------------------------------------------------------
    # FIREBASE + HTML
    # --------------------------------------------------------

    arquivo = salvar_html(
        produto,
        html,
        imagens,
        video
    )

    print()

    print(
        "=== ANÚNCIO MULTIMÍDIA CRIADO ==="
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
        "imagem(ns) + 1 vídeo"
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

    if len(sys.argv) < 3:

        print("Uso:")

        print(
            "python3 criar_anuncio_multimidia.py "
            "<nome_html> '<json_produto>'"
        )

        raise SystemExit(1)

    nome_html = sys.argv[1].strip()

    dados_json = " ".join(
        sys.argv[2:]
    ).strip()

    if not nome_html:

        print(
            "❌ Nome do HTML não informado."
        )

        raise SystemExit(1)

    if not dados_json:

        print(
            "❌ Dados do produto não informados."
        )

        raise SystemExit(1)

    try:

        produto = json.loads(
            dados_json
        )

        if not isinstance(
            produto,
            dict
        ):
            raise ValueError(
                "Os dados do produto devem ser um objeto JSON."
            )

        produto["_nome_html"] = nome_html

        criar_anuncio_multimidia(
            produto
        )

    except json.JSONDecodeError as erro:

        print(
            "❌ JSON inválido:",
            erro
        )

        raise SystemExit(1)

    except Exception as erro:

        print(
            "❌ ERRO:",
            erro
        )

        raise SystemExit(1)
