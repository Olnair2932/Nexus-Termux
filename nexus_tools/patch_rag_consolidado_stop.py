#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

BACKUP = ARQ.with_suffix(".js.bak_rag_consolidado_stop")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_CONSOLIDADO_STOP_AUTOBUILD" in texto:
    print("Patch já aplicado.")
    sys.exit()

antigo = '''return {
                acao: "conversar",
                msg: consultaConsolidada
            };'''

novo = '''// RAG_CONSOLIDADO_STOP_AUTOBUILD

            return {
                acao: "conversar",
                msg: consultaConsolidada,
                ragLocal: true
            };'''

if antigo not in texto:
    print("Trecho não encontrado.")
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

print("Patch RAG_CONSOLIDADO_STOP_AUTOBUILD aplicado.")
