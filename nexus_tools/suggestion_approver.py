

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

PLAN = BASE / "suggestion_plan.json"
LOG = BASE / "logs/nexus.log"


def aprovar():

    if not PLAN.exists():
        print("Nenhum plano encontrado.")
        return

    planos = json.loads(
        PLAN.read_text(encoding="utf-8")
    )

    for p in planos:
        p["status"] = "aprovado"
        p["aprovado_em"] = datetime.now().isoformat()

    PLAN.write_text(
        json.dumps(
            planos,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [SUGESTAO] Plano aprovado\n"
        )

    print("✅ Plano aprovado.")


if __name__ == "__main__":
    aprovar()
