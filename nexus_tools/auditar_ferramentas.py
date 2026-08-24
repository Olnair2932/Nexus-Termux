#!/usr/bin/env python3

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = ROOT / "skills.json"
TOOLS_DIR = ROOT / "nexus_tools"

ARQUIVOS_INTERNOS = {
    "firebase_storage.py",
}

ARQUIVOS_IGNORADOS = {
    "__init__.py",
}


def verificar_sintaxe(arquivo):
    try:
        ast.parse(arquivo.read_text(encoding="utf-8"))
        return True, ""
    except SyntaxError as erro:
        return False, f"{erro.msg} (linha {erro.lineno})"
    except Exception as erro:
        return False, str(erro)


def verificar_main(texto):
    return (
        'if __name__ == "__main__":' in texto
        or "if __name__ == '__main__':" in texto
    )


def verificar_imports(texto):
    problemas = []

    try:
        arvore = ast.parse(texto)
    except Exception:
        return problemas

    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom):
            if no.module and no.module.startswith("."):
                problemas.append(
                    f"import relativo não avaliado: {no.module}"
                )

    return problemas


def main():
    print("🔎 AUDITORIA DE FERRAMENTAS")
    print("===========================")

    if not TOOLS_DIR.exists():
        print("❌ Diretório nexus_tools não encontrado.")
        raise SystemExit(1)

    if not SKILLS_FILE.exists():
        print("❌ skills.json não encontrado.")
        raise SystemExit(1)

    try:
        with SKILLS_FILE.open(encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as erro:
        print(f"❌ Não foi possível ler skills.json: {erro}")
        raise SystemExit(1)

    skills = dados.get("skills", {})

    scripts = sorted(
        p for p in TOOLS_DIR.glob("*.py")
        if (
            p.is_file()
            and p.name not in ARQUIVOS_IGNORADOS
            and p.name not in ARQUIVOS_INTERNOS
        )
    )

    # Somente ferramentas Python registradas no skills.json
    # são consideradas executáveis e precisam de __main__.
    ferramentas_registradas = set()

    if isinstance(skills, dict):
        for skill in skills.values():
            if not isinstance(skill, dict):
                continue

            if skill.get("executor") != "python":
                continue

            script = skill.get("script")

            if not script:
                continue

            ferramentas_registradas.add(
                Path(script).name
            )

    problemas = []
    sem_main = []
    sintaxe_invalida = []
    imports_suspeitos = []

    for arquivo in scripts:
        texto = arquivo.read_text(encoding="utf-8")

        sintaxe_ok, erro = verificar_sintaxe(arquivo)

        if not sintaxe_ok:
            sintaxe_invalida.append(
                f"{arquivo.name}: {erro}"
            )
            continue

        if (
            arquivo.name in ferramentas_registradas
            and not verificar_main(texto)
        ):
            sem_main.append(arquivo.name)

        for problema in verificar_imports(texto):
            imports_suspeitos.append(
                f"{arquivo.name}: {problema}"
            )

    print(f"Ferramentas analisadas       {len(scripts)}")
    print(f"Sem bloco main               {len(sem_main)}")
    print(f"Sintaxe inválida             {len(sintaxe_invalida)}")
    print(f"Imports suspeitos             {len(imports_suspeitos)}")

    if sem_main:
        print()
        print("ℹ️ FERRAMENTAS SEM MAIN")
        print("=======================")

        for nome in sem_main:
            print(f"- {nome}")

        print()
        print(
            "ℹ️ A ausência de __main__ é apenas informativa "
            "e não reprova a auditoria."
        )

    if sintaxe_invalida:
        print()
        print("❌ SINTAXE INVÁLIDA")
        print("==================")

        for item in sintaxe_invalida:
            print(f"- {item}")

        problemas.extend(
            f"Sintaxe inválida: {item}"
            for item in sintaxe_invalida
        )

    if imports_suspeitos:
        print()
        print("⚠️ IMPORTS SUSPEITOS")
        print("===================")

        for item in imports_suspeitos:
            print(f"- {item}")

        problemas.extend(
            f"Import suspeito: {item}"
            for item in imports_suspeitos
        )

    if problemas:
        print()
        print("⚠️ RESULTADO: AUDITORIA ENCONTROU PONTOS PARA REVISÃO")
        raise SystemExit(1)

    print()
    print("✅ RESULTADO: AUDITORIA DAS FERRAMENTAS APROVADA")


if __name__ == "__main__":
    main()
