

import subprocess

def pesquisar_pacote(nome):

    try:
        resultado = subprocess.run(
            ["pkg", "search", nome],
            capture_output=True,
            text=True
        )

        return resultado.stdout

    except Exception as e:
        return str(e)


def instalar_pacote(nome):

    comando = [
        "pkg",
        "install",
        "-y",
        nome
    ]

    return subprocess.run(
        comando,
        capture_output=True,
        text=True
    ).stdout


if __name__ == "__main__":

    import sys

    acao = sys.argv[1]
    pacote = sys.argv[2]

    if acao == "buscar":
        print(pesquisar_pacote(pacote))

    elif acao == "instalar":
        print(instalar_pacote(pacote))
