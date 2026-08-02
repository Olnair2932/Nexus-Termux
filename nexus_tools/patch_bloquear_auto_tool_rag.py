#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

backup = SERVER.with_suffix(".js.bak_bloqueio_rag_tool")

if not SERVER.exists():
    print("server.js não encontrado")
    sys.exit(1)

shutil.copy2(SERVER, backup)
print("Backup criado:", backup)

texto = SERVER.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_SKIP_AUTO_TOOL" in texto:
    print("Patch já aplicado.")
    sys.exit(0)

marcador = """if (
                intent.autoBuild ||"""

if marcador not in texto:
    print("Ponto de inserção não encontrado.")
    sys.exit(1)

patch = r'''
            // RAG_SKIP_AUTO_TOOL

            if (
                intent.acao &&
                (
                    intent.acao.startsWith("explique") ||
                    intent.acao.startsWith("o_que") ||
                    intent.acao.includes("pesquise")
                )
            ) {

                console.log(
                    "RAG respondeu. Ignorando criação automática de ferramenta."
                );

                intent.autoBuild = false;

            }

'''

texto = texto.replace(
    marcador,
    patch + "\n" + marcador,
    1
)

SERVER.write_text(
    texto,
    encoding="utf-8"
)

print("Patch RAG_SKIP_AUTO_TOOL aplicado com sucesso.")
print("Reinicie o servidor.")
