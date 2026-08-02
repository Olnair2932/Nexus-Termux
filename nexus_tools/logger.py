
from pathlib import Path
from datetime import datetime

LOG_DIR = Path.home() / "sentinela_dev/logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

ARQ = LOG_DIR / "nexus.log"

def registrar(tipo, mensagem):

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ARQ, "a", encoding="utf-8") as f:
        f.write(f"[{agora}] [{tipo}] {mensagem}\n")

if __name__ == "__main__":
    registrar("TESTE", "Logger funcionando")
    print("✅ Registro criado.")
