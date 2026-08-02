#!/usr/bin/env python3

from pathlib import Path
import sys

arquivo = Path("server.js")

texto = arquivo.read_text(encoding="utf-8")

marcador = '''if (intent.acao === "executar_comando") {'''

if marcador not in texto:
    print("Bloco não encontrado.")
    sys.exit(1)

bloco = '''
            if (intent.acao === "executar_comando") {

                if (
                    intent.params &&
                    intent.params.trim().startsWith("cd ")
                ) {

                    const destino = intent.params
                        .trim()
                        .substring(3)
                        .trim();

                    execSync(
                        `python3 nexus_tools/cwd_manager.py set "${destino}"`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8"
                        }
                    );

                    respostaFinal =
                        "Diretório alterado para: " + destino;

                    break;

                }
'''

texto = texto.replace(
    marcador,
    bloco,
    1
)

arquivo.write_text(
    texto,
    encoding="utf-8"
)

print("Patch CD aplicado.")
