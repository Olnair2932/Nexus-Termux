#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "knowledge.json"

if not DB.exists():
    DB.write_text(
        json.dumps({"knowledge":[]}, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

banco = json.loads(
    DB.read_text(encoding="utf-8")
)


def salvar():
    DB.write_text(
        json.dumps(banco, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


if len(sys.argv) < 2:
    print("""
Uso:

pesquisar_fonte_conhecimento.py <tema>

Exemplo:
pesquisar_fonte_conhecimento.py Ollama
""")
    sys.exit()


tema = " ".join(sys.argv[1:]).strip()


fontes = {
    "ollama":
    "O Ollama permite executar modelos de linguagem localmente como Llama, Mistral e outros, oferecendo execução de LLMs no computador sem depender somente de serviços em nuvem.",

    "python":
    "Python é uma linguagem de programação interpretada usada em automação, inteligência artificial, análise de dados e desenvolvimento de sistemas.",

    "nexus":
    "O Nexus SRE utiliza memória local, RAG, ferramentas Python, execução segura e integração com Termux para automação inteligente."
}


resposta = None

for chave, valor in fontes.items():

    if chave in tema.lower():
        resposta = valor
        break


if resposta:

    banco["knowledge"].append({

        "pergunta": tema.lower(),
        "resposta": resposta,
        "data": datetime.now().isoformat(),
        "fonte": "pesquisa_fonte_local",
        "acessos": 0

    })

    salvar()

    print("=== FONTE ADICIONADA ===")
    print(resposta)

else:

    print("Nenhuma fonte encontrada para:", tema)
    print("Adicione uma fonte manualmente usando auto_conhecimento_generativo.py")
