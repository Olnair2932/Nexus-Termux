

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

ARQUIVO = BASE / "suggestions.json"
LOG = BASE / "logs/nexus.log"


def registrar(sugestao):

    dados = []

    if ARQUIVO.exists():
        dados = json.loads(
            ARQUIVO.read_text(
                encoding="utf-8"
            )
        )

    item = {
        "sugestao": sugestao,
        "status": "pendente",
        "data": datetime.now().isoformat()
    }

    dados.append(item)

    ARQUIVO.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [SUGESTAO] {sugestao}\n"
        )

    print("✅ Sugestão registrada.")


def listar():

    if not ARQUIVO.exists():
        print("Nenhuma sugestão.")
        return

    dados = json.loads(
        ARQUIVO.read_text(
            encoding="utf-8"
        )
    )

    print("=== SUGESTÕES NEXUS ===")

    for s in dados:
        print(
            s["status"],
            "-",
            s["sugestao"]
        )


if __name__ == "__main__":

    print("NEXUS SUGGESTION MANAGER")

    texto = input(
        "Digite uma sugestão: "
    )

    registrar(texto)
