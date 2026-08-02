

from pathlib import Path
import json
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

PLAN = BASE / "logs/repair_plan.json"
LOG = BASE / "logs/nexus.log"


def registrar(msg):

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [REPAIR_EXECUTOR] {msg}\n"
        )


def executar():

    if not PLAN.exists():

        print("Nenhum plano de reparo encontrado.")
        return


    plano = json.loads(
        PLAN.read_text(
            encoding="utf-8"
        )
    )


    if not plano:

        print("✅ Nenhum reparo pendente.")
        registrar(
            "Nenhum reparo pendente"
        )
        return


    for item in plano:

        ferramenta = item.get(
            "ferramenta",
            "desconhecida"
        )

        acao = item.get(
            "acao",
            "sem ação"
        )

        print(
            f"Executando: {ferramenta} -> {acao}"
        )

        registrar(
            f"Plano executado: {ferramenta} - {acao}"
        )


if __name__ == "__main__":
    executar()
