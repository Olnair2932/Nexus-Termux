
from pathlib import Path

arquivo = Path.home() / "sentinela_dev/workspace/nexus_test.py"

conteudo = arquivo.read_text(encoding="utf-8")

if "def carregar_contexto" in conteudo:
    print("Contexto já integrado. Nenhuma alteração feita.")
    exit()

conteudo = conteudo.replace(
    'LOG = BASE / "logs/nexus.log"',
    '''LOG = BASE / "logs/nexus.log"
CONTEXT = BASE / "nexus_context"'''
)

conteudo = conteudo.replace(
    'def executar(nome):',
    '''def carregar_contexto():

    arquivos = [
        "NEXUS_RULES.txt",
        "NEXUS_TASKS.txt"
    ]

    for nome in arquivos:
        arquivo = CONTEXT / nome

        if arquivo.exists():
            log(f"Contexto carregado: {nome}")


def executar(nome):'''
)

conteudo = conteudo.replace(
    'log("Inicialização iniciada")',
    '''log("Inicialização iniciada")

    carregar_contexto()'''
)

arquivo.write_text(conteudo, encoding="utf-8")

print("✅ Contexto integrado no workspace com sucesso.")
