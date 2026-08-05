import json
from pathlib import Path

BASE = Path.home() / "sentinela_dev"
BRAIN = BASE / "brain.json"


def melhoria_ja_existe(acao):
    if not BRAIN.exists():
        return False

    try:
        brain = json.loads(
            BRAIN.read_text(encoding="utf-8")
        )
    except:
        return False

    melhorias = brain.get(
        "melhorias_aplicadas",
        []
    )

    for item in melhorias:
        if item.get("acao") == acao:
            return True

    return False


if __name__ == "__main__":
    print("Guard Nexus OK")
