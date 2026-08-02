

import json
from pathlib import Path
from datetime import datetime

BRAIN = Path.home() / "sentinela_dev/brain.json"


def aprender(chave, valor):

    dados = json.loads(
        BRAIN.read_text(encoding="utf-8")
    )

    if "conhecimentos" not in dados:
        dados["conhecimentos"] = {}

    dados["conhecimentos"][chave] = {
        "conteudo": valor,
        "data": datetime.now().isoformat()
    }

    BRAIN.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return True


if __name__ == "__main__":
    import sys

    aprender(
        sys.argv[1],
        sys.argv[2]
    )

    print("Aprendido:",sys.argv[1])
