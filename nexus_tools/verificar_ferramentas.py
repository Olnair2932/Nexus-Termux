#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = ROOT / "skills.json"
TOOLS_DIR = ROOT / "nexus_tools"

# Módulos internos de infraestrutura não são ferramentas executáveis.
ARQUIVOS_INTERNOS = {
    "firebase_storage.py",
}


def main():
    print("🔎 VERIFICAÇÃO DE FERRAMENTAS")
    print("=============================")

    if not SKILLS_FILE.exists():
        print("❌ skills.json não encontrado.")
        raise SystemExit(1)

    if not TOOLS_DIR.exists():
        print("❌ Diretório nexus_tools não encontrado.")
        raise SystemExit(1)

    try:
        with SKILLS_FILE.open(encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as erro:
        print(f"❌ Não foi possível ler skills.json: {erro}")
        raise SystemExit(1)

    skills = dados.get("skills", {})

    if not isinstance(skills, dict):
        print("❌ Estrutura inválida: 'skills' não é um objeto.")
        raise SystemExit(1)

    scripts = sorted(
        p for p in TOOLS_DIR.glob("*.py")
        if (
            p.is_file()
            and p.name != "__init__.py"
            and p.name not in ARQUIVOS_INTERNOS
        )
    )

    registrados = set()
    problemas = []

    for nome, skill in skills.items():
        if not isinstance(skill, dict):
            continue

        if skill.get("executor") != "python":
            continue

        script = skill.get("script")

        if not script:
            continue

        caminho = Path(script)

        if caminho.parts and caminho.parts[0] == "nexus_tools":
            registrados.add(caminho.name)
        else:
            registrados.add(caminho.name)

    nomes_scripts = {p.name for p in scripts}

    nao_registrados = sorted(nomes_scripts - registrados)
    registrados_inexistentes = sorted(registrados - nomes_scripts)

    print(f"Scripts Python encontrados       {len(scripts)}")
    print(f"Scripts registrados              {len(registrados)}")
    print(f"Scripts não registrados          {len(nao_registrados)}")
    print(f"Registros sem script local       {len(registrados_inexistentes)}")

    if nao_registrados:
        print()
        print("⚠️ SCRIPTS NÃO REGISTRADOS")
        print("==========================")

        for nome in nao_registrados:
            print(f"- {nome}")

        problemas.extend(
            f"Script não registrado: {nome}"
            for nome in nao_registrados
        )

    if registrados_inexistentes:
        print()
        print("⚠️ REGISTROS SEM SCRIPT LOCAL")
        print("=============================")

        for nome in registrados_inexistentes:
            print(f"- {nome}")

        problemas.extend(
            f"Registro sem script local: {nome}"
            for nome in registrados_inexistentes
        )

    if problemas:
        print()
        print("⚠️ RESULTADO: FERRAMENTAS COM DIFERENÇAS")
        raise SystemExit(1)

    print()
    print("✅ RESULTADO: FERRAMENTAS E REGISTROS COERENTES")


if __name__ == "__main__":
    main()
