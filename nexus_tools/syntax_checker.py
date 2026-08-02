

import ast
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
LOG = BASE / "logs/nexus.log"


def registrar(msg):

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [SINTAXE] {msg}\n"
        )


def verificar(arquivo):

    arquivo = Path(arquivo)

    if not arquivo.exists():
        print("Arquivo não encontrado.")
        return False

    try:

        ast.parse(
            arquivo.read_text(
                encoding="utf-8"
            )
        )

        registrar(
            f"{arquivo.name} aprovado"
        )

        print(
            "✅ Sintaxe correta:",
            arquivo.name
        )

        return True


    except SyntaxError as erro:

        registrar(
            f"{arquivo.name} erro: {erro}"
        )

        print(
            "❌ Erro de sintaxe:"
        )

        print(
            erro
        )

        return False


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print(
            "Uso: python3 syntax_checker.py arquivo.py"
        )
    else:
        verificar(sys.argv[1])
