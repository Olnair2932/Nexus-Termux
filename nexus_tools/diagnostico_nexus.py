#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills.json"
TOOLS = ROOT / "nexus_tools"


def verificar_skills():
    if not SKILLS.exists():
        return False, "skills.json não encontrado"

    try:
        with SKILLS.open(encoding="utf-8") as f:
            dados = json.load(f)

        skills = dados.get("skills", {})

        if not isinstance(skills, dict):
            return False, "estrutura skills inválida"

        return True, f"{len(skills)} skills registradas"

    except json.JSONDecodeError as erro:
        return False, f"JSON inválido: {erro}"

    except Exception as erro:
        return False, str(erro)


def verificar_ferramentas():
    if not TOOLS.exists():
        return False, "nexus_tools não encontrado"

    arquivos = list(TOOLS.glob("*.py"))

    return True, f"{len(arquivos)} scripts Python encontrados"


def verificar_scripts_registrados():
    if not SKILLS.exists():
        return False, "skills.json não encontrado"

    with SKILLS.open(encoding="utf-8") as f:
        dados = json.load(f)

    skills = dados.get("skills", {})
    ausentes = []

    for nome, configuracao in skills.items():
        if not isinstance(configuracao, dict):
            continue

        script = configuracao.get("script")

        if not script:
            continue

        caminho = ROOT / script

        if not caminho.exists():
            ausentes.append(f"{nome} -> {script}")

    if ausentes:
        return False, f"{len(ausentes)} scripts registrados não encontrados"

    return True, "todos os scripts registrados existem"


def verificar_python():
    if not TOOLS.exists():
        return False, "nexus_tools não encontrado"

    arquivos = list(TOOLS.glob("*.py"))
    erros = []

    for arquivo in arquivos:
        resultado = subprocess.run(
            [sys.executable, "-m", "py_compile", str(arquivo)],
            capture_output=True,
            text=True,
        )

        if resultado.returncode != 0:
            erros.append(arquivo.name)

    if erros:
        return False, f"{len(erros)} scripts com erro de sintaxe"

    return True, f"{len(arquivos)} scripts passaram no py_compile"


def verificar_json():
    arquivos = [
        ROOT / "skills.json",
        ROOT / "brain.json",
    ]

    erros = []

    for arquivo in arquivos:
        if not arquivo.exists():
            continue

        try:
            with arquivo.open(encoding="utf-8") as f:
                json.load(f)
        except Exception:
            erros.append(arquivo.name)

    if erros:
        return False, "JSON inválido: " + ", ".join(erros)

    return True, "JSONs principais válidos"


def main():
    verificacoes = [
        ("Skills", verificar_skills),
        ("Ferramentas Python", verificar_ferramentas),
        ("Scripts registrados", verificar_scripts_registrados),
        ("Python", verificar_python),
        ("JSON", verificar_json),
    ]

    print("🔎 DIAGNÓSTICO NEXUS")
    print("====================")
    print()

    falhas = 0

    for nome, funcao in verificacoes:
        try:
            ok, mensagem = funcao()
        except Exception as erro:
            ok = False
            mensagem = str(erro)

        status = "OK" if ok else "ERRO"

        if not ok:
            falhas += 1

        print(f"{nome:<24} {status}")
        print(f"  {mensagem}")

    print()

    if falhas:
        print(f"⚠️ RESULTADO: {falhas} verificação(ões) com problema.")
        raise SystemExit(1)

    print("✅ RESULTADO: SISTEMA SAUDÁVEL")


if __name__ == "__main__":
    main()
