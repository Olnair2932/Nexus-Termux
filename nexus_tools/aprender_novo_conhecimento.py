#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import json
from datetime import datetime

ROOT = Path("/data/data/com.termux/files/home/sentinela_dev")
PASTA = ROOT / "conhecimento" / "aprendidos"

PASTA.mkdir(
    parents=True,
    exist_ok=True
)

if len(sys.argv) < 3:
    print("Uso: aprender_novo_conhecimento.py tema resposta")
    sys.exit()

tema = sys.argv[1]
conteudo = sys.argv[2]

arquivo = (
    PASTA /
    (tema.lower().replace(" ","_") + ".md")
)

arquivo.write_text(
f"""# {tema}

Data: {datetime.now().isoformat()}

{conteudo}
""",
encoding="utf-8"
)

print("Conhecimento salvo:")
print(arquivo)

