#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path("/data/data/com.termux/files/home/sentinela_dev")
DB = ROOT / "knowledge.json"

if not DB.exists():
    DB.write_text(
        json.dumps({"knowledge":[]}, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

try:
    banco = json.loads(DB.read_text(encoding="utf-8"))
except:
    banco = {"knowledge":[]}


args = sys.argv[1:]

if not args:
    print("Uso:")
    print(" buscar <texto>")
    print(" aprender <pergunta> <resposta>")
    sys.exit()


def salvar():
    DB.write_text(
        json.dumps(banco, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


modo = args[0].lower()


if modo == "aprender":

    pergunta = args[1].lower()
    resposta = " ".join(args[2:])

    banco["knowledge"].append({
        "pergunta": pergunta,
        "resposta": resposta,
        "data": datetime.now().isoformat(),
        "acessos": 0,
        "fonte": "Nexus"
    })

    salvar()

    print("Conhecimento aprendido.")
    sys.exit()


consulta = " ".join(args).lower()

# -------------------------------------------------------

# -------------------------------------------------------
# NORMALIZAR_CONSULTA_RAG
# -------------------------------------------------------

remover = [
    "o que é ",
    "o que e ",
    "explique ",
    "explique o ",
    "pesquise ",
    "sobre "
]

for palavra in remover:
    consulta = consulta.replace(palavra, "")

consulta = consulta.strip()

# NORMALIZACAO_PONTUACAO_RAG

import re

consulta = re.sub(
    r"[^a-zA-Z0-9áéíóúÁÉÍÓÚãõçÇ ]",
    "",
    consulta
).strip().lower()

# -------------------------------------------------------
# NORMALIZAÇÃO DA CONSULTA
# -------------------------------------------------------

stopwords = {
    "o","a","os","as",
    "que","é","eh",
    "explique","explica",
    "como","funciona","funcionar",
    "sobre","fale",
    "de","do","da","dos","das",
    "um","uma","uns","umas",
    "para","por","com","me"
}

palavras = [
    p for p in consulta.split()
    if p not in stopwords
]

if palavras:
    consulta = palavras[-1]



# BUSCA_CONHECIMENTO_MANUAIS
# -------------------------------------------------------

pasta_conhecimento = ROOT / "conhecimento"

if pasta_conhecimento.exists():

    arquivos = [
        arq for arq in pasta_conhecimento.rglob("*")
        if arq.is_file()
        and arq.suffix.lower() in (".md", ".txt")
        and arq.name not in ("indice.json", "historico.json")
    ]

    consulta_normalizada = consulta.strip().lower()
    nome_procurado = consulta_normalizada.replace(" ", "_")

    # -------------------------------------------------------
    # ETAPA 1 - procura pelo nome do arquivo
    # -------------------------------------------------------

    for arquivo in arquivos:

        if arquivo.stem.lower() == nome_procurado:

            try:
                conteudo = arquivo.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                print("=== DOCUMENTAÇÃO NEXUS ===")
                print()
                print("Arquivo:", arquivo)
                print()
                print(conteudo[:4000])
                print("\n=== FIM_DOCUMENTACAO_NEXUS ===")
                sys.exit(0)

            except Exception:
                pass

    # -------------------------------------------------------
    # ETAPA 2 - procura pelo conteúdo
    # -------------------------------------------------------

    for arquivo in arquivos:

        try:
            conteudo = arquivo.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if consulta_normalizada in conteudo.lower():

                print("=== DOCUMENTAÇÃO NEXUS ===")
                print()
                print("Arquivo:", arquivo)
                print()
                print(conteudo[:4000])
                print("\n=== FIM_DOCUMENTACAO_NEXUS ===")
                sys.exit(0)

        except Exception:
            pass

for item in banco["knowledge"]:

    texto = (
        item["pergunta"] +
        " " +
        item["resposta"]
    ).lower()

    if consulta in texto:

        item["acessos"] += 1
        salvar()

        print("=== CONHECIMENTO APRENDIDO ===\n")
        print(item["resposta"])
        sys.exit()



# -------------------------------------------------------
if rag_encontrado:
    sys.exit(0)

# APRENDIZADO_ASSISTIDO_NEXUS
# -------------------------------------------------------

print("=== APRENDIZADO_ASSISTIDO_NEXUS ===")
print()
print("Não encontrei conhecimento local sobre:")
print(consulta)
print()
print("Deseja pesquisar e aprender? Responda: sim")

