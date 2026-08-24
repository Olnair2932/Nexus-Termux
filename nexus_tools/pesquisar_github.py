#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import urllib.parse
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent

load_dotenv(str(ROOT / ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GITHUB_API = "https://api.github.com"

GEMINI_API = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.1-flash-lite:generateContent"
)


def executar_curl(args):
    resultado = subprocess.run(
        args,
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            resultado.stderr.strip()
            or "curl retornou erro."
        )

    return resultado.stdout


def pesquisar_github(consulta):
    query = urllib.parse.quote(consulta)

    url = (
        f"{GITHUB_API}/search/repositories"
        f"?q={query}"
        f"&sort=stars"
        f"&order=desc"
        f"&per_page=10"
    )

    cmd = [
        "curl",
        "-s",
        "-L",
        url,
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28"
    ]

    resposta = executar_curl(cmd)

    try:
        return json.loads(resposta)
    except json.JSONDecodeError:
        raise RuntimeError(
            "GitHub retornou uma resposta inválida."
        )


def obter_readme(owner, repo):
    url = (
        f"{GITHUB_API}/repos/"
        f"{urllib.parse.quote(owner)}/"
        f"{urllib.parse.quote(repo)}/readme"
    )

    cmd = [
        "curl",
        "-s",
        "-L",
        url,
        "-H",
        "Accept: application/vnd.github.raw+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28"
    ]

    return executar_curl(cmd)


def preparar_resultados(dados):
    resultados = []

    for item in dados.get("items", []):
        nome = item.get("full_name", "")
        partes = nome.split("/", 1)

        readme = ""

        if len(partes) == 2:
            owner, repo = partes
            try:
                readme = obter_readme(owner, repo)
            except Exception as erro:
                print(
                    f"⚠️ Não foi possível obter README de {nome}: {erro}"
                )

        resultados.append({
            "nome": nome,
            "descricao": item.get("description"),
            "url": item.get("html_url"),
            "linguagem": item.get("language"),
            "estrelas": item.get("stargazers_count"),
            "forks": item.get("forks_count"),
            "issues": item.get("open_issues_count"),
            "atualizado": item.get("updated_at"),
            "topicos": item.get("topics", []),
            "readme": readme
        })

    return resultados


def montar_contexto(resultados):
    blocos = []
    LIMITE_README = 3000

    for item in resultados[:5]:
        nome = item.get('nome', '')

        if '/' not in nome:
            continue

        owner, repo = nome.split('/', 1)

        try:
            readme = obter_readme(owner, repo)
        except Exception as erro:
            readme = f'{erro}'

        if not readme:
            readme = 'README não encontrado.'

        readme_reduzido = readme[:LIMITE_README]

        blocos.append({
            'repositorio': {
                'nome': item.get('nome'),
                'descricao': item.get('descricao'),
                'url': item.get('url'),
                'linguagem': item.get('linguagem'),
                'estrelas': item.get('estrelas'),
                'forks': item.get('forks'),
                'issues': item.get('issues'),
                'atualizado': item.get('atualizado'),
                'topicos': item.get('topicos', [])
            },
            'readme': readme_reduzido
        })

    return blocos
def analisar_com_gemini(tema, contexto):

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY não encontrada."
        )

    prompt = f"""
Você é o mecanismo de análise de conhecimento do Nexus.

Foi realizada uma pesquisa pública no GitHub.

Tema pesquisado:
{tema}

Analise SOMENTE as informações fornecidas abaixo.

Produza um relatório em Markdown contendo:

# {tema}

## Resumo

Explique objetivamente o que foi encontrado.

## Projetos relevantes

Para cada projeto relevante informe:

- nome
- descrição
- linguagem principal
- estrelas
- URL
- finalidade
- relevância para o tema

## Conhecimento técnico

Extraia os conceitos técnicos importantes encontrados
nos projetos e em seus README.

## Possíveis aplicações

Explique como esse conhecimento pode ser utilizado.

## Referências

Liste os repositórios utilizados como fonte.

## Observações

Separe claramente fatos encontrados das interpretações.

Regras:

- não invente informações;
- não atribua características não presentes nos dados;
- preserve as URLs;
- não utilize emojis;
- escreva em português;
- seja técnico e objetivo.

Dados encontrados:

{json.dumps(contexto, ensure_ascii=False, indent=2)}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    url = (
        f"{GEMINI_API}"
        f"?key={urllib.parse.quote(GEMINI_API_KEY)}"
    )

    cmd = [
        "curl",
        "-s",
        "-X",
        "POST",
        url,
        "-H",
        "Content-Type: application/json",
        "-d",
        json.dumps(payload, ensure_ascii=False)
    ]

    resposta = executar_curl(cmd)

    try:
        dados = json.loads(resposta)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Gemini retornou resposta inválida."
        )

    try:
        return (
            dados["candidates"][0]
            ["content"]["parts"][0]["text"]
        )
    except (KeyError, IndexError, TypeError):
        print(json.dumps(
            dados,
            indent=2,
            ensure_ascii=False
        ))
        raise RuntimeError(
            "Gemini não retornou conteúdo utilizável."
        )


def salvar_conhecimento(tema, texto):

    pasta = ROOT / "conhecimento" / "aprendidos"

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    nome = (
        tema.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    arquivo = pasta / f"github_{nome}.md"

    conteudo = f"""# Pesquisa GitHub: {tema}

