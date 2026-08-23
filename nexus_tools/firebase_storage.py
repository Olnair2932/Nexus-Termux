#!/usr/bin/env python3

import os
import json
from datetime import datetime, timezone

try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_DISPONIVEL = True
except ImportError:
    firebase_admin = None
    credentials = None
    db = None
    FIREBASE_DISPONIVEL = False


DATABASE_URL = (
    "https://finance-master-629d1-default-rtdb.firebaseio.com"
)


def conectar_firebase():
    """Conecta ao Firebase quando disponível."""
    if not FIREBASE_DISPONIVEL:
        raise RuntimeError(
            "firebase-admin não está instalado neste ambiente."
        )

    if firebase_admin._apps:
        return

    cred_json = os.getenv("private_key")

    if not cred_json:
        raise RuntimeError(
            "Variável private_key não encontrada."
        )

    cred_data = json.loads(cred_json)

    cred_data["private_key"] = (
        cred_data["private_key"].replace("\\n", "\n")
    )

    firebase_admin.initialize_app(
        credentials.Certificate(cred_data),
        {
            "databaseURL": DATABASE_URL
        }
    )

def _normalizar_nome(nome):
    nome = str(nome).strip().replace("\\", "/")
    nome = nome.split("/")[-1]

    if not nome:
        raise ValueError("Nome de arquivo vazio.")

    return nome


def salvar_arquivo(nome, conteudo):
    """Salva um arquivo no Firebase Realtime Database."""
    conectar_firebase()

    nome = _normalizar_nome(nome)

    dados = {
        "nome": nome,
        "conteudo": str(conteudo),
        "atualizado_em": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    db.reference(
        f"arquivos_nexus/{nome}"
    ).set(dados)

    return dados


def ler_arquivo(nome):
    """Lê um arquivo persistente do Firebase."""
    conectar_firebase()

    nome = _normalizar_nome(nome)

    dados = db.reference(
        f"arquivos_nexus/{nome}"
    ).get()

    if not dados:
        return None

    return dados


def excluir_arquivo(nome):
    """Remove um arquivo persistente do Firebase."""
    conectar_firebase()

    nome = _normalizar_nome(nome)

    db.reference(
        f"arquivos_nexus/{nome}"
    ).delete()


def listar_arquivos():
    """Lista os arquivos persistentes do Nexus."""
    conectar_firebase()

    dados = db.reference(
        "arquivos_nexus"
    ).get()

    return dados or {}
