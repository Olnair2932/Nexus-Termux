
import json
from pathlib import Path

from universal_executor import executar as interpretar
from tool_discovery import procurar

BASE = Path.home() / "sentinela_dev"

SKILLS = json.loads(
    (BASE / "skills.json").read_text(
        encoding="utf-8"
    )
)["skills"]


def decidir(frase):

    # 1 - Linguagem natural
    resultado = interpretar(frase)

    if resultado:
        return {
            "tipo": "skill",
            "dados": resultado
        }

    # 2 - Tool Discovery
    encontrados = procurar(frase)

    if encontrados:

        nome, info = encontrados[0]

        return {
            "tipo": "tool",
            "dados": info
        }

    # 3 - Nada encontrado
    return None


if __name__ == "__main__":

    pergunta = input("Pergunta: ")

    resultado = decidir(pergunta)

    print()
    print(resultado)
