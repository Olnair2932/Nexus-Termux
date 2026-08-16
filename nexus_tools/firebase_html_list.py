import os
import json
import firebase_admin
from firebase_admin import credentials, db

try:
    if not firebase_admin._apps:
        private_key = os.environ.get("private_key")

        if not private_key:
            print("ERRO: variável private_key não encontrada.")
            raise SystemExit(1)

        service_account = json.loads(private_key)

        cred = credentials.Certificate(service_account)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL":
                "https://finance-master-629d1-default-rtdb.firebaseio.com"
            }
        )

    ref = db.reference("nexus/html_gerados")
    dados = ref.get()

    print("=== HTMLs ARMAZENADOS NO FIREBASE ===")

    if not dados:
        print("Nenhum HTML encontrado.")
        raise SystemExit(0)

    if isinstance(dados, dict):
        for chave, valor in dados.items():
            print(f"- {chave}")

    else:
        print(dados)

    print("=== FIM ===")

except Exception as e:
    print(f"ERRO FIREBASE: {e}")
    raise SystemExit(1)
