
from pathlib import Path
import json

BASE = Path.home() / "sentinela_dev"
BRAIN = BASE / "brain.json"
SKILLS = BASE / "skills.json"


def consultar(frase):

    frase = frase.lower().strip()

    try:

        if BRAIN.exists():

            dados = json.loads(
                BRAIN.read_text(encoding="utf-8")
            )

            # Intenções Bash
            for _, valor in dados.get(
                "intencoes_bash",
                {}
            ).items():

                for item in valor.get("frases", []):

                    if item.lower() in frase:
                        return valor.get("acao")

            # Memória antiga
            for chave, valor in dados.get(
                "memoria_aprendizado",
                {}
            ).items():

                if chave.lower() in frase:

                    if isinstance(valor, dict):
                        return valor.get("acao")

                    return valor

    except Exception:
        pass

    skills = {}

    try:

        if SKILLS.exists():

            skills = json.loads(
                SKILLS.read_text(
                    encoding="utf-8"
                )
            )

            candidatos = []

            for nome, skill in skills.get(
                "skills",
                {}
            ).items():

                for frase_skill in skill.get(
                    "frases",
                    []
                ):

                    if frase_skill.lower() in frase:

                        candidatos.append(
                            (
                                len(frase_skill),
                                nome
                            )
                        )

            if candidatos:

                candidatos.sort(
                    reverse=True
                )

                return candidatos[0][1]

    except Exception:
        pass

    frases_acao = {

        "temperatura": "ver_temperatura",
        "cpu": "ver_cpu",
        "processador": "ver_cpu",
        "bateria": "ver_bateria",
        "ram": "ver_memoria",
        "memoria": "ver_memoria",
        "armazenamento": "ver_armazenamento",
        "disco": "ver_disco",
        "rede": "ver_rede"

    }

    for palavra, ferramenta in frases_acao.items():

        if palavra in frase:

            if ferramenta in skills.get(
                "skills",
                {}
            ):

                return ferramenta

            # Bloqueia AUTO_BUILD para ferramentas já existentes
            if ferramenta in [
                "ver_memoria",
                "ver_armazenamento",
                "ver_rede",
                "ver_bateria",
                "listar_ferramentas"
            ]:
                return ferramenta

            return "AUTO_BUILD:" + ferramenta

    return None


if __name__ == "__main__":

    import sys

    entrada = " ".join(sys.argv[1:])

    resultado = consultar(entrada)

    if resultado:
        print(resultado)
