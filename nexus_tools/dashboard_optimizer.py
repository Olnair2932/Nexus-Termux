

from pathlib import Path
import json
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

DASHBOARD = BASE / "public/index.html"
RELATORIO = BASE / "logs/dashboard_plan.json"


def analisar():

    plano = []

    if not DASHBOARD.exists():

        plano.append({
            "tipo": "erro",
            "acao": "Criar dashboard base",
            "status": "pendente"
        })

    else:

        tamanho = DASHBOARD.stat().st_size

        plano.append({
            "tipo": "analise",
            "arquivo": "index.html",
            "tamanho": tamanho,
            "sugestao": [
                "Verificar organização do código",
                "Melhorar interface",
                "Adicionar recursos solicitados pelos logs"
            ],
            "data": datetime.now().isoformat()
        })


    RELATORIO.write_text(
        json.dumps(
            plano,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


    print("✅ Plano do dashboard criado.")


if __name__ == "__main__":
    analisar()
