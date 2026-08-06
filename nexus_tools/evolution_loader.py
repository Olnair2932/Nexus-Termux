import json
from pathlib import Path

BASE = Path.home() / "sentinela_dev"
BRAIN = BASE / "brain.json"


def carregar():

    if not BRAIN.exists():
        print("brain.json não encontrado.")
        return

    dados = json.loads(
        BRAIN.read_text(encoding="utf-8")
    )

    memoria = dados.get(
        "memoria_aprendizado",
        {}
    )

    melhorias = memoria.get(
        "melhorias_validadas",
        []
    )

    print("=== NEXUS EVOLUTION LOADER ===")
    print("Melhorias carregadas:", len(melhorias))

    for item in melhorias:
        print("-", item)


if __name__ == "__main__":
    carregar()
