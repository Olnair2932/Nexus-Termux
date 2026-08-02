#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

BACKUP = ARQ.with_suffix(".js.bak_rag_autobuild_seguro")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_AUTO_BUILD_SEGURO" in texto:
    print("Patch já aplicado.")
    sys.exit()

marcador = """            if (
                intent.autoBuild ||
"""

if marcador not in texto:
    print("Ponto de inserção não encontrado.")
    sys.exit()

patch = """
            // RAG_AUTO_BUILD_SEGURO

            if (intent.ragLocal) {
                intent.autoBuild = false;
            }

"""

texto = texto.replace(
    marcador,
    patch + marcador,
    1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("Patch RAG_AUTO_BUILD_SEGURO aplicado.")
print("Teste com: node --check server.js")
