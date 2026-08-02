#!/usr/bin/env python3

from pathlib import Path
import sys

arquivo = Path("server.js")

texto = arquivo.read_text(encoding="utf-8")

marcador = 'exec(cmd, { cwd: CONFIG.ROOT, timeout: 120000 },'

if marcador not in texto:
    print("Marcador não encontrado.")
    sys.exit(1)

novo = '''const cwdAtual = execSync(
            "python3 nexus_tools/cwd_manager.py get",
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8"
            }
        ).trim();

        exec(cmd, { cwd: cwdAtual, timeout: 120000 },'''

texto = texto.replace(
    marcador,
    novo,
    1
)

arquivo.write_text(
    texto,
    encoding="utf-8"
)

print("Patch 1 aplicado.")
