#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, db


DATABASE_URL = "https://finance-master-629d1-default-rtdb.firebaseio.com"
CAMINHO = "nexus/comandos_funcionando"


def conectar_firebase():
    if not os.environ.get("private_key"):
        raise RuntimeError(
            "Variável de ambiente private_key não encontrada."
        )

    if not firebase_admin._apps:
        service_account = json.loads(
            os.environ["private_key"]
        )

        cred = credentials.Certificate(service_account)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": DATABASE_URL
            }
        )


def atualizar_comando(comando, resultado):
    conectar_firebase()

    agora = datetime.now(timezone.utc).isoformat()

    chave = (
        comando.strip()
        .lower()
        .replace("/", "_")
        .replace(".", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )

    dados = {
        "comando": comando,
        "resultado": resultado,
        "status": "funcionando",
        "ambiente": "render",
        "ultima_confirmacao": agora
    }

    db.reference(f"{CAMINHO}/{chave}").set(dados)

    print("=== MEMÓRIA DE COMANDOS NEXUS ===")
    print()
    print("✅ Comando registrado no Firebase.")
    print(f"Comando: {comando}")
    print(f"Status: funcionando")
    print(f"Firebase: {CAMINHO}/{chave}")
    print(f"Resultado: {resultado}")


def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print(
            'python3 nexus_tools/atualizar_lista_comandos.py '
            '"COMANDO" "RESULTADO"'
        )
        sys.exit(1)

    comando = sys.argv[1]
    resultado = " ".join(sys.argv[2:])

    try:
        atualizar_comando(comando, resultado)

    except Exception as e:
        print("❌ Erro ao atualizar memória:")
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
