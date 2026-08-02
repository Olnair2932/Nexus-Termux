#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil

arq = Path("server.js")

backup = arq.with_suffix(".js.bak.fix_result_parser")
shutil.copy2(arq, backup)

txt = arq.read_text(encoding="utf-8")

txt = txt.replace(
"""` +
                                `Temperatura: ${bateria.temperature}°C
` +""",
"""\\n` +
                                `Temperatura: ${bateria.temperature}°C\\n` +"""
)

txt = txt.replace(
"""                                .join("
");""",
"""                                .join("\\n");"""
)

arq.write_text(txt, encoding="utf-8")

print("✔ Correção aplicada.")
print("✔ Backup:", backup)
