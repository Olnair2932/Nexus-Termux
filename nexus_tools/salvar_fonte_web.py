#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path("/data/data/com.termux/files/home/sentinela_dev")

PASTA = ROOT / "conhecimento" / "aprendidos"

PASTA.mkdir(
    parents=True,
    exist_ok=True
)

if len(sys.argv) < 3:
    print("Uso: tema conteúdo")
    sys.exit()

tema = sys.argv[1].lower().replace(" ","_")

conteudo = " ".join(sys.argv[2:])

arquivo = PASTA / f"{tema}.md"

arquivo.write_text(
f"""# {tema}

Data:
{datetime.now().isoformat()}

Fonte aprendida:

{conteudo}
""",
encoding="utf-8"
)

print("=== CONHECIMENTO WEB SALVO ===")
print(arquivo)

