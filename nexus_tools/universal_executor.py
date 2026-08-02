
import json
from pathlib import Path

BASE = Path.home() / "sentinela_dev"

SKILLS = json.loads(
    (BASE / "skills.json").read_text(encoding="utf-8")
)["skills"]

def executar(frase):

    texto = frase.lower()

    for ch in ",.!?:;":
        texto = texto.replace(ch, "")

    texto = texto.replace("nexus", "")
    texto = texto.replace("eu", "")

    texto = " ".join(texto.split())

    for nome, skill in SKILLS.items():

        for f in skill.get("frases", []):

            if f.lower() in texto:

                return {
                    "acao": nome,
                    "executor": skill["executor"]
                }

    return None


if __name__ == "__main__":

    frase = input("Pergunta: ")

    resultado = executar(frase)

    print(resultado)


# Compatibilidade com versões antigas
def descobrir(frase):
    return executar(frase)
