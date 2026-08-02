#!/usr/bin/env python3
from pathlib import Path
import shutil

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

shutil.copy2(
    ARQ,
    ARQ.with_suffix(".js.bak_rag_intent_final")
)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_INTENT_FINAL_FIX" in texto:
    print("Patch já aplicado.")
    exit()

marcador = """    console.log("========== DEBUG ==========");"""

patch = r'''
    // RAG_INTENT_FINAL_FIX

    if (
        intent &&
        intent.ragLocal === true
    ) {

        console.log(
            "RAG local detectado. Forçando conversa."
        );

        intent.acao = "conversar";
        intent.autoBuild = false;

    }

'''

if marcador not in texto:
    print("Marcador não encontrado.")
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

print("Patch RAG_INTENT_FINAL_FIX aplicado.")
