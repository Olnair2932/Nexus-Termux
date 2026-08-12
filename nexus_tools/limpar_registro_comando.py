#!/usr/bin/env python3

import os
import json
import firebase_admin
from firebase_admin import credentials, db

DATABASE_URL = "https://finance-master-629d1-default-rtdb.firebaseio.com"

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

alvo = "listar_comandos_funcionando"

ref = db.reference(
    f"nexus/comandos_funcionando/{alvo}"
)

ref.delete()

print("=== LIMPEZA DA MEMÓRIA NEXUS ===")
print()
print(f"Registro removido: {alvo}")
print("Firebase: OK")
