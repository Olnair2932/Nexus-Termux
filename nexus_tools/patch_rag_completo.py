#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

if not SERVER.exists():
    print("ERRO: server.js não encontrado")
    sys.exit(1)

backup = SERVER.with_suffix(".js.bak_rag_completo")
shutil.copy2(SERVER, backup)

print("Backup criado:", backup)

texto = SERVER.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "RAG_COMPLETO_NEXUS" in texto:
    print("Patch já aplicado.")
    sys.exit(0)


marcador = """
    // � Consulta memória aprendida antes do Gemini
"""

if marcador not in texto:
    marcador = """
    // Consulta memória aprendida antes do Gemini
"""

if marcador not in texto:
    print("Ponto de inserção não encontrado.")
    sys.exit(1)


patch = r'''
    // RAG_COMPLETO_NEXUS

    try {

        const { execSync } = require("child_process");

        const perguntaRag = promptUsuario.toLowerCase();

        const palavrasRag = [
            "explique",
            "o que é",
            "o que e",
            "pesquise",
            "manual",
            "documentação",
            "documentacao",
            "README",
            ".md",
            ".json",
            "base de conhecimento",
            "arquivo",
            "documento"
        ];

        const usarRag =
            palavrasRag.some(p =>
                perguntaRag.includes(p.toLowerCase())
            );


        if (usarRag) {

            const resultadoRag = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 2 * 1024 * 1024
                }
            ).trim();


            if (
                resultadoRag &&
                !resultadoRag.includes("Nenhum conhecimento")
            ) {

                console.log(
                    "RAG LOCAL RESPONDEU"
                );


                return {
                    acao: "conversar",
                    msg: resultadoRag
                };

            }

        }


    } catch(e) {

        console.log(
            "RAG_COMPLETO_NEXUS:",
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

print("RAG_COMPLETO_NEXUS aplicado com sucesso.")
print("Reinicie o servidor.")
