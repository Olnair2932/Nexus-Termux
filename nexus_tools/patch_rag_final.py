#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

BACKUP = ARQ.with_suffix(".js.bak_rag_final")

shutil.copy2(ARQ, BACKUP)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_FINAL_STOP_AUTO_BUILD" in texto:
    print("Patch já aplicado.")
    sys.exit()

marcador = "    const systemPrompt = `Você é o NEXUS SRE"

if marcador not in texto:
    print("Ponto de inserção não encontrado.")
    sys.exit()

patch = r'''
    // RAG_FINAL_STOP_AUTO_BUILD

    if (
        contextoLocal &&
        contextoLocal.length > 50 &&
        (
            contextoLocal.includes("DOCUMENTAÇÃO NEXUS") ||
            contextoLocal.includes("CONHECIMENTO APRENDIDO")
        )
    ) {

        return {
            acao: "conversar",
            msg: contextoLocal
        };

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

print("Patch RAG_FINAL_STOP_AUTO_BUILD aplicado.")
print("Reinicie o servidor.")
