

from pathlib import Path
import json
import shutil
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

ORIGINAL = BASE / "public/index.html"
WORKSPACE = BASE / "workspace/html"

PLANO = BASE / "logs/dashboard_plan.json"
LOG = BASE / "logs/nexus.log"


def registrar(msg):

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [DASHBOARD] {msg}\n"
        )


def construir():

    if not ORIGINAL.exists():
        print("Dashboard original não encontrado.")
        return

    WORKSPACE.mkdir(
        parents=True,
        exist_ok=True
    )

    destino = WORKSPACE / "index_test.html"

    shutil.copy2(
        ORIGINAL,
        destino
    )

    plano = []

    if PLANO.exists():
        plano = json.loads(
            PLANO.read_text(encoding="utf-8")
        )

    registrar(
        f"Versão de teste criada: {destino.name}"
    )

    print("✅ Dashboard de teste criado.")
    print("Arquivo:", destino)
    print("Sugestões carregadas:", len(plano))


if __name__ == "__main__":
    construir()
