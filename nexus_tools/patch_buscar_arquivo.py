#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

SERVER = Path("/data/data/com.termux/files/home/sentinela_dev/server.js")

if not SERVER.exists():
    print("ERRO: server.js não encontrado.")
    sys.exit(1)

backup = SERVER.with_suffix(".js.bak_buscar_arquivo")
shutil.copy2(SERVER, backup)
print("Backup criado:", backup)

texto = SERVER.read_text(encoding="utf-8", errors="ignore")

if 'case "buscar_arquivo":' in texto:
    print("Patch já aplicado.")
    sys.exit(0)

marcador = '''
    case "status_sistema":
        respostaFinal = intent.msg || "Sistema operacional pronto.";
        break;

    default:
'''

if marcador not in texto:
    print("Não encontrei o ponto de inserção.")
    sys.exit(1)

novo = '''
    case "status_sistema":
        respostaFinal = intent.msg || "Sistema operacional pronto.";
        break;

    case "buscar_arquivo":

        try {

            const { execSync } = require("child_process");

            respostaFinal = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${intent.params || promptUsuario}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

        } catch(e) {

            respostaFinal =
                "Erro ao consultar a base de conhecimento: " +
                e.message;

        }

        break;

    default:
'''

texto = texto.replace(marcador, novo, 1)

SERVER.write_text(texto, encoding="utf-8")

print("Patch buscar_arquivo aplicado com sucesso.")
