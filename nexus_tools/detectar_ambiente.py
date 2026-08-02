#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
from pathlib import Path

def detectar():

    ambiente = {
        "sistema": platform.system(),
        "python": platform.python_version(),
        "hostname": platform.node(),
        "ambiente": "desconhecido"
    }

    # Detecta Termux
    if Path("/data/data/com.termux").exists():
        ambiente["ambiente"] = "termux"
        ambiente["root"] = "/data/data/com.termux"

    # Detecta Render
    elif os.environ.get("RENDER"):
        ambiente["ambiente"] = "render"
        ambiente["root"] = os.getcwd()

    # Linux comum
    elif platform.system().lower() == "linux":
        ambiente["ambiente"] = "linux"
        ambiente["root"] = os.getcwd()

    return ambiente


if __name__ == "__main__":
    import json
    print(json.dumps(detectar(), indent=4, ensure_ascii=False))
