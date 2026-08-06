import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
BRAIN = BASE / "brain.json"


def aprender():

    if not BRAIN.exists():
        print("brain.json não encontrado.")
        return

    dados = json.loads(
        BRAIN.read_text(encoding="utf-8")
    )

    melhorias = dados.get(
        "melhorias_aplicadas",
        []
    )

    memoria = dados.setdefault(
        "memoria_aprendizado",
        {}
    )

    aprendidas = memoria.setdefault(
        "melhorias_validadas",
        []
    )

    for item in melhorias:
        acao = item.get("acao")

        if acao and acao not in aprendidas:
            aprendidas.append(acao)

    dados["ultima_evolucao"] = datetime.now().isoformat()

    BRAIN.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("✅ Melhorias convertidas em aprendizado.")
    print("Total aprendidas:", len(aprendidas))


if __name__ == "__main__":
    aprender()
