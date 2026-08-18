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

def upload_video_cloudinary(caminho):
    """
    Envia o vídeo para Cloudinary.

    CLOUDINARY_URL existe somente no Render.
    Nenhuma dependência é importada no Termux.
    """

    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError:
        raise RuntimeError(
            "Dependência cloudinary não instalada no Render."
        )

    caminho = Path(caminho)

    if not caminho.exists():
        raise RuntimeError(
            f"Vídeo não encontrado: {caminho}"
        )

    if not caminho.is_file():
        raise RuntimeError(
            f"O caminho informado não é um arquivo: {caminho}"
        )

    cloudinary_url = obter_env(
        "CLOUDINARY_URL"
    )

    cloudinary.config(
        cloudinary_url=cloudinary_url
    )

    print()
    print("☁️ Enviando vídeo para Cloudinary...")
    print("Arquivo:", caminho.name)

    resultado = cloudinary.uploader.upload(
        str(caminho),
        resource_type="video",
        folder="nexus/anuncios/videos"
    )

    url = resultado.get("secure_url")

    if not url:
        raise RuntimeError(
            "Cloudinary não retornou secure_url."
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
# GEMINI
# ============================================================

def gerar_html_gemini(produto, video):

    """
    Gera a página de anúncio usando Gemini.

    GEMINI_API_KEY existe somente no Render.
    """

    import urllib.request
    import urllib.error

    api_key = obter_env(
        "GEMINI_API_KEY"
    )

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

Vídeo real do produto:
{json.dumps(video, ensure_ascii=False)}

Requisitos obrigatórios:

1. HTML completo.
2. CSS dentro do próprio HTML.
3. Layout profissional de página de vendas.
4. Responsivo para celular.
5. Mostrar nome do produto.
6. Mostrar preço.
7. Mostrar descrição.
8. Mostrar benefícios somente quando fornecidos.
9. Criar botão de compra pelo WhatsApp somente se
   houver número/contato informado.
10. Usar o vídeo real fornecido.
11. O vídeo deve ser exibido com a tag HTML5 <video>.
12. Usar a URL real do Cloudinary.
13. Não usar vídeo fictício.
14. Não usar imagens ou vídeos externos inventados.
15. Não inventar informações do produto.
16. Não colocar chaves de API no HTML.
17. O vídeo deve possuir controles.
18. O vídeo deve ser responsivo.
19. Usar poster somente se uma URL real for fornecida.
20. Retornar somente HTML.

URL real do vídeo:
{video.get("url", "")}
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

    if video.get("url") not in texto:
        raise RuntimeError(
            "O HTML gerado não contém a URL real do vídeo."
        )

    return texto


# ============================================================
# SALVAR E SINCRONIZAR
# ============================================================

def salvar_html(produto, html, video):

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
        "nexus_anuncio_video_"
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
        "tipo": "anuncio_produto_video",
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

def criar_anuncio_video(produto):

    print(
        "=== NEXUS CRIADOR DE ANÚNCIO COM VÍDEO ==="
    )

    print()

    print(
        "Produto:",
        produto.get("nome", "")
    )

    caminho_video = produto.get(
        "video"
    )

    if not caminho_video:
        raise RuntimeError(
            "Nenhum vídeo foi informado."
        )

    # --------------------------------------------------------
    # 1. CLOUDINARY
    # --------------------------------------------------------

    video = upload_video_cloudinary(
        caminho_video
    )

    print()
    print("✅ Vídeo enviado para Cloudinary.")
    print("URL:", video.get("url"))

    # --------------------------------------------------------
    # 2. GEMINI
    # --------------------------------------------------------

    produto["video"] = video

    print()
    print(
        "🤖 Gerando página de anúncio com Gemini..."
    )

    html = gerar_html_gemini(
        produto,
        video
    )

    print(
        "✅ HTML gerado."
    )

    # --------------------------------------------------------
    # 3. FIREBASE + HTML
    # --------------------------------------------------------

    arquivo = salvar_html(
        produto,
        html,
        video
    )

    print()
    print(
        "=== ANÚNCIO COM VÍDEO CRIADO ==="
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
        video.get("url")
    )

    print()
    print(
        "URL:",
        "https://nexus-termux.onrender.com/html_gerados/"
        + arquivo.name
    )

    print()
    print(
        "=== FIM ==="
    )

    return arquivo


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Uso:")

        print(
            "python3 criar_anuncio_video.py "
            "'{\"nome\":\"Produto\","
            "\"preco\":\"R$ 99,90\","
            "\"descricao\":\"Descrição\","
            "\"video\":\"/caminho/video.mp4\"}'"
        )

        raise SystemExit(1)

    try:

        produto = json.loads(
            sys.argv[1]
        )

        criar_anuncio_video(
            produto
        )

    except Exception as erro:

        print(
            "❌ ERRO:",
            erro
        )

        raise SystemExit(1)
