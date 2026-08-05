import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

BRAIN = BASE / "brain.json"
SUG = BASE / "suggestions.json"


def gerar():

    if not BRAIN.exists():
        print("brain.json não encontrado.")
        return

    brain = json.loads(
        BRAIN.read_text(encoding="utf-8")
    )

    erros = brain.get(
        "erros_aprendidos",
        []
    )

    sugestoes = []
    vistos = set()

    for erro in erros:

        texto = erro.get("erro", "")

        if texto in vistos:
            continue

        vistos.add(texto)

        sugestoes.append({
            "sugestao": f"Corrigir erro recorrente: {texto}",
            "origem": "log_analyzer",
            "status": "nova",
            "data": datetime.now().isoformat()
        })


    SUG.write_text(
        json.dumps(
            sugestoes,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("✅ Sugestões geradas:", len(sugestoes))


if __name__ == "__main__":
    gerar()
