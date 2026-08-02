
import json
from pathlib import Path

BASE = Path.home() / "sentinela_dev"

SKILLS = BASE / "skills.json"
TOOLS = BASE / "tools_catalog.json"


def carregar_json(arquivo):
    if arquivo.exists():
        return json.loads(
            arquivo.read_text(
                encoding="utf-8"
            )
        )
    return {}


def salvar_json(arquivo, dados):
    arquivo.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def gerar():

    skills = carregar_json(SKILLS)

    catalogo = carregar_json(TOOLS)

    skills.setdefault("skills", {})

    adicionadas = 0

    for nome, info in catalogo.items():

        chave = Path(nome).stem

        if chave in skills["skills"]:
            continue

        skills["skills"][chave] = {
            "executor": "python",
            "script": info["arquivo"],
            "descricao": "Gerado automaticamente",
            "frases": [
                chave.replace("_", " ")
            ]
        }

        adicionadas += 1

    salvar_json(SKILLS, skills)

    print("Novas skills:", adicionadas)


if __name__ == "__main__":
    gerar()
