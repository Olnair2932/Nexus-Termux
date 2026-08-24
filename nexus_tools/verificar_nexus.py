#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "nexus_tools"

VERIFICACOES = [
    "verificar_skills.py",
    "verificar_ferramentas.py",
    "auditar_ferramentas.py",
]


def executar(nome):
    arquivo = TOOLS_DIR / nome

    if not arquivo.exists():
        print(f"❌ Ferramenta não encontrada: {nome}")
        return False

    print()
    print(f"▶️ {nome}")
    print("-" * 40)

    resultado = subprocess.run(
        [sys.executable, str(arquivo)],
        cwd=ROOT,
    )

    return resultado.returncode == 0


def main():
    print("🔎 VERIFICAÇÃO CONSOLIDADA DO NEXUS")
    print("===================================")

    resultados = []

    for nome in VERIFICACOES:
        resultados.append((nome, executar(nome)))

    print()
    print("===================================")
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("===================================")

    falhas = 0

    for nome, sucesso in resultados:
        if sucesso:
            print(f"✅ {nome}")
        else:
            print(f"❌ {nome}")
            falhas += 1

    print()

    if falhas:
        print(f"⚠️ RESULTADO: {falhas} verificação(ões) falharam.")
        raise SystemExit(1)

    print("✅ RESULTADO: NEXUS APROVADO NAS VERIFICAÇÕES")


if __name__ == "__main__":
    main()
