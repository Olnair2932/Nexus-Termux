

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

SUG = BASE / "suggestions.json"
PLAN = BASE / "suggestion_plan.json"
LOG = BASE / "logs/nexus.log"


def classificar(texto):

    t = texto.lower()

    if "dashboard" in t or "interface" in t:
        return "interface"

    if "erro" in t or "corrigir" in t:
        return "correcao"

    if "ferramenta" in t or "modulo" in t:
        return "nova_ferramenta"

    if "segurança" in t:
        return "seguranca"

    return "otimizacao"


def analisar():

    if not SUG.exists():
        print("Nenhuma sugestão encontrada.")
        return

    sugestoes = json.loads(
        SUG.read_text(encoding="utf-8")
    )

    planos = []

    for item in sugestoes:

        categoria = classificar(
            item["sugestao"]
        )

        plano = {
            "sugestao": item["sugestao"],
            "categoria": categoria,
            "acao": "Criar plano de melhoria",
            "status": "aguardando_aprovacao",
            "data": datetime.now().isoformat()
        }

        planos.append(plano)

        item["status"] = "analisada"

    PLAN.write_text(
        json.dumps(
            planos,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    SUG.write_text(
        json.dumps(
            sugestoes,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [ANALISE_SUGESTAO] {len(planos)} plano(s) criado(s)\n"
        )

    print("✅ Sugestões analisadas.")
    print("Planos criados:", len(planos))


if __name__ == "__main__":
    analisar()
