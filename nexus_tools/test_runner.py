

from pathlib import Path
import subprocess

BASE = Path.home() / "sentinela_dev"
WORK = BASE / "workspace"

TESTES = []

# Testa todos os arquivos Python do workspace
for arq in (WORK / "python").glob("*.py"):
    TESTES.append([
        "python3",
        "-m",
        "py_compile",
        str(arq)
    ])

def executar():

    aprovados = 0

    for teste in TESTES:

        r = subprocess.run(
            teste,
            capture_output=True,
            text=True
        )

        if r.returncode == 0:
            aprovados += 1
        else:
            print("❌ ERRO:")
            print(teste[-1])
            print(r.stderr)
            return False

    print(f"✅ {aprovados} arquivos Python aprovados.")

    return True


if __name__ == "__main__":
    executar()