Data:
{datetime.now().isoformat()}

Fonte:
GitHub + Gemini

{texto}
"""

    arquivo.write_text(
        conteudo,
        encoding="utf-8"
    )

    return arquivo


def atualizar_indice():

    script = (
        ROOT
        / "nexus_tools"
        / "criar_indice_conhecimento.py"
    )

    if not script.exists():
        print(
            "Aviso: criar_indice_conhecimento.py "
            "não encontrado."
        )
        return

    subprocess.run(
        ["python3", str(script)],
        check=False
    )


def registrar_historico(
    tema,
    arquivo,
    quantidade
):

    historico = (
        ROOT
        / "conhecimento"
        / "historico.json"
    )

    try:

        if historico.exists():
            dados = json.loads(
                historico.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            )

            if not isinstance(dados, list):
                dados = []
        else:
            dados = []

        dados.append({
            "data": datetime.now().isoformat(),
            "evento": "Pesquisa de conhecimento no GitHub",
            "tema": tema,
            "arquivo": str(arquivo),
            "origem": "GitHub + Gemini 3.1 Flash Lite",
            "repositorios_encontrados": quantidade
        })

        historico.write_text(
            json.dumps(
                dados,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        print("Histórico atualizado.")

    except Exception as erro:
        print(
            "Aviso ao atualizar histórico:",
            erro
        )


def main():

    if len(sys.argv) < 2:
        print()
        print(
            "Uso: python3 "
            "nexus_tools/pesquisar_github.py <tema>"
        )
        print()
        sys.exit(1)

    tema = " ".join(sys.argv[1:]).strip()

    if not tema:
        print("ERRO: tema vazio.")
        sys.exit(1)

    print()
    print("==========================================")
    print("NEXUS — PESQUISA NO GITHUB")
    print("==========================================")
    print()
    print("Tema:", tema)
    print()

    print("Pesquisando no GitHub...")

    dados = pesquisar_github(tema)

    resultados = preparar_resultados(dados)

    if not resultados:
        print()
        print("Nenhum repositório público encontrado.")
        return 0

    print(
        f"{len(resultados)} repositório(s) encontrado(s)."
    )

    print()
    print("Obtendo README dos principais projetos...")

    contexto = montar_contexto(resultados)

    print()
    print("Analisando conhecimento com Gemini...")

    texto = analisar_com_gemini(
        tema,
        contexto
    )

    print()
    print("Salvando conhecimento...")

    arquivo = salvar_conhecimento(
        tema,
        texto
    )

    print()
    print("Conhecimento salvo em:")
    print(arquivo)

    print()
    print("Atualizando índice...")

    atualizar_indice()

    registrar_historico(
        tema,
        arquivo,
        len(resultados)
    )

    print()
    print("==========================================")
    print("PESQUISA CONCLUÍDA")
    print("==========================================")
    print()
    print("Tema:", tema)
    print("Repositórios:", len(resultados))
    print("Arquivo:", arquivo)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
