
from pathlib import Path
import json
import subprocess
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
BRAIN = BASE / "brain.json"


def carregar():
    return json.loads(
        BRAIN.read_text(encoding="utf-8")
    )


def executar(acao):
    brain = carregar()

    comandos = brain.get(
        "comandos_bash_aprendidos",
        {}
    )

    if acao not in comandos:
        return {
            "status": "ERRO",
            "mensagem": "Comando não autorizado"
        }

    item = comandos[acao]

    try:
        resultado = subprocess.check_output(
            item["comando"],
            shell=True,
            text=True,
            stderr=subprocess.STDOUT
        )

        return {
            "status": "OK",
            "acao": acao,
            "comando": item["comando"],
            "resultado": resultado.strip(),
            "data": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "ERRO",
            "mensagem": str(e)
        }


if __name__ == "__main__":
    import sys

    acao = sys.argv[1]

    resposta = executar(acao)

    print(
        json.dumps(
            resposta,
            indent=4,
            ensure_ascii=False
        )
    )
