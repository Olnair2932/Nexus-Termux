

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
REG = BASE / "tools_registry.json"
HIST = BASE / "logs/tools_history.json"


def carregar():
    return json.loads(
        REG.read_text(encoding="utf-8")
    )


def salvar(dados):
    REG.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def historico(evento, ferramenta):

    if HIST.exists():
        dados = json.loads(
            HIST.read_text(encoding="utf-8")
        )
    else:
        dados = []

    dados.append({
        "evento": evento,
        "ferramenta": ferramenta,
        "data": datetime.now().isoformat()
    })

    HIST.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def listar():

    dados = carregar()

    print("=== FERRAMENTAS NEXUS ===")

    for t in dados["tools"]:
        print(
            f'{t["nome"]} | {t["status"]}'
        )


def alterar(nome, status):

    dados = carregar()

    for t in dados["tools"]:

        if t["nome"] == nome:

            t["status"] = status

            salvar(dados)

            historico(
                status,
                nome
            )

            print(
                f"✅ {nome} -> {status}"
            )
            return

    print("Ferramenta não encontrada.")


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        listar()

    elif sys.argv[1] == "ativar":
        alterar(sys.argv[2], "ativo")

    elif sys.argv[1] == "desativar":
        alterar(sys.argv[2], "inativo")

    else:
        print("Comando inválido.")
