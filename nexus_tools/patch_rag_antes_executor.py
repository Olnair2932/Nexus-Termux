#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

BACKUP = ARQ.with_suffix(".js.bak_rag_antes_executor")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_FORCA_CONVERSA_FINAL" in texto:
    print("Patch já aplicado.")
    sys.exit()

marcador = """    console.log("========== DEBUG ==========");"""

if marcador not in texto:
    print("Ponto não encontrado.")
    sys.exit()

patch = r'''
    // RAG_FORCA_CONVERSA_FINAL

    if (
        intent &&
        intent.msg &&
        (
            intent.msg.includes("NEXUS CONHECIMENTO CONSOLIDADO") ||
            intent.msg.includes("CONHECIMENTO APRENDIDO") ||
            intent.msg.includes("DOCUMENTAÇÃO NEXUS")
        )
    ) {

        console.log(
            "RAG local encontrado. Bloqueando AutoBuild."
        );

        intent.acao = "conversar";
        intent.autoBuild = false;

    }

'''

texto = texto.replace(
    marcador,
    patch + marcador,
    1
)

ARQ.write_text(
    texto,
    encoding="utf-8"
)

print("Patch RAG_FORCA_CONVERSA_FINAL aplicado.")
print("Teste: node --check server.js")
