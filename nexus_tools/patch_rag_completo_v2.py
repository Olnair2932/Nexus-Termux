#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

backup = SERVER.with_suffix(".js.bak_rag_completo_v2")
shutil.copy2(SERVER, backup)

print("Backup criado:", backup)

texto = SERVER.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_COMPLETO_NEXUS_V2" in texto:
    print("Patch já aplicado.")
    sys.exit(0)


marcador = '''
    try {
        const { execSync } = require("child_process");

        const memoria = execSync(
'''


if marcador not in texto:
    print("Ponto de inserção não encontrado.")
    sys.exit(1)


patch = r'''
    // RAG_COMPLETO_NEXUS_V2

    try {

        const { execSync } = require("child_process");

        const consulta =
            promptUsuario.toLowerCase();

        if (
            consulta.includes("base de conhecimento") ||
            consulta.includes("documentação") ||
            consulta.includes("documentacao") ||
            consulta.includes("manual") ||
            consulta.includes("readme") ||
            consulta.includes(".md") ||
            consulta.includes(".json") ||
            consulta.includes("pesquise")
        ) {

            const resposta = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 2 * 1024 * 1024
                }
            ).trim();


            if (resposta) {

                return {
                    acao: "conversar",
                    msg: resposta
                };

            }

        }

    } catch(e) {

        console.log(
            "RAG_COMPLETO_NEXUS_V2:",
            e.message
        );

    }


'''

texto = texto.replace(
    marcador,
    patch + marcador,
    1
)

SERVER.write_text(
    texto,
    encoding="utf-8"
)

print("Patch RAG_COMPLETO_NEXUS_V2 aplicado.")
print("Reinicie o servidor.")
