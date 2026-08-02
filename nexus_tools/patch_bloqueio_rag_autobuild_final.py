#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

BACKUP = ARQ.with_suffix(".js.bak_rag_autobuild_final")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_LOCAL_BLOQUEIA_AUTOBUILD" in texto:
    print("Patch já aplicado.")
    sys.exit()

antigo = """if (
                intent.autoBuild ||
                ("""

novo = """// RAG_LOCAL_BLOQUEIA_AUTOBUILD

            if (
                !intent.ragLocal &&
                (
                intent.autoBuild ||
                ("""

if antigo not in texto:
    print("Ponto não encontrado.")
    sys.exit()

texto = texto.replace(
    antigo,
    novo,
    1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("Patch RAG_LOCAL_BLOQUEIA_AUTOBUILD aplicado.")
print("Reinicie o servidor.")
