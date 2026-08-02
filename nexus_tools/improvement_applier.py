

import json
from pathlib import Path
from datetime import datetime
import shutil

BASE = Path.home() / "sentinela_dev"

PLAN = BASE / "suggestion_plan.json"
WORKSPACE = BASE / "workspace/html/index_test.html"
BACKUP = BASE / "backups"
LOG = BASE / "logs/nexus.log"


def aplicar():

    if not PLAN.exists():
        print("Nenhum plano encontrado.")
        return

    planos = json.loads(
        PLAN.read_text(encoding="utf-8")
    )

    for plano in planos:

        if plano["status"] != "aprovado":
            continue

        if plano["categoria"] == "interface":

            if WORKSPACE.exists():

                BACKUP.mkdir(exist_ok=True)

                destino = BACKUP / (
                    "index_test_"
                    + datetime.now().strftime("%Y%m%d_%H%M%S")
                    + ".bak"
                )

                shutil.copy(
                    WORKSPACE,
                    destino
                )

                texto = WORKSPACE.read_text(
                    encoding="utf-8"
                )

                marca = "\n<!-- Nexus Dashboard Improvement Applied -->\n"

                if marca not in texto:
                    texto += marca

                WORKSPACE.write_text(
                    texto,
                    encoding="utf-8"
                )

                plano["status"] = "aplicado"
                plano["aplicado_em"] = datetime.now().isoformat()

                with open(LOG, "a", encoding="utf-8") as f:
                    f.write(
                        f"[{datetime.now()}] [MELHORIA] Dashboard atualizado\n"
                    )

                print("✅ Melhoria aplicada no dashboard teste.")

    PLAN.write_text(
        json.dumps(
            planos,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


if __name__ == "__main__":
    aplicar()
