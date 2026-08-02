

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
REG = BASE / "tools_registry.json"
TOOLS = BASE / "nexus_tools"
LOG = BASE / "logs/nexus.log"
REL = BASE / "logs/tool_audit.json"


def registrar(texto):

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [AUDITOR] {texto}\n"
        )


def auditar():

    dados = json.loads(
        REG.read_text(encoding="utf-8")
    )

    resultado = []

    for ferramenta in dados["tools"]:

        arquivo = TOOLS / ferramenta["arquivo"]

        item = {
            "nome": ferramenta["nome"],
            "arquivo": ferramenta["arquivo"],
            "status_catalogo": ferramenta["status"],
            "existe": arquivo.exists(),
            "data": datetime.now().isoformat()
        }

        if arquivo.exists():
            item["resultado"] = "OK"
        else:
            item["resultado"] = "ARQUIVO AUSENTE"
            registrar(
                f'Ferramenta ausente: {ferramenta["nome"]}'
            )

        resultado.append(item)

    REL.write_text(
        json.dumps(
            resultado,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("=== AUDITORIA NEXUS ===")

    for r in resultado:
        print(
            r["nome"],
            "->",
            r["resultado"]
        )


if __name__ == "__main__":
    auditar()
