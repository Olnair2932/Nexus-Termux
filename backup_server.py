#!/usr/bin/env python3

from pathlib import Path
import shutil
import time

origem = Path("server.js")

if not origem.exists():
    raise SystemExit("server.js não encontrado.")

backup = Path(
    f"server.js.bak.{int(time.time())}"
)

shutil.copy2(origem, backup)

print("Backup criado:", backup)
