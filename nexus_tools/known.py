

import json
from pathlib import Path

BRAIN = Path.home() / "sentinela_dev/brain.json"

def conhece(chave):

    if not BRAIN.exists():
        return False

    dados = json.loads(
        BRAIN.read_text(encoding="utf-8")
    )

    return chave in dados.get("conhecimentos", {})


if __name__ == "__main__":

    import sys

    print(conhece(sys.argv[1]))
