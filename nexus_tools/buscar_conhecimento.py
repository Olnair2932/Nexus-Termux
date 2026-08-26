#!/usr/bin/env python3

from pathlib import Path
import re
import sys
import unicodedata

BASE = Path(__file__).resolve().parent.parent
PASTA_APRENDIDOS = BASE / "conhecimento" / "aprendidos"


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9\s_-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def extrair_tema(entrada):
    tema = normalizar(entrada)

    padroes = [
        r"^o que voce sabe sobre\s+",
        r"^o que voce sabe de\s+",
        r"^explica\s+",
        r"^explique\s+",
        r"^fale sobre\s+",
        r"^me explique\s+",
        r"^quero saber sobre\s+",
        r"^o que aprendeu sobre\s+",
        r"^o que voce aprendeu sobre\s+",
    ]

    for padrao in padroes:
        tema = re.sub(padrao, "", tema, count=1)

    tema = re.sub(
        r"\s+(?:com base nas pesquisas salvas|com base no conhecimento salvo|"
        r"com base nas pesquisas|das pesquisas salvas|nas pesquisas salvas).*$",
        "",
        tema,
    )

    return tema.strip(" ,.!?:;")


def pontuar(tema, arquivo, conteudo):
    alvo = normalizar(tema)
    nome = normalizar(arquivo.stem)
    texto = normalizar(conteudo)

    palavras = [
        p for p in alvo.split()
        if len(p) >= 3
    ]

    pontos = 0

    if alvo and alvo in nome:
        pontos += 100

    if alvo and alvo in texto:
        pontos += 50

    for palavra in palavras:
        if palavra in nome:
            pontos += 20
        elif palavra in texto:
            pontos += 5

    return pontos


def buscar(entrada):
    tema = extrair_tema(entrada)

    if not PASTA_APRENDIDOS.exists():
        return tema, []

    candidatos = []

    for arquivo in PASTA_APRENDIDOS.glob("*.md"):
        try:
            conteudo = arquivo.read_text(encoding="utf-8")
        except Exception:
            continue

        pontos = pontuar(tema, arquivo, conteudo)

        if pontos > 0:
            candidatos.append((pontos, arquivo, conteudo))

    candidatos.sort(key=lambda item: item[0], reverse=True)

    return tema, candidatos


def main():
    entrada = " ".join(sys.argv[1:]).strip()

    if not entrada:
        print("Uso: python3 nexus_tools/buscar_conhecimento.py <pergunta>")
        return 1

    tema, resultados = buscar(entrada)

    print()
    print("=== BUSCA NA BASE DE CONHECIMENTO NEXUS ===")
    print()
    print("Pergunta:", entrada)
    print("Tema identificado:", tema)
    print()

    if not resultados:
        print("Não encontrei conhecimento local sobre:")
        print(tema)
        print()
        print("Arquivos pesquisados:")
        print(PASTA_APRENDIDOS)
        return 0

    melhor_pontuacao, melhor_arquivo, melhor_conteudo = resultados[0]

    print("Conhecimento encontrado:")
    print()
    print("Arquivo:", melhor_arquivo)
    print("Relevância:", melhor_pontuacao)
    print()
    print("------------------------------------------")
    print(melhor_conteudo.strip())
    print("------------------------------------------")

    if len(resultados) > 1:
        print()
        print("Outros documentos relacionados:")
        for pontos, arquivo, _ in resultados[1:4]:
            print(f"- {arquivo.name} ({pontos} pontos)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
