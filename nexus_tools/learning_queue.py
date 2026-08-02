

import json
from pathlib import Path

ARQ = Path.home() / "sentinela_dev/learning_queue.json"

PADRAO = {
    "indice": 0,
    "comandos": [
        "mkdir",
        "ls",
        "cp",
        "mv",
        "rm",
        "grep",
        "find",
        "curl",
        "git",
        "python",
        "sed",
        "awk",
        "chmod",
        "chown",
        "tar",
        "zip",
        "unzip",
        "ssh",
        "nano",
        "vim"
    ]
}

if not ARQ.exists():
    ARQ.write_text(
        json.dumps(PADRAO, indent=4),
        encoding="utf-8"
    )

def proximo():

    dados = json.loads(
        ARQ.read_text(encoding="utf-8")
    )

    comandos = dados["comandos"]
    indice = dados["indice"]

    comando = comandos[indice]

    dados["indice"] = (indice + 1) % len(comandos)

    ARQ.write_text(
        json.dumps(dados, indent=4),
        encoding="utf-8"
    )

    return comando


if __name__ == "__main__":
    print(proximo())
