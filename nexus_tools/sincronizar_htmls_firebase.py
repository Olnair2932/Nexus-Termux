#!/usr/bin/env python3

import os
import json
from pathlib import Path
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db


BASE = Path(__file__).resolve().parent.parent
HTML_DIR = BASE / "html_gerados"

FIREBASE_PATH = "nexus/html_gerados"


def conectar_firebase():
    if not firebase_admin._apps:
        private_key = os.getenv("private_key")

        if not private_key:
            raise RuntimeError("Variável private_key não encontrada.")

        cred_data = {
            "type": "service_account",
            "project_id": os.getenv("project_id"),
            "private_key_id": os.getenv("private_key_id"),
            "private_key": private_key.replace("\\n", "\n"),
            "client_email": os.getenv("client_email"),
            "client_id": os.getenv("client_id"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":
                "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("client_x509_cert_url")
        }

        firebase_admin.initialize_app(
            credentials.Certificate(cred_data),
            {
                "databaseURL":
                    "https://finance-master-629d1-default-rtdb.firebaseio.com"
            }
        )


def sincronizar():
    conectar_firebase()

    HTML_DIR.mkdir(parents=True, exist_ok=True)

    ref = db.reference(FIREBASE_PATH)

    arquivos = list(HTML_DIR.glob("*.html"))

    print("=== NEXUS SINCRONIZADOR DE HTML ===")
    print(f"Pasta: {HTML_DIR}")
    print(f"Firebase: {FIREBASE_PATH}")
    print()

    enviados = 0

    for arquivo in arquivos:
        try:
            html = arquivo.read_text(encoding="utf-8")

            dados = {
                "nome": arquivo.name,
                "html": html,
                "criado_em": datetime.fromtimestamp(
                    arquivo.stat().st_mtime
                ).isoformat(),
                "sincronizado_em": datetime.now().isoformat()
            }

            ref.child(arquivo.stem).set(dados)

            print(f"✅ Sincronizado: {arquivo.name}")
            enviados += 1

        except Exception as e:
            print(f"❌ Erro em {arquivo.name}: {e}")

    print()
    print(f"HTMLs sincronizados: {enviados}")
    print("=== FIM DA SINCRONIZAÇÃO ===")


if __name__ == "__main__":
    try:
        sincronizar()
    except Exception as e:
        print(f"❌ ERRO: {e}")
        raise SystemExit(1)
