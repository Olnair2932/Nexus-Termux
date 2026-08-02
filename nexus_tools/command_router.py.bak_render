
from pathlib import Path
import json
import subprocess
from tool_discovery import procurar
import sys

BASE = Path.home() / "sentinela_dev"

SKILLS = json.loads(
    (BASE / "skills.json").read_text(encoding="utf-8")
)["skills"]


def executar(acao):

    print("ACTION:", acao)

    if acao not in SKILLS:

        encontrados = procurar(acao)

        if encontrados:

            nome, info = encontrados[0]

            print("\n🔎 TOOL DISCOVERY")
            print("Ferramenta:", nome)
            print("Categoria :", info["categoria"])

            resultado = subprocess.run(
                [
                    "python3",
                    str(BASE / info["arquivo"])
                ],
                capture_output=True,
                text=True
            )

            print(resultado.stdout)

            if resultado.stderr:
                print(resultado.stderr)

            return

        print("❌ Skill não encontrada.")
        return

    skill = SKILLS[acao]

    executor = skill["executor"]

    if executor == "bash":

        comando = skill["comando"]

        print("\nExecutando Bash seguro:")
        print(comando)

        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True
        )

    elif executor == "python":

        script = BASE / skill["script"]

        print("\nExecutando Python:")
        print(script.name)

        resultado = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True
        )

    elif executor == "termux":

        comando = skill["comando"]

        print("\nExecutando API Termux:")
        print(comando)

        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True
        )

    else:

        print("❌ Executor ainda não suportado:", executor)
        return

    print("""
====================
NEXUS RESULTADO
====================
""")

    print("Ação:", acao)
    print("Executor:", executor)

    if resultado.returncode == 0:
        print("Validação: OK")
        print("Status: CONCLUÍDO")
    else:
        print("Validação: ERRO")
        print("Status: FALHA")

    print("Resultado:")
    print(resultado.stdout)

    if resultado.stderr:
        print("\nErro:")
        print(resultado.stderr)


if __name__ == "__main__":

    if len(sys.argv) > 1:
        executar(sys.argv[1])
    else:
        print("====== NEXUS SKILLS ENGINE ======")
        print("Skills disponíveis:\n")

        for nome in sorted(SKILLS):
            print("-", nome)
