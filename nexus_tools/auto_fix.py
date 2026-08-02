

from pathlib import Path
import shutil
import subprocess
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

WORKSPACE = BASE / "workspace/python"
LOG = BASE / "logs/nexus.log"


def registrar(msg):

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [AUTO_FIX] {msg}\n"
        )


def preparar(arquivo):

    origem = Path(arquivo)

    if not origem.exists():
        print("Arquivo não encontrado.")
        return

    destino = WORKSPACE / origem.name

    WORKSPACE.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        origem,
        destino
    )

    registrar(
        f"Cópia criada: {destino.name}"
    )

    print(
        "✅ Cópia preparada:",
        destino
    )

    verificar(destino)


def verificar(arquivo):

    resultado = subprocess.run(
        [
            "python3",
            str(BASE / "nexus_tools/syntax_checker.py"),
            str(arquivo)
        ],
        capture_output=True,
        text=True
    )

    if resultado.returncode == 0:
        registrar(
            f"{arquivo.name} validado"
        )
        print(
            "✅ Arquivo pronto para análise."
        )

    else:
        registrar(
            f"Falha na validação: {arquivo.name}"
        )
        print(
            resultado.stdout
        )


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print(
            "Uso: python3 auto_fix.py arquivo.py"
        )

    else:
        preparar(sys.argv[1])
