#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/nexus_tools/auto_conhecimento_generativo.py")

BACKUP = ARQ.with_suffix(".py.bak_aprendizado_assistido")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "APRENDIZADO_ASSISTIDO_NEXUS" in texto:
    print("Patch já aplicado.")
    exit()

antigo = 'print("Nenhum conhecimento encontrado.")'

novo = r'''
# -------------------------------------------------------
# APRENDIZADO_ASSISTIDO_NEXUS
# -------------------------------------------------------

print("=== APRENDIZADO_ASSISTIDO_NEXUS ===")
print()
print("Não encontrei conhecimento local sobre:")
print(consulta)
print()
print("Deseja pesquisar e aprender? Responda: sim")
'''

if antigo not in texto:
    print("Ponto não encontrado.")
    exit()

texto = texto.replace(
    antigo,
    novo,
    1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("Patch APRENDIZADO_ASSISTIDO_NEXUS aplicado.")
