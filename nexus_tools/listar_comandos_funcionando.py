import os
import json
import firebase_admin
from firebase_admin import credentials, db

print("=== COMANDOS CONFIRMADOS COMO FUNCIONANDO ===")

if not firebase_admin._apps:
    private_key = os.environ.get("private_key")

    if not private_key:
        print("ERRO: variável private_key não encontrada.")
        raise SystemExit(1)

    service_account = json.loads(private_key)

    firebase_admin.initialize_app(
        credentials.Certificate(service_account),
        {
            "databaseURL":
            "https://finance-master-629d1-default-rtdb.firebaseio.com"
        }
    )

ref = db.reference("nexus/comandos_funcionando")
dados = ref.get()

if not dados:
    print("Nenhum comando confirmado encontrado.")
    raise SystemExit(0)

for comando, info in dados.items():
    if isinstance(info, dict):
        resultado = info.get("resultado", "")
        print(f"- {comando} → FUNCIONA")
        if resultado:
            print(f"  Resultado: {resultado}")
    else:
        print(f"- {comando} → FUNCIONA")
