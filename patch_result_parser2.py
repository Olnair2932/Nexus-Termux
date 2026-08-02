#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re

arq = Path("server.js")
backup = arq.with_suffix(".js.bak.result_parser2")
shutil.copy2(arq, backup)

txt = arq.read_text(encoding="utf-8")

padrao = re.compile(
    r"respostaFinal\s*=\s*resultado\.stdout\s*\|\|\s*resultado\.stderr\s*\|\|\s*resultado\.erro\s*\|\|\s*\"Comando executado\.\";",
    re.MULTILINE
)

novo = r'''
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
            .join("\\n");
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
'''

txt, n = padrao.subn(novo, txt, count=1)

if n == 0:
    print("Trecho não encontrado.")
else:
    arq.write_text(txt, encoding="utf-8")
    print("✔ Patch aplicado.")
    print("✔ Backup:", backup)
