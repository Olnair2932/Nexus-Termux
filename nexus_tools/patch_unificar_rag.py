#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/nexus_tools/auto_conhecimento_generativo.py")

BACKUP = ARQ.with_suffix(".py.bak_unificar")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_UNIFICADO_NEXUS" in texto:
    print("Patch já aplicado.")
    sys.exit()

marcador = 'print("=== CONHECIMENTO APRENDIDO ===\\n")'

if marcador not in texto:
    print("Ponto não encontrado.")
    sys.exit()

texto = texto.replace(
    marcador,
'''# -------------------------------------------------------
# RAG_UNIFICADO_NEXUS
# -------------------------------------------------------

print("=== NEXUS CONHECIMENTO ===")
print()

''',
1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("Patch RAG_UNIFICADO_NEXUS aplicado.")
