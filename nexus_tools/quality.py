

import json
from pathlib import Path

ARQ = Path.home() / "sentinela_dev/brain.json"

def melhor(conhecimento_antigo, conhecimento_novo):

    if not conhecimento_antigo:
        return True

    antigo = conhecimento_antigo.strip()
    novo = conhecimento_novo.strip()

    # Não substitui por texto menor
    if len(novo) < len(antigo):
        return False

    # Prefere textos que tenham exemplo
    if "Exemplo" in novo and "Exemplo" not in antigo:
        return True

    # Prefere textos mais completos
    if len(novo) > len(antigo) * 1.20:
        return True

    return False


def deve_gravar(chave, novo):

    if not ARQ.exists():
        return True

    dados = json.loads(ARQ.read_text(encoding="utf-8"))

    antigo = dados.get(chave)

    return melhor(antigo, novo)


if __name__ == "__main__":

    import sys

    chave = sys.argv[1]
    texto = sys.argv[2]

    print(deve_gravar(chave, texto))
