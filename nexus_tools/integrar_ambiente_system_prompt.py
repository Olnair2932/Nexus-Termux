#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re

ARQUIVO = Path("server.js")

if not ARQUIVO.exists():
    print("server.js não encontrado.")
    raise SystemExit(1)

backup = ARQUIVO.with_suffix(".js.bak_system_prompt")
shutil.copy2(ARQUIVO, backup)
print(f"Backup criado: {backup}")

texto = ARQUIVO.read_text(encoding="utf-8")

if "AMBIENTE DETECTADO" in texto:
    print("Bloco já integrado.")
    raise SystemExit(0)

padrao = r'const systemPrompt = `Você é o NEXUS SRE, um sistema operacional inteligente para Termux/Linux\.'

novo = """const systemPrompt = `Você é o NEXUS SRE, um sistema operacional inteligente.

AMBIENTE DETECTADO
- Tipo: ${AMBIENTE.ambiente}
- Sistema: ${AMBIENTE.sistema || process.platform}
- Root: ${AMBIENTE.root}

REGRAS
- Se o ambiente for "render", nunca utilize comandos exclusivos do Termux (termux-info, termux-battery-status, termux-tts-speak).
- Se o ambiente for "termux", utilize normalmente os comandos do Termux.
"""

texto2, n = re.subn(padrao, novo, texto, count=1)

if n == 0:
    print("Não foi encontrado o início do systemPrompt.")
    raise SystemExit(1)

ARQUIVO.write_text(texto2, encoding="utf-8")

print("Integração concluída com sucesso.")
