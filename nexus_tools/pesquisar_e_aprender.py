#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

ROOT = Path("/data/data/com.termux/files/home/sentinela_dev")

load_dotenv("/data/data/com.termux/files/home/sentinela_dev_backup/.env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("GEMINI_API_KEY não encontrada.")
    exit()

import sys

if len(sys.argv) < 2:
    print("Uso: pesquisar_e_aprender.py <tema>")
    exit()

tema = " ".join(sys.argv[1:])

prompt = f"""
Explique detalhadamente:

{tema}

Responda em Markdown contendo:

- definição
- funcionamento
- aplicações
- vantagens
- limitações
- referências oficiais quando possível

Não utilize emojis.
"""

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ]
}

cmd = [
    "curl",
    "-s",
    "-X",
    "POST",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}",
    "-H",
    "Content-Type: application/json",
    "-d",
    json.dumps(payload)
]

resultado = subprocess.check_output(cmd, text=True)

dados = json.loads(resultado)







texto = dados["candidates"][0]["content"]["parts"][0]["text"]

PASTA = ROOT / "conhecimento" / "aprendidos"
PASTA.mkdir(parents=True, exist_ok=True)

arquivo = PASTA / (tema.lower().replace(" ","_") + ".md")


# -------------------------------------------------------
# BACKUP_CONHECIMENTO_EXISTENTE
# -------------------------------------------------------

if arquivo.exists():

    backup = arquivo.with_suffix(".md.bak")

    shutil.copy2(
        arquivo,
        backup
    )

    print("Backup do conhecimento:", backup)


arquivo.write_text(
f"""# {tema}

Data:
{datetime.now().isoformat()}

{texto}
""",
encoding="utf-8"
)

subprocess.run([
    "python3",
    str(ROOT / "nexus_tools" / "criar_indice_conhecimento.py")
])

print()
print("=== CONHECIMENTO APRENDIDO ===")
print()
print("Arquivo:", arquivo)
print()

print("Índice atualizado.")

# -------------------------------------------------------
# REGISTRO_HISTORICO_APRENDIZADO
# -------------------------------------------------------

from pathlib import Path
import json
from datetime import datetime

try:

    hist = ROOT / "conhecimento" / "historico.json"

    if hist.exists():
        dados = json.loads(
            hist.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        )

        if not isinstance(dados, list):
            dados = []
    else:
        dados = []

    dados.append({
        "data": datetime.now().isoformat(),
        "evento": "Conhecimento aprendido",
        "tema": tema,
        "arquivo": str(arquivo),
        "origem": "Gemini 3.1 Flash Lite"
    })

    hist.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("Histórico atualizado.")

except Exception as e:
    print("Falha ao atualizar histórico:", e)

