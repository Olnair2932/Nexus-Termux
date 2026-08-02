

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

HISTORY = BASE / "logs/evolution_history.json"
PLAN = BASE / "suggestion_plan.json"


def registrar():

    if not PLAN.exists():
        print("Nenhuma evolução encontrada.")
        return

    planos = json.loads(
        PLAN.read_text(encoding="utf-8")
    )

    historico = []

    if HISTORY.exists():
        historico = json.loads(
            HISTORY.read_text(encoding="utf-8")
        )

    for item in planos:

        if item.get("status") == "aplicado":

            registro = {
                "evento": item["sugestao"],
                "categoria": item["categoria"],
                "status": "concluido",
                "data": datetime.now().isoformat()
            }

            if registro not in historico:
                historico.append(registro)

    HISTORY.write_text(
        json.dumps(
            historico,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("✅ Histórico de evolução atualizado.")
    print(f"Evoluções registradas: {len(historico)}")


if __name__ == "__main__":
    registrar()
