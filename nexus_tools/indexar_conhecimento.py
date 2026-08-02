#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
PASTA = ROOT / "conhecimento"
INDICE = ROOT / "conhecimento_index.json"

base = []

for arquivo in PASTA.rglob("*"):

    if arquivo.suffix.lower() not in [".md", ".txt", ".json"]:
        continue

    try:
        texto = arquivo.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        base.append({
            "arquivo": str(arquivo),
            "conteudo": texto,
            "data": datetime.now().isoformat()
        })

    except Exception:
        pass


INDICE.write_text(
    json.dumps(
        {
            "documentos": base,
            "total": len(base)
        },
        indent=4,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("=== ÍNDICE DE CONHECIMENTO NEXUS ===")
print("Documentos:", len(base))
print("Arquivo criado:", INDICE)
