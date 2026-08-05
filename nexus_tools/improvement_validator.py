from pathlib import Path
import json
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

BRAIN = BASE / "brain.json"
LOG = BASE / "logs/nexus.log"


def validar():

    resultado = {
        "data": datetime.now().isoformat(),
        "status": "OK",
        "testes": []
    }

    # Teste brain
    if BRAIN.exists():
        resultado["testes"].append(
            "brain.json encontrado"
        )
    else:
        resultado["status"] = "ERRO"
        resultado["testes"].append(
            "brain.json ausente"
        )

    # Teste melhorias
    try:
        brain = json.loads(
            BRAIN.read_text(encoding="utf-8")
        )

        melhorias = brain.get(
            "melhorias_aplicadas",
            []
        )

        resultado["testes"].append(
            f"melhorias registradas: {len(melhorias)}"
        )

    except Exception as e:
        resultado["status"] = "ERRO"
        resultado["testes"].append(
            str(e)
        )

    # Log
    if LOG.exists():
        resultado["testes"].append(
            "logs disponíveis"
        )

    print(json.dumps(
        resultado,
        indent=4,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    validar()
