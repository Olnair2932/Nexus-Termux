#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

if not SERVER.exists():
    print("ERRO: server.js não encontrado.")
    sys.exit(1)

backup = SERVER.with_suffix(".js.bak_consulta_rag_v2")
shutil.copy2(SERVER, backup)
print("Backup criado:", backup)

texto = SERVER.read_text(encoding="utf-8", errors="ignore")

if "CONSULTA_RAG_LOCAL" in texto:
    print("Patch já aplicado.")
    sys.exit(0)

marcador = '''    try {
        const { execSync } = require("child_process");

        const memoria = execSync(
'''

if marcador not in texto:
    print("Não encontrei o ponto de inserção.")
    sys.exit(1)

patch = r'''
    // CONSULTA_RAG_LOCAL

    try {

        const pergunta = promptUsuario.toLowerCase();

        if (
            pergunta.startsWith("explique") ||
            pergunta.startsWith("o que é") ||
            pergunta.startsWith("o que voce") ||
            pergunta.startsWith("o que você") ||
            pergunta.startsWith("pesquise") ||
            pergunta.startsWith("manual") ||
            pergunta.startsWith("documentação") ||
            pergunta.startsWith("documentacao") ||
            pergunta.includes("readme") ||
            pergunta.includes(".md") ||
            pergunta.includes(".json")
        ) {

            const { execSync } = require("child_process");

            const respostaLocal = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

            if (
                respostaLocal &&
                !respostaLocal.includes("Nenhum conhecimento")
            ) {

                return {
                    acao: "conversar",
                    msg: respostaLocal
                };

            }

        }

    } catch(e) {

        console.log("CONSULTA_RAG_LOCAL:", e.message);

    }

'''

texto = texto.replace(marcador, patch + marcador, 1)

SERVER.write_text(texto, encoding="utf-8")

print("Patch CONSULTA_RAG_LOCAL aplicado com sucesso.")
print("Reinicie o servidor.")
