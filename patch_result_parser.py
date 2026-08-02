#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re
import sys

ARQ = Path("server.js")

if not ARQ.exists():
    print("server.js não encontrado.")
    sys.exit(1)

backup = ARQ.with_suffix(".js.bak.result_parser")
shutil.copy2(ARQ, backup)

texto = ARQ.read_text(encoding="utf-8")

padrao = r'execResult\s*=\s*resultado\s*;\s*'

novo = r'''execResult = resultado;

                    switch (resultado.executor) {

                        case "termux-battery-status": {
                            const bateria = JSON.parse(resultado.stdout);
                            respostaFinal =
                                `Bateria: ${bateria.percentage}%\n` +
                                `Temperatura: ${bateria.temperature}°C\n` +
                                `Estado: ${bateria.status}`;
                            break;
                        }

                        case "termux-volume": {
                            const volumes = JSON.parse(resultado.stdout);
                            respostaFinal = volumes
                                .map(v => `${v.stream}: ${v.volume}/${v.max_volume}`)
                                .join("\n");
                            break;
                        }

                        case "termux-torch":
                            respostaFinal = "Lanterna acionada com sucesso.";
                            break;

                        default:
                            respostaFinal =
                                resultado.stdout ||
                                resultado.stderr ||
                                resultado.erro ||
                                "Comando executado.";
                    }

                    break;

'''

texto_novo, n = re.subn(padrao, novo, texto, count=1)

if n == 0:
    print("Não foi possível localizar 'execResult = resultado;'.")
    sys.exit(1)

ARQ.write_text(texto_novo, encoding="utf-8")

print("✔ Patch aplicado com sucesso.")
print("✔ Backup criado em:", backup)
