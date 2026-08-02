#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/nexus_tools/auto_conhecimento_generativo.py")

BACKUP = ARQ.with_suffix(".py.bak_conhecimento")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "BUSCA_CONHECIMENTO_MANUAIS" in texto:
    print("Patch já aplicado.")
    exit()

marcador = """
resultado=[]
"""

patch = r'''

# -------------------------------------------------------
# BUSCA_CONHECIMENTO_MANUAIS
# -------------------------------------------------------

pasta_conhecimento = ROOT / "conhecimento"

if pasta_conhecimento.exists():

    for arquivo in pasta_conhecimento.rglob("*"):

        if arquivo.suffix.lower() not in [".md",".txt",".json"]:
            continue

        try:

            conteudo = arquivo.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            score = conteudo.lower().count(consulta)

            if score:

                print("=== DOCUMENTAÇÃO NEXUS ===\n")
                print(f"Arquivo: {arquivo}\n")
                print(conteudo[:4000])
                sys.exit()

        except:
            pass

'''

if marcador not in texto:
    print("Ponto não encontrado")
    exit()

texto = texto.replace(
    marcador,
    patch + "\n" + marcador,
    1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("Patch BUSCA_CONHECIMENTO_MANUAIS aplicado.")
