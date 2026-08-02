

from pathlib import Path
import json
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

AUDIT = BASE / "logs/tool_audit.json"
PLAN = BASE / "logs/repair_plan.json"
LOG = BASE / "logs/nexus.log"


def registrar(texto):

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [REPARO] {texto}\n"
        )


def analisar():

    if not AUDIT.exists():
        print("Nenhuma auditoria encontrada.")
        return

    dados = json.loads(
        AUDIT.read_text(encoding="utf-8")
    )

    plano = []

    for ferramenta in dados:

        if ferramenta["resultado"] != "OK":

            plano.append({
                "ferramenta": ferramenta["nome"],
                "acao": "Reparar arquivo",
                "status": "pendente"
            })


    PLAN.write_text(
        json.dumps(
            plano,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


    if plano:

        registrar(
            f"{len(plano)} reparos planejados"
        )

        print(
            "⚠️ Plano de reparo criado."
        )

    else:

        registrar(
            "Nenhum reparo necessário"
        )

        print(
            "✅ Nenhum reparo necessário."
        )


if __name__ == "__main__":
    analisar()
