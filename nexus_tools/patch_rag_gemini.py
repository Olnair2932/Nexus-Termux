#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

if not SERVER.exists():
    print("ERRO: server.js não encontrado.")
    sys.exit(1)

backup = SERVER.with_suffix(".js.bak_rag")
shutil.copy2(SERVER, backup)
print("Backup criado:", backup)

texto = SERVER.read_text(encoding="utf-8", errors="ignore")

if "BASE_CONHECIMENTO_LOCAL_RAG" in texto:
    print("Patch já aplicado.")
    sys.exit(0)

marcador = "const systemPrompt = `Você é o NEXUS SRE"

if marcador not in texto:
    print("Não encontrei o systemPrompt.")
    sys.exit(1)

bloco_python = '''
    // BASE_CONHECIMENTO_LOCAL_RAG

    let contextoLocal = "";

    try {

        contextoLocal = execSync(
            `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\\\"')}"`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024
            }
        ).trim();

    } catch(e) {

        console.log("AUTO_CONHECIMENTO:", e.message);

    }

'''

texto = texto.replace(
    "const systemPrompt = `Você é o NEXUS SRE",
    bloco_python + "    const systemPrompt = `Você é o NEXUS SRE",
    1
)

texto = texto.replace(
    "Você é o NEXUS SRE, um sistema operacional inteligente para Termux/Linux.\n",
    """Você é o NEXUS SRE, um sistema operacional inteligente para Termux/Linux.

BASE DE CONHECIMENTO LOCAL

${contextoLocal}

Utilize primeiro o conhecimento local acima.
Se ele não responder completamente à pergunta,
complemente utilizando seu conhecimento geral.

""",
    1
)

SERVER.write_text(texto, encoding="utf-8")

print("Patch RAG aplicado com sucesso.")
print("Reinicie o servidor.")
