#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db

DATABASE_URL = "https://finance-master-629d1-default-rtdb.firebaseio.com"

if len(sys.argv) < 2:
    print("ERRO: informe o nome/código do HTML.")
    raise SystemExit(1)

nome = sys.argv[1].strip()

if nome.endswith(".html"):
    nome = nome[:-5]

# Segurança: somente nome de arquivo, sem caminhos
nome = Path(nome).name

if not nome:
    print("ERRO: nome do HTML vazio.")
    raise SystemExit(1)

if not firebase_admin._apps:
    private_key = os.environ.get("private_key")

    if not private_key:
        raise RuntimeError(
            "Variável de ambiente private_key não encontrada."
        )

    service_account = json.loads(private_key)

    firebase_admin.initialize_app(
        credentials.Certificate(service_account),
        {
            "databaseURL": DATABASE_URL
        }
    )

# ============================================================
# FIREBASE
# ============================================================

ref = db.reference(f"nexus/html_gerados/{nome}")

existente = ref.get()

if existente is None:
    print(f"HTML não encontrado no Firebase: {nome}")
    raise SystemExit(1)

ref.delete()

# ============================================================
# ARQUIVO LOCAL
# ============================================================

base = Path(__file__).resolve().parent.parent
arquivo_local = base / "html_gerados" / f"{nome}.html"

if arquivo_local.exists():
    arquivo_local.unlink()
    local_status = "Arquivo local removido."
else:
    local_status = "Arquivo local não existia."

print("=== EXCLUSÃO DE HTML ===")
print()
print(f"HTML excluído: {nome}")
print("Firebase: registro removido.")
print(local_status)
print("Status: OK")
