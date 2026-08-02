#!/usr/bin/env python3
from pathlib import Path
import shutil

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/nexus_tools/auto_conhecimento_generativo.py")

shutil.copy2(
    ARQ,
    ARQ.with_suffix(".py.bak_normalizar_consulta_rag")
)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "NORMALIZAR_CONSULTA_RAG" in texto:
    print("Patch já aplicado.")
    exit()

marcador = "# BUSCA_CONHECIMENTO_MANUAIS"

patch = r'''
# -------------------------------------------------------
# NORMALIZAR_CONSULTA_RAG
# -------------------------------------------------------

remover = [
    "o que é ",
    "o que e ",
    "explique ",
    "explique o ",
    "pesquise ",
    "sobre "
]

for palavra in remover:
    consulta = consulta.replace(palavra, "")

consulta = consulta.strip()

'''

if marcador not in texto:
    print("Marcador não encontrado")
    exit()

texto = texto.replace(
    marcador,
    patch + marcador,
    1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("NORMALIZAR_CONSULTA_RAG aplicado.")
