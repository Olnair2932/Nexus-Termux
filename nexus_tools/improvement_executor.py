
import json
from pathlib import Path
from .events import melhoria
from .improvement_guard import melhoria_ja_existe

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

    if melhoria_ja_existe(acao):
        print("⚠️ Melhoria já registrada. Evitando duplicidade.")
        return

    melhoria(f"Plano executado: {acao}")

    # Registrar melhoria aplicada no brain.json
    brain = Path.home() / "sentinela_dev/brain.json"

    try:
        dados = json.loads(brain.read_text(encoding="utf-8"))
    except:
        dados = {}

    historico = dados.setdefault("melhorias_aplicadas", [])

    if any(item.get("acao") == acao for item in historico):
        print("⚠️ Melhoria já registrada. Evitando duplicidade.")
        return

    if validar_melhoria():
        status = "validada"
    else:
        status = "falhou"

    historico.append({
        "acao": acao,
        "status": status
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


# AUTO_REPAIR_OK
print("Autocorreção registrada com sucesso.")
