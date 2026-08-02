

import requests
import sys

API = "https://bash-search-backend.onrender.com/search"

def pesquisar(prompt):
    try:
        r = requests.post(
            API,
            json={"prompt": prompt},
            timeout=20
        )

        if r.status_code != 200:
            return f"Erro HTTP {r.status_code}: {r.text}"

        dados = r.json()

        return dados.get(
            "resposta",
            "Sem resposta da IA."
        )

    except Exception as e:
        return f"Erro conexão: {e}"


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:])

    if not pergunta:
        print("Uso: python3 knowledge.py pergunta")
        exit()

    print(pesquisar(pergunta))
