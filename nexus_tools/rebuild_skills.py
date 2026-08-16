#!/usr/bin/env python3

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "nexus_tools"
SKILLS_FILE = ROOT / "skills.json"

IGNORAR = {
    "__pycache__",
}

EXTENSOES_IGNORAR = (
    ".bak",
    ".old",
    ".tmp",
)


def carregar_skills():
    if not SKILLS_FILE.exists():
        return {"skills": {}}

    try:
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if not isinstance(dados, dict):
            dados = {}

        if not isinstance(dados.get("skills"), dict):
            dados["skills"] = {}

        return dados

    except Exception as e:
        print("Erro ao ler skills.json:", e)
        return {"skills": {}}


def main():
    dados = carregar_skills()
    skills = dados["skills"]

    encontrados = []
    novas = []

    for arquivo in sorted(TOOLS_DIR.glob("*.py")):
        nome = arquivo.stem

        if nome in IGNORAR:
            continue

        if arquivo.name.endswith(EXTENSOES_IGNORAR):
            continue

        encontrados.append(nome)

        if nome not in skills:
            skills[nome] = {
                "executor": "python",
                "script": f"nexus_tools/{arquivo.name}"
            }

            novas.append(nome)

    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )
        f.write("\n")

    print()
    print("====================================")
    print(" NEXUS REBUILD SKILLS")
    print("====================================")
    print(f"Ferramentas encontradas: {len(encontrados)}")
    print(f"Novas registradas:       {len(novas)}")

    if novas:
        print()
        print("NOVAS FERRAMENTAS:")
        for nome in novas:
            print(" +", nome)
    else:
        print()
        print("Nenhuma ferramenta nova.")

    print()
    print("skills.json atualizado.")
    print("====================================")


if __name__ == "__main__":
    main()
