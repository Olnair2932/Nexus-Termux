#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re
import sys

ARQ = Path("shell_executor.py")

if not ARQ.exists():
    print("shell_executor.py não encontrado.")
    sys.exit(1)

backup = ARQ.with_suffix(".py.bak")
shutil.copy2(ARQ, backup)

texto = ARQ.read_text(encoding="utf-8")

novo = r'''
EXECUTORES = {

    # Shell
    "bash","sh",

    # Navegação
    "ls","pwd","cd","tree","find","locate",

    # Arquivos
    "cat","less","more","head","tail","grep","sed","awk",
    "sort","uniq","cut","wc","touch","cp","mv","mkdir","rmdir",

    # Sistema
    "date","whoami","id","hostname","uname","env",
    "printenv","which","whereis",

    # Recursos
    "df","du","free","ps","top","uptime",

    # Rede
    "curl","wget","ping","nslookup",

    # Git
    "git",

    # Node
    "node","npm","npx",

    # Python
    "python","python3","pip","pip3",

    # Pacotes
    "pkg","apt",

    # Compactação
    "zip","unzip","tar","gzip",

    # Multimídia
    "ffmpeg","ffprobe","yt-dlp",

    # JSON
    "jq",

    # SQLite
    "sqlite3",

    # Termux
    "termux-info",
    "termux-battery-status",
    "termux-camera-photo",
    "termux-clipboard-get",
    "termux-clipboard-set",
    "termux-download",
    "termux-location",
    "termux-media-player",
    "termux-microphone-record",
    "termux-notification",
    "termux-open",
    "termux-open-url",
    "termux-share",
    "termux-storage-get",
    "termux-telephony-deviceinfo",
    "termux-toast",
    "termux-tts-speak",
    "termux-vibrate",
    "termux-volume"
}
'''

padrao = re.compile(
    r'EXECUTORES\s*=\s*\{.*?\}',
    re.DOTALL
)

if not padrao.search(texto):
    print("Bloco EXECUTORES não encontrado.")
    sys.exit(1)

texto = padrao.sub(novo, texto, count=1)

ARQ.write_text(texto, encoding="utf-8")

print("✔ EXECUTORES atualizado.")
print(f"✔ Backup salvo em: {backup}")
