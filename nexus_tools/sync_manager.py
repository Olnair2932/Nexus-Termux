

from pathlib import Path
import shutil
from datetime import datetime
import json

BASE = Path.home() / "sentinela_dev"

ORIGEM = BASE / "nexus_tools"
DESTINO = BASE / "workspace/python"

LOG = BASE / "logs/sync_history.json"


def registrar(evento):

    if LOG.exists():
        dados = json.loads(
            LOG.read_text(encoding="utf-8")
        )
    else:
        dados = []

    dados.append({
        "evento": evento,
        "data": datetime.now().isoformat()
    })

    LOG.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def sincronizar():

    DESTINO.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivos = 0

    for arquivo in ORIGEM.glob("*.py"):

        destino = DESTINO / arquivo.name

        shutil.copy2(
            arquivo,
            destino
        )

        arquivos += 1

    registrar(
        f"{arquivos} arquivos sincronizados"
    )

    print(
        f"✅ {arquivos} arquivos sincronizados para Workspace."
    )


if __name__ == "__main__":
    sincronizar()
