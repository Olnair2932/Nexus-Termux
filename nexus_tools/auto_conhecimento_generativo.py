#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "knowledge.json"
PASTA_CONHECIMENTO = ROOT / "conhecimento"

if not DB.exists():
    DB.write_text(
        json.dumps({"knowledge": []}, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

try:
    banco = json.loads(DB.read_text(encoding="utf-8"))
except Exception:
    banco = {"knowledge": []}

banco.setdefault("knowledge", [])

args = sys.argv[1:]


def salvar():
    DB.write_text(
        json.dumps(banco, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def limpar_texto(texto):
    texto = texto.lower()

    remover = [
        "o que você aprendeu sobre ",
        "o que voce aprendeu sobre ",
        "você aprendeu sobre ",
        "voce aprendeu sobre ",
        "aprendeu sobre ",
        "o que é ",
        "o que e ",
        "explique o ",
        "explique ",
        "pesquise ",
        "resuma o ",
        "resuma ",
        "documento ",
        "fale sobre ",
        "sobre "
    ]

    for item in remover:
        texto = texto.replace(item, "")

    texto = re.sub(
        r"[^a-z0-9áéíóúàãõâêîôûç ]",
        "",
        texto,
        flags=re.IGNORECASE
    )

    stopwords = {
        "o","a","os","as",
        "de","da","do","dos","das",
        "que","é","eh",
        "um","uma",
        "com","para","por",
        "sobre","como","funciona",
        "funcionar","explique",
        "explica","fale","me"
    }

    palavras = [
        p for p in texto.split()
        if p not in stopwords
    ]

    return " ".join(palavras).strip()


def imprimir_documentacao(arquivo, conteudo):
    print("=== DOCUMENTAÇÃO NEXUS ===")
    print()
    print(f"Arquivo: {arquivo}")
    print()
    print(conteudo)
    print()
    print("=== FIM_DOCUMENTACAO_NEXUS ===")
def buscar_documentacao(consulta):
    if not PASTA_CONHECIMENTO.exists():
        return False

    consulta = limpar_texto(consulta)
    if not consulta:
        return False

    arquivos = sorted(
        arq for arq in PASTA_CONHECIMENTO.rglob("*")
        if arq.is_file()
        and arq.suffix.lower() in (".md", ".txt")
        and arq.name not in ("indice.json", "historico.json")
    )

    nome_procurado = consulta.replace(" ", "_")

    # 1 - procura pelo nome do arquivo
    for arquivo in arquivos:
        if arquivo.stem.lower() == nome_procurado:
            try:
                conteudo = arquivo.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
                imprimir_documentacao(arquivo, conteudo)
                return True
            except Exception:
                pass

    # 2 - procura pelo conteúdo
    for arquivo in arquivos:
        try:
            conteudo = arquivo.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if consulta in conteudo.lower():
                imprimir_documentacao(arquivo, conteudo)
                return True

        except Exception:
            pass

    return False


def buscar_knowledge(consulta):
    consulta = limpar_texto(consulta)

    for item in banco["knowledge"]:
        texto = (
            item.get("pergunta", "") +
            " " +
            item.get("resposta", "")
        ).lower()

        if consulta and consulta in texto:
            item["acessos"] = item.get("acessos", 0) + 1
            salvar()

            print("=== CONHECIMENTO APRENDIDO ===")
            print()
            print(item.get("resposta", ""))
            return True

    return False
if not args:
    print("Uso:")
    print("  aprender <pergunta> <resposta>")
    print("  buscar <texto>")
    print("  <consulta>")
    sys.exit(1)

modo = args[0].lower()

# -------------------------------------------------------
# MODO APRENDER
# -------------------------------------------------------

if modo == "aprender":

    if len(args) < 3:
        print("Uso:")
        print("  aprender <pergunta> <resposta>")
        sys.exit(1)

    pergunta = limpar_texto(args[1])
    resposta = " ".join(args[2:]).strip()

    banco["knowledge"].append({
        "pergunta": pergunta,
        "resposta": resposta,
        "data": datetime.now().isoformat(),
        "acessos": 0,
        "fonte": "Nexus"
    })

    salvar()

    print("Conhecimento aprendido.")
    sys.exit(0)

# -------------------------------------------------------
# CONSULTA
# -------------------------------------------------------

if modo == "buscar":
    consulta = " ".join(args[1:])
else:
    consulta = " ".join(args)

consulta = consulta.strip()

if buscar_documentacao(consulta):
    sys.exit(0)

if buscar_knowledge(consulta):
    sys.exit(0)
# -------------------------------------------------------
# APRENDIZADO ASSISTIDO
# -------------------------------------------------------

consulta_limpa = limpar_texto(consulta)

print("=== APRENDIZADO_ASSISTIDO_NEXUS ===")
print()
print("Não encontrei conhecimento local sobre:")
print(consulta_limpa if consulta_limpa else consulta)
print()
print("Deseja pesquisar e aprender? Responda: sim")
