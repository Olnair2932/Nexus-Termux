#!/usr/bin/env python3
from pathlib import Path
import shutil

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

shutil.copy2(
    ARQ,
    ARQ.with_suffix(".js.bak_bloqueio_file_creator_rag")
)

texto = ARQ.read_text(
    encoding="utf-8",
    errors="ignore"
)

if "BLOQUEIO_FILE_CREATOR_RAG" in texto:
    print("Patch já aplicado.")
    exit()

marcador = """                console.log(
                    "🛠️ Ferramenta inexistente:",
                    chave
                );"""

patch = r'''
                // BLOQUEIO_FILE_CREATOR_RAG

                if (
                    intent.acao === "conversar" ||
                    intent.ragLocal === true
                ) {

                    console.log(
                        "RAG local: criação automática cancelada."
                    );

                    respostaFinal =
                        intent.msg ||
                        "Resposta encontrada na base local.";

                    break;

                }

'''

if marcador not in texto:
    print("Ponto não encontrado.")
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

print("Patch BLOQUEIO_FILE_CREATOR_RAG aplicado.")
