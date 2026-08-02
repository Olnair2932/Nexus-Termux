
import json
from pathlib import Path

BASE = Path.home() / "sentinela_dev"
CATALOGO = BASE / "tools_catalog.json"


def carregar_catalogo():
    if not CATALOGO.exists():
        return {}
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def procurar(texto):

    texto = texto.lower()

    catalogo = carregar_catalogo()

    resultados = []

    for nome, dados in catalogo.items():

        if texto in nome.lower():
            resultados.append((nome, dados))
            continue

        if texto in dados.get("categoria", "").lower():
            resultados.append((nome, dados))
            continue

        for func in dados.get("funcoes", []):
            if texto in func.lower():
                resultados.append((nome, dados))
                break

    return resultados


if __name__ == "__main__":

    consulta = input("Pesquisar: ")

    achados = procurar(consulta)

    print()

    if not achados:
        print("Nenhuma ferramenta encontrada.")
    else:
        print("Ferramentas encontradas:\n")

        for nome, dados in achados:
            print(nome)
            print(" Categoria :", dados["categoria"])
            print(" Arquivo   :", dados["arquivo"])
            print(" Executor  :", dados["executor"])
            print(" Funções   :", ", ".join(dados["funcoes"]))
            print()
