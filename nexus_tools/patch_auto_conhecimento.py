#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

server = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

if not server.exists():
    print("server.js não encontrado.")
    sys.exit(1)

backup = server.with_suffix(".js.bak_auto_conhecimento")
shutil.copy2(server, backup)
print("Backup:", backup)

texto = server.read_text(encoding="utf-8", errors="ignore")

if "AUTO_CONHECIMENTO_GENERATIVO" in texto:
    print("Patch já aplicado.")
    sys.exit(0)

assinatura = "async function processarIntencao(promptUsuario) {"

if assinatura not in texto:
    print("Função processarIntencao não encontrada.")
    sys.exit(1)

patch = '''
async function processarIntencao(promptUsuario) {

    // AUTO_CONHECIMENTO_GENERATIVO

    try {

        const { execSync } = require("child_process");

        if (promptUsuario.toLowerCase().startsWith("aprender ")) {

            const consulta = promptUsuario.substring(9).trim();

            const contexto = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${consulta.replace(/"/g,'\\\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

            return {
                acao: "conversar",
                msg: contexto
            };

        }

    } catch(e) {
        console.log("AUTO_CONHECIMENTO:", e.message);
    }
'''

texto = texto.replace(assinatura, patch, 1)

server.write_text(texto, encoding="utf-8")

print("Patch aplicado com sucesso.")
