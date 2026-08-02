

import re

def resumir(comando, texto):

    linhas = [
        l.strip()
        for l in texto.splitlines()
        if l.strip()
    ]

    resumo = []

    resumo.append(comando)

    for linha in linhas:

        if linha.lower().startswith("usage"):
            resumo.append(linha)
            break

    ignorar = (
        "--help",
        "--version",
        "gnu",
        "copyright",
        "bug",
        "https://",
        "e-mail"
    )

    contador = 0

    for linha in linhas:

        if any(x in linha.lower() for x in ignorar):
            continue

        if linha.lower().startswith("usage"):
            continue

        if linha.startswith("-"):
            resumo.append(linha)
            contador += 1

        if contador >= 8:
            break

    return "\\n".join(resumo)


if __name__ == "__main__":

    import sys
    from pathlib import Path

    comando = sys.argv[1]
    texto = Path(sys.argv[2]).read_text(encoding="utf-8")

    print(resumir(comando, texto))
