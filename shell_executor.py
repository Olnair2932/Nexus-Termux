#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import shlex
import json
import sys


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


def resposta(ok, **dados):
    r = {"ok": ok}
    r.update(dados)
    return r

def executar(comando):

    comando = comando.strip()

    if not comando:
        return resposta(False, erro="Nenhum comando informado.")

    try:
        partes = shlex.split(comando)
    except Exception as e:
        return resposta(False, erro=str(e))

    executavel = partes[0]

    if executavel not in COMANDOS_PERMITIDOS:
        return resposta(False, erro=f"Comando bloqueado: {executavel}")

    if executavel == "cd":
        return resposta(
            True,
            executor="cd",
            stdout="Diretório alterado apenas para esta execução."
        )

    try:

        resultado = subprocess.run(
            partes,
            capture_output=True,
            text=True,
            timeout=30
        )

        return resposta(
            resultado.returncode == 0,
            executor=executavel,
            codigo=resultado.returncode,
            stdout=resultado.stdout.strip(),
            stderr=resultado.stderr.strip()
        )

    except subprocess.TimeoutExpired:
        return resposta(False, erro="Tempo limite excedido.")

    except Exception as e:
        return resposta(False, erro=str(e))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(json.dumps(
            resposta(False, erro="Uso: python3 shell_executor.py '<comando>'"),
            ensure_ascii=False
        ))
        sys.exit(1)

    comando = " ".join(sys.argv[1:])

    print(json.dumps(
        executar(comando),
        ensure_ascii=False
    ))
