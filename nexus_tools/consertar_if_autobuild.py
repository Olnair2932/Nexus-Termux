#!/usr/bin/env python3
from pathlib import Path

ARQ = Path(__file__).resolve().parent.parent / "server.js"

texto = ARQ.read_text(encoding="utf-8")

errado = """if (
                !intent.ragLocal &&
                (
                intent.autoBuild ||
                (
                    !skillsValidacao.skills[chave] &&
                    !intentMap.acoes[chave]
                )
            ) {"""

certo = """if (
                intent.autoBuild ||
                (
                    !skillsValidacao.skills[chave] &&
                    !intentMap.acoes[chave]
                )
            ) {"""

if errado not in texto:
    print("Bloco quebrado não encontrado.")
    exit()

texto = texto.replace(errado, certo, 1)

ARQ.write_text(texto, encoding="utf-8")

print("IF AUTO_BUILD corrigido.")
