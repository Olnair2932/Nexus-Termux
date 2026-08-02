

import json
from pathlib import Path

BRAIN = Path.home() / "sentinela_dev/brain.json"

def lembrar(chave):

    if not BRAIN.exists():
        return None

    dados = json.loads(
        BRAIN.read_text(encoding="utf-8")
    )

    conhecimentos = dados.get("conhecimentos", {})

    resultado = conhecimentos.get(chave)

    if resultado:
        return resultado["conteudo"]

    return None


if __name__ == "__main__":

    import sys

    pergunta = sys.argv[1]

    resposta = lembrar(pergunta)

    if resposta:
        print("Memória Nexus:")
        print(resposta)
    else:
        print("Não encontrado na memória.")
