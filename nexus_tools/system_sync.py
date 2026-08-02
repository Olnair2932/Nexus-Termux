

from pathlib import Path
import shutil
import json
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

ORIGENS = [
    BASE / "nexus_tools",
    BASE / "public",
]

DESTINO = BASE / "workspace"

HIST = BASE / "logs/system_sync.json"


def registrar(total):

    if HIST.exists():
        dados = json.loads(
            HIST.read_text(encoding="utf-8")
        )
    else:
        dados = []

    dados.append({
        "arquivos_sincronizados": total,
        "data": datetime.now().isoformat()
    })

    HIST.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def sincronizar():

    total = 0

    for origem in ORIGENS:

        if not origem.exists():
            continue

        destino = DESTINO / origem.name

        destino.mkdir(
            parents=True,
            exist_ok=True
        )

        for arquivo in origem.rglob("*"):

            if arquivo.is_file():

                relativo = arquivo.relative_to(origem)

                copia = destino / relativo

                copia.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                shutil.copy2(
                    arquivo,
                    copia
                )

                total += 1

    registrar(total)

    print(
        f"✅ Sistema sincronizado: {total} arquivos."
    )


if __name__ == "__main__":
    sincronizar()
