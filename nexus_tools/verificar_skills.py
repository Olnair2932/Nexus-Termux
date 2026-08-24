#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = ROOT / "skills.json"


def main():
    print("🔎 VERIFICAÇÃO DE SKILLS")
    print("========================")

    if not SKILLS_FILE.exists():
        print("❌ skills.json não encontrado.")
        raise SystemExit(1)

    try:
        with SKILLS_FILE.open(encoding="utf-8") as f:
            dados = json.load(f)
    except json.JSONDecodeError as erro:
        print(f"❌ skills.json contém JSON inválido: {erro}")
        raise SystemExit(1)
    except Exception as erro:
        print(f"❌ Não foi possível ler skills.json: {erro}")
        raise SystemExit(1)

    skills = dados.get("skills")

    if not isinstance(skills, dict):
        print("❌ Estrutura inválida: 'skills' não é um objeto.")
        raise SystemExit(1)

    total = len(skills)
    validas = 0
    invalidas = 0

    problemas = []

    for nome, skill in skills.items():

        if not isinstance(skill, dict):
            problemas.append(
                f"{nome}: definição da skill não é um objeto"
            )
            invalidas += 1
            continue

        executor = skill.get("executor")

        if not executor:
            problemas.append(
                f"{nome}: executor ausente"
            )
            invalidas += 1
            continue

        if executor == "python":
            script = skill.get("script")

            if not script:
                problemas.append(
                    f"{nome}: script Python ausente"
                )
                invalidas += 1
                continue

            caminho = ROOT / script

            if not caminho.exists():
                problemas.append(
                    f"{nome}: script não encontrado: {script}"
                )
                invalidas += 1
                continue

        elif executor == "bash":
            comando = skill.get("comando")

            if not comando:
                problemas.append(
                    f"{nome}: comando bash ausente"
                )
                invalidas += 1
                continue

        validas += 1

    print(f"Skills analisadas        {total}")
    print(f"Skills válidas           {validas}")
    print(f"Skills com problemas     {invalidas}")

    if problemas:
        print()
        print("⚠️ PROBLEMAS ENCONTRADOS")
        print("========================")

        for problema in problemas:
            print(f"- {problema}")

        print()
        print("⚠️ RESULTADO: SKILLS COM PROBLEMAS")
        raise SystemExit(1)

    print()
    print("✅ RESULTADO: TODAS AS SKILLS ESTÃO VÁLIDAS")


if __name__ == "__main__":
    main()
