#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

if not SERVER.exists():
    print("server.js não encontrado")
    sys.exit(1)

backup = SERVER.with_suffix(".js.bak_consolidado_rag")
shutil.copy2(SERVER, backup)

print("Backup criado:", backup)

texto = SERVER.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_CONSOLIDADO_DASHBOARD" in texto:
    print("Patch já aplicado.")
    sys.exit(0)


marcador = "// RAG_COMPLETO_NEXUS_V2"

if marcador not in texto:
    print("Ponto de inserção não encontrado.")
    sys.exit(1)


patch = r'''

    // RAG_CONSOLIDADO_DASHBOARD

    try {

        const { execSync } = require("child_process");

        const consultaConsolidada = execSync(
            `python3 nexus_tools/consolidar_conhecimento.py "${promptUsuario.replace(/"/g,'\\"')}"`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024
            }
        ).trim();


        if (
            consultaConsolidada &&
            !consultaConsolidada.includes("Nenhum conhecimento")
        ) {

            return {
                acao: "conversar",
                msg: consultaConsolidada
            };

        }


    } catch(e) {

        console.log(
            "RAG_CONSOLIDADO_DASHBOARD:",
            e.message
        );

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

print("Patch RAG consolidado aplicado com sucesso.")
print("Reinicie o servidor.")
