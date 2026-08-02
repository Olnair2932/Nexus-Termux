

from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

ARQUIVO = BASE / "workspace/html/index_test.html"
LOG = BASE / "logs/nexus.log"


def registrar(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [DASHBOARD EDITOR] {msg}\n"
        )


def melhorar():

    if not ARQUIVO.exists():
        print("Arquivo de teste não encontrado.")
        return

    texto = ARQUIVO.read_text(
        encoding="utf-8"
    )

    marca = "<!-- Nexus Optimization Test -->"

    if marca not in texto:

        texto = marca + "\n" + texto

        ARQUIVO.write_text(
            texto,
            encoding="utf-8"
        )

        registrar(
            "Marca de otimização adicionada ao dashboard de teste"
        )

        print("✅ Melhoria aplicada no teste.")

    else:
        print("ℹ️ Melhoria já aplicada.")


if __name__ == "__main__":
    melhorar()
