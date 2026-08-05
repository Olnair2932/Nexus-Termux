from pathlib import Path
from datetime import datetime
import os

BASE = Path(
    os.environ.get(
        "NEXUS_ROOT",
        Path.cwd()
    )
)

LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ARQ = LOG_DIR / "nexus.log"


def registrar(tipo, mensagem):

    agora = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        ARQ,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            f"[{agora}] [{tipo}] {mensagem}\n"
        )


if __name__ == "__main__":

    registrar(
        "TESTE",
        "Logger Nexus funcionando"
    )

    print(
        f"Registro criado em: {ARQ}"
    )
