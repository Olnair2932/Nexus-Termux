

from pathlib import Path
import json
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent

MEMORIA = BASE / "brain.json"


def carregar():
    try:
        return json.loads(MEMORIA.read_text(encoding="utf-8"))
    except:
        return {
            "aprendizado": {}
        }


def salvar(dados):
    MEMORIA.write_text(
        json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def registrar_acerto(frase, acao):
    brain = carregar()

    aprendizado = brain.setdefault(
        "memoria_aprendizado",
        {}
    )

    item = aprendizado.setdefault(
        frase,
        {
            "acao": acao,
            "acertos": 0,
            "ultimo_acerto": ""
        }
    )

    item["acao"] = acao
    item["acertos"] += 1
    item["ultimo_acerto"] = datetime.now().isoformat()

    salvar(brain)

    print("MEMÓRIA OK:", frase, "->", acao)


def registrar_erro(frase, acao_errada, acao_correta):
    brain = carregar()

    erros = brain.setdefault(
        "erros_aprendidos",
        []
    )

    erros.append({
        "frase": frase,
        "erro": acao_errada,
        "correto": acao_correta,
        "data": datetime.now().isoformat()
    })

    salvar(brain)

    print("CORREÇÃO APRENDIDA")
