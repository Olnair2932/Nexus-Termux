#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from pathlib import Path

ARQ = Path("/data/data/com.termux/files/home/sentinela_dev/cwd_state.json")
ROOT = "/data/data/com.termux/files/home/sentinela_dev"

def carregar():
    if ARQ.exists():
        try:
            return json.loads(ARQ.read_text())["cwd"]
        except Exception:
            pass
    return ROOT

def salvar(cwd):
    ARQ.write_text(json.dumps({"cwd": cwd}, indent=2))

if len(sys.argv) == 1:
    print(carregar())
    sys.exit(0)

acao = sys.argv[1]

if acao == "get":
    print(carregar())

elif acao == "set":
    if len(sys.argv) < 3:
        print("Uso: cwd_manager.py set <diretorio>")
        sys.exit(1)

    destino = os.path.abspath(os.path.expanduser(sys.argv[2]))

    if not os.path.isdir(destino):
        print("ERRO")
        sys.exit(1)

    salvar(destino)
    print(destino)

elif acao == "reset":
    salvar(ROOT)
    print(ROOT)

else:
    print("Ação inválida")
    sys.exit(1)
