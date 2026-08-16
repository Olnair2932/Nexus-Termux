#!/usr/bin/env python3

import os
import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db


BASE = Path(__file__).resolve().parent.parent

HTML_DIR = BASE / "html_gerados"
VERSOES_DIR = HTML_DIR / "versoes"

FIREBASE_PATH = "nexus/html_gerados"

DATABASE_URL = (
    "https://finance-master-629d1-default-rtdb.firebaseio.com"
)


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
            "databaseURL": DATABASE_URL
        }
    )


def restaurar():
    conectar_firebase()

    HTML_DIR.mkdir(parents=True, exist_ok=True)
    VERSOES_DIR.mkdir(parents=True, exist_ok=True)

    ref = db.reference(FIREBASE_PATH)

    dados = ref.get()

    print("=== NEXUS RESTAURADOR DE HTML ===")
    print()
    print(f"Firebase: {FIREBASE_PATH}")
    print(f"Destino: {HTML_DIR}")
    print()

    if not dados:
        print("Nenhum HTML encontrado no Firebase.")
        print("=== FIM DA RESTAURAÇÃO ===")
        return

    restaurados = 0
    existentes = 0
    erros = 0

    for chave, registro in dados.items():

        try:
            if not isinstance(registro, dict):
                continue

            nome = registro.get("nome")
            html = registro.get("html")

            if not nome or not html:
                print(
                    f"⚠️ Registro ignorado: {chave}"
                )
                continue

            if not nome.endswith(".html"):
                nome += ".html"

            arquivo = HTML_DIR / nome
            versao = VERSOES_DIR / nome

            if arquivo.exists():
                print(
                    f"⏭️ Já existe: {nome}"
                )
                existentes += 1
                continue

            arquivo.write_text(
                html,
                encoding="utf-8"
            )

            versao.write_text(
                html,
                encoding="utf-8"
            )

            print(
                f"✅ Restaurado: {nome}"
            )

            restaurados += 1

        except Exception as erro:
            print(
                f"❌ Erro ao restaurar {chave}: {erro}"
            )
            erros += 1

    print()
    print(f"HTMLs restaurados: {restaurados}")
    print(f"HTMLs já existentes: {existentes}")
    print(f"Erros: {erros}")
    print()
    print("=== FIM DA RESTAURAÇÃO ===")


if __name__ == "__main__":
    try:
        restaurar()
    except Exception as erro:
        print(f"❌ ERRO: {erro}")
        raise SystemExit(1)
