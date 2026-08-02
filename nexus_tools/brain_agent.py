
import subprocess
from pathlib import Path
from logger import registrar

BASE = Path(__file__).parent

def consultar(pergunta):

    registrar("CONSULTA", pergunta)

    # 1 - Memória
    try:
        memoria = subprocess.run(
            [
                "python3",
                str(BASE / "recall.py"),
                pergunta
            ],
            capture_output=True,
            text=True
        ).stdout.strip()

        if memoria and "Não encontrado" not in memoria:
            return memoria

    except Exception:
        pass

    # 2 - BashSearch
    try:
        resposta = subprocess.run(
            [
                "python3",
                str(BASE / "knowledge.py"),
                pergunta
            ],
            capture_output=True,
            text=True
        ).stdout.strip()

        if resposta:

            gravar = subprocess.run(
                [
                    "python3",
                    str(BASE / "quality.py"),
                    pergunta,
                    resposta
                ],
                capture_output=True,
                text=True
            ).stdout.strip()

            if gravar == "True":

                subprocess.run(
                    [
                        "python3",
                        str(BASE / "learn.py"),
                        pergunta,
                        resposta
                    ],
                    capture_output=True,
                    text=True
                )

            return resposta

    except Exception:
        pass

    # 3 - Documentação do Termux
    try:
        resposta = subprocess.check_output(
            [
                "python3",
                str(BASE / "termux_knowledge.py"),
                pergunta
            ],
            text=True
        ).strip()

        if resposta and resposta != "Nada encontrado.":

            resumo = subprocess.run(
                [
                    "python3",
                    str(BASE / "summarize_help.py"),
                    pergunta,
                    "/dev/stdin"
                ],
                input=resposta,
                capture_output=True,
                text=True
            ).stdout.strip()

            if resumo:
                resposta = resumo

            gravar = subprocess.run(
                [
                    "python3",
                    str(BASE / "quality.py"),
                    pergunta,
                    resposta
                ],
                capture_output=True,
                text=True
            ).stdout.strip()

            if gravar == "True":

                subprocess.run(
                    [
                        "python3",
                        str(BASE / "learn.py"),
                        pergunta,
                        resposta
                    ],
                    capture_output=True,
                    text=True
                )

            return resposta

    except Exception:
        pass

    return "Não consegui encontrar conhecimento."


if __name__ == "__main__":
    import sys
    print(consultar(" ".join(sys.argv[1:])))
