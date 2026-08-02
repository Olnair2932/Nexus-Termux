#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/sentinela_dev")
DB = ROOT / "knowledge.json"

if not DB.exists():
    print("Banco de conhecimento não encontrado.")
    sys.exit(1)

try:
    banco = json.loads(
        DB.read_text(encoding="utf-8")
    )
except Exception as e:
    print("Erro lendo banco:", e)
    sys.exit(1)


if len(sys.argv) < 2:
    print("Uso:")
    print("  consolidar_conhecimento.py <tema>")
    sys.exit(1)


tema = " ".join(sys.argv[1:]).lower()

resultados = []

for item in banco.get("knowledge", []):

    texto = (
        item.get("pergunta","") +
        " " +
        item.get("resposta","")
    ).lower()

    palavras = tema.split()

    pontos = sum(
        1 for p in palavras
        if p in texto
    )

    if pontos:
        resultados.append(
            (
                pontos,
                item
            )
        )


resultados.sort(
    key=lambda x: x[0],
    reverse=True
)


if not resultados:

    print("Nenhum conhecimento relacionado encontrado.")
    sys.exit()


print("=== NEXUS CONHECIMENTO CONSOLIDADO ===\n")

vistos = set()

for pontos,item in resultados:

    resposta = item.get("resposta","")

    if resposta not in vistos:

        print("- " + resposta)
        print()

        vistos.add(resposta)

print("=== FIM DA BASE ===")
