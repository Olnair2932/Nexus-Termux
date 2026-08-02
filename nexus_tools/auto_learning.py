

import subprocess
from pathlib import Path
import time

from mode import modo_atual
from learning_queue import proximo
from known import conhece

print("Auto Learning iniciado.")

while True:

    if modo_atual() == "online":
        print("[ONLINE] Aguardando usuário...")
        time.sleep(5)
        continue

    comando = proximo()

    if conhece(comando):
        print(f"[JÁ APRENDIDO] {comando}")
        time.sleep(1)
        continue

    print(f"[NOVO] {comando}")

    try:

        resposta = subprocess.check_output(
            [
                "python3",
                "brain_agent.py",
                comando
            ],
            cwd=Path(__file__).parent,
            text=True
        )

        print(resposta.strip())

    except Exception as e:

        print("Erro:", e)

    time.sleep(5)
