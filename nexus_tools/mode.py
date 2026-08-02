

import json
from pathlib import Path

ARQ = Path.home() / "sentinela_dev/brain_mode.json"

def modo_atual():
    if not ARQ.exists():
        return "online"

    dados = json.loads(ARQ.read_text(encoding="utf-8"))
    return dados.get("modo", "online")


def alterar_modo(novo):
    dados = {"modo": novo}

    ARQ.write_text(
        json.dumps(dados, indent=4),
        encoding="utf-8"
    )

    return novo


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print(modo_atual())

    elif sys.argv[1] == "online":
        alterar_modo("online")
        print("Modo ONLINE")

    elif sys.argv[1] == "aprendizado":
        alterar_modo("aprendizado")
        print("Modo APRENDIZADO")
