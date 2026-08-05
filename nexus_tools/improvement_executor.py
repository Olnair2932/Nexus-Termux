
import json
from pathlib import Path
from .events import melhoria

PLANO = Path.home() / "sentinela_dev/improvement_plan.json"

def executar():

    if not PLANO.exists():
        print("Plano não encontrado.")
        return

    plano = json.loads(
        PLANO.read_text(encoding="utf-8")
    )

    acao = plano.get("proxima_acao", "Nenhuma")

    print("Próxima ação:", acao)

    melhoria(f"Plano executado: {acao}")

if __name__ == "__main__":
    executar()
