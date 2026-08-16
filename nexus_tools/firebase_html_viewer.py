import os
import sys
import json
import firebase_admin
from firebase_admin import credentials, db

IDENTIFICADOR = sys.argv[1] if len(sys.argv) > 1 else ""

if not IDENTIFICADOR:
    print("ERRO: informe o identificador do HTML.")
    sys.exit(1)

try:
    if not firebase_admin._apps:
        private_key = os.environ.get("private_key")

        if not private_key:
            print("ERRO: variável private_key não encontrada.")
            sys.exit(1)

        service_account = json.loads(private_key)

        cred = credentials.Certificate(service_account)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL":
                "https://finance-master-629d1-default-rtdb.firebaseio.com"
            }
        )

    caminhos = [
        f"nexus/html_gerados/{IDENTIFICADOR}",
        f"nexus/html_gerados/{IDENTIFICADOR}.html",
    ]

    resultado = None
    caminho_encontrado = None

    for caminho in caminhos:
        resultado = db.reference(caminho).get()

        if resultado is not None:
            caminho_encontrado = caminho
            break

    if resultado is None:
        print(f"HTML não encontrado no Firebase: {IDENTIFICADOR}")
        sys.exit(1)

    print("=== FIREBASE HTML VIEWER ===")
    print(f"Identificador: {IDENTIFICADOR}")
    print(f"Caminho: {caminho_encontrado}")
    print()
    print("=== HTML ===")

    if isinstance(resultado, dict):
        html = (
            resultado.get("html")
            or resultado.get("conteudo")
            or resultado.get("content")
        )

        if html:
            print(html)
        else:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        print(resultado)

    print()
    print("=== FIM ===")

except Exception as e:
    print(f"ERRO FIREBASE: {e}")
    sys.exit(1)
