

import requests


def pesquisar_github(nome):

    url = "https://api.github.com/search/repositories"

    dados = {
        "q": nome,
        "per_page": 5
    }

    r = requests.get(
        url,
        params=dados,
        timeout=15
    )

    if r.status_code != 200:
        return "Erro GitHub"

    resposta = []

    for item in r.json()["items"]:
        resposta.append({
            "nome": item["full_name"],
            "descricao": item["description"],
            "estrelas": item["stargazers_count"],
            "url": item["html_url"]
        })

    return resposta


if __name__ == "__main__":

    import sys

    termo = " ".join(sys.argv[1:])

    resultado = pesquisar_github(termo)

    print(resultado)
