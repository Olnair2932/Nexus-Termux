#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re
import shutil

arq = Path("shell_executor.py")

backup = arq.with_suffix(".py.bak")
shutil.copy2(arq, backup)

texto = arq.read_text(encoding="utf-8")

novo = '''
COMANDOS_PERMITIDOS = {

    # Linux
    "ls","pwd","cd","find","tree","locate",
    "cat","head","tail","less","more",
    "grep","sed","awk","cut","sort","uniq","wc",
    "touch","mkdir","rmdir","cp","mv",

    # Sistema
    "date","whoami","id","hostname","uname",
    "env","printenv","which","whereis",
    "df","du","free","ps","top","uptime",

    # Rede
    "curl","wget","ping","nslookup",

    # Desenvolvimento
    "node","npm","npx",
    "python","python3","pip","pip3",
    "git",

    # Pacotes
    "pkg","apt",

    # Compressão
    "zip","unzip","tar","gzip",

    # Multimídia
    "ffmpeg","ffprobe","yt-dlp",

    # JSON
    "jq",

    # SQLite
    "sqlite3",

    # Termux API
    "termux-open",
    "termux-open-url",
    "termux-backup",
    "termux-info",
    "termux-wake-lock",
    "termux-wake-unlock",
    "termux-brightness",
    "termux-call-log",
    "termux-camera-info",
    "termux-camera-photo",
    "termux-clipboard-get",
    "termux-clipboard-set",
    "termux-contact-list",
    "termux-dialog",
    "termux-download",
    "termux-fingerprint",
    "termux-location",
    "termux-media-player",
    "termux-media-scan",
    "termux-microphone-record",
    "termux-notification",
    "termux-notification-list",
    "termux-notification-remove",
    "termux-saf-create",
    "termux-saf-dirs",
    "termux-saf-ls",
    "termux-saf-managedir",
    "termux-saf-mkdir",
    "termux-saf-read",
    "termux-saf-rm",
    "termux-saf-stat",
    "termux-saf-write",
    "termux-sensor",
    "termux-share",
    "termux-sms-inbox",
    "termux-sms-list",
    "termux-sms-send",
    "termux-speech-to-text",
    "termux-storage-get",
    "termux-telephony-call",
    "termux-telephony-cellinfo",
    "termux-telephony-deviceinfo",
    "termux-toast",
    "termux-torch",
    "termux-tts-engines",
    "termux-tts-speak",
    "termux-usb",
    "termux-vibrate",
    "termux-volume",
    "termux-wallpaper",
    "termux-wifi-connectioninfo",
    "termux-wifi-enable",
    "termux-wifi-scaninfo",
    "termux-api-start",
    "termux-api-stop",
    "termux-audio-info",
    "termux-battery-status",
    "termux-job-scheduler"
}
'''

texto = re.sub(
    r'COMANDOS_PERMITIDOS\s*=\s*\{.*?\}',
    novo,
    texto,
    flags=re.S
)

arq.write_text(texto, encoding="utf-8")

print("✔ shell_executor.py atualizado.")
print("✔ Backup:", backup)
