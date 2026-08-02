

from pathlib import Path
import subprocess
from datetime import datetime

BASE = Path.home() / "sentinela_dev"
TOOLS = BASE / "nexus_tools"
LOG = BASE / "logs/nexus.log"


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] [NEXUS] {msg}\n"
        )


def executar(nome):

    arquivo = TOOLS / nome

    if arquivo.exists():

        subprocess.run(
            [
                "python3",
                str(arquivo)
            ]
        )


def iniciar():

    print("""
====================
     NEXUS CORE
====================
""")

    log("Inicialização iniciada")

    print("🔄 Sincronizando...")
    executar("system_sync.py")

    print("🔍 Auditando ferramentas...")
    executar("tool_auditor.py")

    print("[OK] Nexus iniciado.")
    print("Aguardando comandos.")

    log("Sistema iniciado")


if __name__ == "__main__":
    iniciar()
