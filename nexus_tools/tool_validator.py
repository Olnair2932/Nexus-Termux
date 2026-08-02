

import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
REG = BASE / "tools_registry.json"
TOOLS = BASE / "nexus_tools"
LOG = BASE / "logs/nexus.log"


def registrar(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [VALIDADOR] {msg}\n"
        )


def validar(nome):

    dados = json.loads(
        REG.read_text(encoding="utf-8")
    )

    for ferramenta in dados["tools"]:

        if ferramenta["nome"] == nome:

            arquivo = TOOLS / ferramenta["arquivo"]

            teste = subprocess.run(
                ["python3", str(arquivo)],
                capture_output=True,
                text=True
            )

            if teste.returncode == 0:

                ferramenta["status"] = "ativo"

                REG.write_text(
                    json.dumps(
                        dados,
                        indent=4,
                        ensure_ascii=False
                    ),
                    encoding="utf-8"
                )

                registrar(
                    f"{nome} aprovado e ativado"
                )

                print("✅ Ferramenta aprovada.")
                return

            else:
                registrar(
                    f"{nome} falhou no teste"
                )
                print("❌ Falha na ferramenta.")
                return

    print("Ferramenta não encontrada.")


if __name__ == "__main__":
    import sys

    validar(sys.argv[1])
