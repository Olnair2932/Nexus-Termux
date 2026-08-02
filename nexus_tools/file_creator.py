
from pathlib import Path
import sys
import json
import subprocess


ROOT = Path.home() / "sentinela_dev"


def criar_tool(nome, descricao, frases, codigo_python):

    script = ROOT / "nexus_tools" / f"{nome}.py"

    script.write_text(
        codigo_python,
        encoding="utf-8"
    )

    skills = ROOT / "skills.json"

    dados = json.loads(
        skills.read_text(
            encoding="utf-8"
        )
    )

    dados.setdefault(
        "skills",
        {}
    )

    dados["skills"][nome] = {
        "executor": "python",
        "script": f"nexus_tools/{nome}.py",
        "descricao": descricao,
        "frases": frases
    }

    skills.write_text(
        json.dumps(
            dados,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


    teste = subprocess.run(
        [
            "python3",
            "-m",
            "py_compile",
            str(script)
        ],
        capture_output=True,
        text=True
    )


    if teste.returncode != 0:
        print("❌ Erro no código da ferramenta:")
        print(teste.stderr)
        return


    print("✅ Tool criada:", nome)
    print("✅ Skill registrada:", nome)

    # Teste de autoativação humana
    try:
        teste = frases[0]

        resultado = subprocess.run(
            [
                "python3",
                "nexus_tools/memory_lookup.py",
                teste
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True
        )

        if nome in resultado.stdout:
            print("✅ Autoativação confirmada:", teste)
        else:
            print("⚠️ Skill criada, mas frase ainda não ativou:", teste)

    except Exception as e:
        print("⚠️ Falha no teste de ativação:", e)



def criar_arquivo(nome):

    arquivo = ROOT / nome

    arquivo.write_text(
        "Arquivo criado pelo Nexus.\n",
        encoding="utf-8"
    )

    print(
        "Arquivo criado:",
        arquivo
    )



if __name__ == "__main__":

    args = sys.argv[1:]


    if not args:
        print("Uso: file_creator.py <modo>")
        raise SystemExit


    modo = args[0]


    if modo == "criar_tool":

        if len(args) < 5:
            print(
                "Uso: criar_tool nome descricao frases codigo"
            )
            raise SystemExit


        nome = args[1]
        descricao = args[2]

        frases = [
            x.strip()
            for x in args[3].split(",")
            if x.strip()
        ]

        codigo = args[4]


        criar_tool(
            nome,
            descricao,
            frases,
            codigo
        )


    elif modo == "arquivo":

        nome = args[1] if len(args) > 1 else "usuario.txt"
        criar_arquivo(nome)


    else:

        print(
            "Modo desconhecido:",
            modo
        )


def normalizar_nome_tool(frase):

    frase = frase.lower()

    removidas = [
        "mostrar",
        "mostra",
        "ver",
        "me diga",
        "quero saber",
        "qual",
        "quais",
        "nexus",
        "por favor"
    ]

    for palavra in removidas:
        frase = frase.replace(palavra, "")

    frase = "_".join(
        frase.strip().split()
    )

    if not frase.startswith(
        ("ver_", "listar_", "criar_")
    ):
        frase = "ver_" + frase

    return frase

