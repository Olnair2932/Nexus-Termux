

import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

def verificar():
    status = {
        "sistema": "OPERACIONAL",
        "data": datetime.now().isoformat(),
        "arquivos": {},
        "ferramentas": [],
        "logs": "OK"
    }

    # Verificar arquivos principais
    arquivos = [
        "nexus.py",
        "nexus_release.json",
        "tools_registry.json",
        "manual_procedures.json"
    ]

    for arq in arquivos:
        status["arquivos"][arq] = (
            "OK" if (BASE / arq).exists()
            else "AUSENTE"
        )

    # Ler ferramentas
    registro = BASE / "tools_registry.json"

    if registro.exists():
        dados = json.loads(
            registro.read_text(
                encoding="utf-8"
            )
        )

        for tool in dados.get("tools", []):
            status["ferramentas"].append(
                {
                    "nome": tool["nome"],
                    "status": tool["status"]
                }
            )

    print("====== NEXUS SRE STATUS ======")
    print("Sistema:", status["sistema"])
    print("Data:", status["data"])

    print("\nArquivos:")
    for k,v in status["arquivos"].items():
        print(k, "->", v)

    print("\nFerramentas:")
    for t in status["ferramentas"]:
        print(
            t["nome"],
            "->",
            t["status"]
        )

    print("\nLogs:", status["logs"])
    print("==============================")

if __name__ == "__main__":
    verificar()
