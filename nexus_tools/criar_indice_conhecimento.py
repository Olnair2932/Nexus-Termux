#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json

ROOT = Path("/data/data/com.termux/files/home/sentinela_dev")
PASTA = ROOT / "conhecimento"
INDICE = ROOT / "conhecimento" / "indice.json"

base = []

if PASTA.exists():

    for arquivo in PASTA.rglob("*"):

        if arquivo.suffix.lower() in [".md",".txt",".json"]:

            try:
                texto = arquivo.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                base.append({
                    "arquivo": str(arquivo),
                    "tamanho": len(texto),
                    "nome": arquivo.name
                })

            except:
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

print("Índice criado:", INDICE)
print("Documentos:", len(base))
