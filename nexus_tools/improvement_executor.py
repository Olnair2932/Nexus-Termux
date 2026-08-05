
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

    # Registrar melhoria aplicada no brain.json
    brain = Path.home() / "sentinela_dev/brain.json"

    try:
        dados = json.loads(brain.read_text(encoding="utf-8"))
    except:
        dados = {}

    historico = dados.setdefault("melhorias_aplicadas", [])

    historico.append({
        "acao": acao,
        "status": "executada"
    })

    brain.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


if __name__ == "__main__":
    executar()
