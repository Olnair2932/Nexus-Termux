
from pathlib import Path
from collections import Counter
import re
import json

LOG = Path.home() / "sentinela_dev/logs/nexus.log"
PLANO = Path.home() / "sentinela_dev/improvement_plan.json"

def gerar():

    if not LOG.exists():
        print("Nenhum log encontrado.")
        return

    eventos = Counter()

    for linha in LOG.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines():

        m = re.search(r"\[(ERRO|MELHORIA|CONSULTA|APRENDIZADO)\]", linha)

        if m:
            eventos[m.group(1)] += 1

    plano = {
        "objetivo": "Aprender com os próprios logs",
        "estatisticas": dict(eventos),
        "proxima_acao": None
    }

    if eventos["ERRO"] > 0:
        plano["proxima_acao"] = "Corrigir erros recorrentes"

    elif eventos["CONSULTA"] > eventos["APRENDIZADO"]:
        plano["proxima_acao"] = "Aprender assuntos mais consultados"

    else:
        plano["proxima_acao"] = "Otimizar desempenho"

    PLANO.write_text(
        json.dumps(plano, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("✅ improvement_plan.json atualizado.")
    print(plano["proxima_acao"])

if __name__ == "__main__":
    gerar()
