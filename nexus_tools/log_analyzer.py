
import re
from pathlib import Path

LOGS = Path.home() / "sentinela_dev/logs"

def analisar():

    erros = {}
    total = 0

    if not LOGS.exists():
        print("Nenhuma pasta de logs.")
        return

    for arq in LOGS.glob("*"):

        if not arq.is_file():
            continue

        try:
            texto = arq.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:
            continue

        total += 1

        for linha in texto.splitlines():

            if (
                "erro" in linha.lower()
                or "exception" in linha.lower()
                or "traceback" in linha.lower()
            ):

                chave = linha.strip()

                erros[chave] = erros.get(chave, 0) + 1

    print(f"Arquivos analisados: {total}")

    if not erros:
        print("Nenhum erro recorrente encontrado.")
        return

    print("\nErros recorrentes:\n")

    for erro, qtd in sorted(
        erros.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"[{qtd}x] {erro}")

if __name__ == "__main__":
    analisar()
