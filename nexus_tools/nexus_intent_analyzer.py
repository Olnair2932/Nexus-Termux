#!/usr/bin/env python3

import sys
import os
import json
import re
import urllib.request
import urllib.error


# ============================================================
# NEXUS INTENT ANALYZER
# ============================================================
#
# Responsabilidade:
#
# 1. Entender a intenção básica do usuário.
# 2. Distinguir:
#       - conversa
#       - executar Bash
#       - executar Python
#       - usar ferramenta existente
#       - criar script Python
#       - criar script Bash
#       - criar ferramenta
#       - consultar conhecimento
#
# 3. Nunca executar comandos.
# 4. Nunca criar arquivos de ferramenta.
# 5. Nunca executar file_creator.
# 6. Nome de ferramenta limitado a 60 caracteres.
# 7. Firebase é secundário.
#
# ============================================================


MAX_NOME = 60


VALID_INTENTS = {
    "conversar",
    "executar_bash",
    "executar_python",
    "usar_ferramenta",
    "criar_script_python",
    "criar_script_bash",
    "criar_ferramenta",
    "consultar_conhecimento",
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(texto):
    if texto is None:
        return ""

    texto = str(texto).strip().lower()

    substituicoes = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "í": "i",
        "ì": "i",
        "î": "i",
        "ï": "i",
        "ó": "o",
        "ò": "o",
        "õ": "o",
        "ô": "o",
        "ö": "o",
        "ú": "u",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    return texto


# ============================================================
# NOME DE FERRAMENTA
# ============================================================

def normalizar_nome(nome):
    if not nome:
        return None

    nome = normalizar_texto(nome)

    nome = re.sub(
        r"[^a-z0-9_]+",
        "_",
        nome
    )

    nome = re.sub(
        r"_+",
        "_",
        nome
    )

    nome = nome.strip("_")

    if not nome:
        return None

    return nome[:MAX_NOME]


# ============================================================
# DETECTAR LINGUAGEM
# ============================================================

def detectar_linguagem(texto):
    t = normalizar_texto(texto)

    if (
        "python" in t
        or ".py" in t
        or "script python" in t
    ):
        return "python"

    if (
        "bash" in t
        or "shell" in t
        or ".sh" in t
        or "linux" in t
        or "terminal" in t
    ):
        return "bash"

    return None


# ============================================================
# DETECTAR BASH / LINUX
# ============================================================

def parece_bash(texto):
    t = normalizar_texto(texto).strip()

    comandos_exatos = {
        "ls",
        "pwd",
        "whoami",
        "id",
        "top",
        "htop",
        "df",
        "free",
        "uname",
        "ps",
        "ifconfig",
        "ip",
    }

    if t in comandos_exatos:
        return True

    comandos = [
        "ls ",
        "pwd ",
        "cd ",
        "df ",
        "du ",
        "ps ",
        "free ",
        "uname ",
        "whoami ",
        "grep ",
        "find ",
        "cat ",
        "head ",
        "tail ",
        "chmod ",
        "mkdir ",
        "touch ",
        "cp ",
        "mv ",
        "tar ",
        "zip ",
        "unzip ",
        "echo ",
        "ip ",
        "ping ",
        "kill ",
    ]

    for comando in comandos:
        if t.startswith(comando):
            return True

    frases = [
        "liste os arquivos",
        "listar os arquivos",
        "listar arquivos",
        "mostre os arquivos",
        "mostrar os arquivos",
        "liste a pasta",
        "listar a pasta",
        "mostre a pasta",
        "liste o diretorio",
        "listar o diretorio",
        "mostre o diretorio",
        "liste os diretorios",
        "listar os diretorios",
        "mostre os diretorios",
        "mostre o conteudo da pasta",
        "qual o diretorio atual",
        "qual a pasta atual",
        "onde estou",
        "mostre os processos",
        "listar processos",
        "ver processos",
        "ver espaco em disco",
        "mostrar espaco em disco",
        "quanto espaco em disco",
    ]

    for frase in frases:
        if frase in t:
            return True

    if "execute o comando" in t:
        return True

    if "rode o comando" in t:
        return True

    if "executar bash" in t:
        return True

    if "rode bash" in t:
        return True

    if "execute bash" in t:
        return True

    if "comando linux" in t:
        return True

    return False


# ============================================================
# DETECTAR EXECUÇÃO PYTHON
# ============================================================

def parece_execucao_python(texto):
    t = normalizar_texto(texto)

    indicadores = [
        "execute python",
        "executar python",
        "rode python",
        "rodar python",
        "execute o python",
        "rode o python",
        "execute o script",
        "executar o script",
        "rode o script",
        "rodar o script",
        ".py",
    ]

    for indicador in indicadores:
        if indicador in t:
            return True

    return False


# ============================================================
# DETECTAR CRIAÇÃO DE SCRIPT PYTHON
# ============================================================

def quer_criar_script_python(texto):
    t = normalizar_texto(texto)

    criacao = [
        "crie",
        "criar",
        "gere",
        "gerar",
        "escreva",
        "escrever",
        "desenvolva",
        "desenvolver",
        "faca",
        "fazer",
    ]

    python = [
        "script python",
        "codigo python",
        "programa python",
        "arquivo python",
    ]

    tem_criacao = any(x in t for x in criacao)
    tem_python = any(x in t for x in python)

    return tem_criacao and tem_python


# ============================================================
# DETECTAR CRIAÇÃO DE SCRIPT BASH
# ============================================================

def quer_criar_script_bash(texto):
    t = normalizar_texto(texto)

    criacao = [
        "crie",
        "criar",
        "gere",
        "gerar",
        "escreva",
        "escrever",
        "desenvolva",
        "desenvolver",
        "faca",
        "fazer",
    ]

    bash = [
        "script bash",
        "script shell",
        "codigo bash",
        "codigo shell",
        "arquivo bash",
        "arquivo shell",
    ]

    tem_criacao = any(x in t for x in criacao)
    tem_bash = any(x in t for x in bash)

    return tem_criacao and tem_bash


# ============================================================
# DETECTAR CRIAÇÃO DE FERRAMENTA
# ============================================================

def quer_criar_ferramenta(texto):
    t = normalizar_texto(texto)

    verbos = [
        "crie",
        "criar",
        "gere",
        "gerar",
        "desenvolva",
        "desenvolver",
        "faca",
        "fazer",
        "adicione",
        "adicionar",
    ]

    palavras_ferramenta = [
        "ferramenta",
        "tool",
    ]

    tem_verbo = any(x in t for x in verbos)
    tem_ferramenta = any(x in t for x in palavras_ferramenta)

    return tem_verbo and tem_ferramenta


# ============================================================
# EXTRAIR NOME DE FERRAMENTA
# ============================================================

def extrair_nome_ferramenta(texto):
    t = normalizar_texto(texto)

    padroes = [
        r"ferramenta\s+chamada\s+([a-z0-9_\- ]+)",
        r"ferramenta\s+de\s+([a-z0-9_\- ]+)",
        r"tool\s+chamada\s+([a-z0-9_\- ]+)",
        r"crie\s+uma\s+ferramenta\s+([a-z0-9_\- ]+)",
        r"criar\s+uma\s+ferramenta\s+([a-z0-9_\- ]+)",
    ]

    for padrao in padroes:
        resultado = re.search(
            padrao,
            t
        )

        if resultado:
            nome = resultado.group(1).strip()

            nome = re.split(
                r"\s+(?:para|que|capaz|usando|em|no|na)\s+",
                nome,
                maxsplit=1
            )[0]

            return normalizar_nome(nome)

    # --------------------------------------------------------
    # Se não houver nome explícito, NÃO inventar.
    # --------------------------------------------------------

    return None


# ============================================================
# DETECTAR FERRAMENTA EXISTENTE
# ============================================================

def parece_ferramenta_existente(texto):
    t = normalizar_texto(texto)

    executar = [
        "execute a ferramenta",
        "executar a ferramenta",
        "rode a ferramenta",
        "rodar a ferramenta",
        "use a ferramenta",
        "usar a ferramenta",
        "chame a ferramenta",
        "chamar a ferramenta",
    ]

    return any(x in t for x in executar)


# ============================================================
# DETECTAR CONHECIMENTO
# ============================================================

def parece_consulta_conhecimento(texto):
    t = normalizar_texto(texto)

    frases = [
        "explique",
        "o que e",
        "o que voce sabe",
        "como funciona",
        "documentacao",
        "documentacao do",
        "manual",
        "readme",
        "base de conhecimento",
        "pesquise",
        "pesquisar",
        "consulte",
        "consultar conhecimento",
    ]

    return any(x in t for x in frases)


# ============================================================
# ANÁLISE PRINCIPAL
# ============================================================

def analisar_localmente(pedido):
    texto = str(pedido).strip()

    if not texto:
        return {
            "intencao": "conversar",
            "linguagem": None,
            "nome": None,
            "pedido": "",
            "confianca": 1.0,
            "motivo": "Nenhum pedido recebido."
        }

    t = normalizar_texto(texto)

    # --------------------------------------------------------
    # 1. CRIAÇÃO DE FERRAMENTA
    # --------------------------------------------------------
    #
    # Tem prioridade sobre execução.
    #
    # Mas SOMENTE se o usuário disser explicitamente
    # "ferramenta".
    #
    # --------------------------------------------------------

    if quer_criar_ferramenta(texto):

        nome = extrair_nome_ferramenta(texto)

        return {
            "intencao": "criar_ferramenta",
            "linguagem": detectar_linguagem(texto),
            "nome": nome,
            "nome_maximo": MAX_NOME,
            "pedido": texto,
            "confianca": 0.98,
            "motivo": (
                "O usuário solicitou explicitamente "
                "a criação de uma ferramenta."
            )
        }

    # --------------------------------------------------------
    # 2. CRIAÇÃO DE SCRIPT PYTHON
    # --------------------------------------------------------

    if quer_criar_script_python(texto):

        return {
            "intencao": "criar_script_python",
            "linguagem": "python",
            "nome": None,
            "pedido": texto,
            "confianca": 0.98,
            "motivo": (
                "O usuário solicitou explicitamente "
                "a criação de um script Python."
            )
        }

    # --------------------------------------------------------
    # 3. CRIAÇÃO DE SCRIPT BASH
    # --------------------------------------------------------

    if quer_criar_script_bash(texto):

        return {
            "intencao": "criar_script_bash",
            "linguagem": "bash",
            "nome": None,
            "pedido": texto,
            "confianca": 0.98,
            "motivo": (
                "O usuário solicitou explicitamente "
                "a criação de um script Bash."
            )
        }

    # --------------------------------------------------------
    # 4. EXECUÇÃO PYTHON
    # --------------------------------------------------------

    if parece_execucao_python(texto):

        return {
            "intencao": "executar_python",
            "linguagem": "python",
            "nome": None,
            "pedido": texto,
            "confianca": 0.96,
            "motivo": (
                "O usuário solicitou execução "
                "de Python ou de um script Python."
            )
        }

    # --------------------------------------------------------
    # 5. FERRAMENTA EXISTENTE
    # --------------------------------------------------------

    if parece_ferramenta_existente(texto):

        return {
            "intencao": "usar_ferramenta",
            "linguagem": "python",
            "nome": None,
            "pedido": texto,
            "confianca": 0.96,
            "motivo": (
                "O usuário solicitou explicitamente "
                "o uso de uma ferramenta existente."
            )
        }

    # --------------------------------------------------------
    # 6. BASH / LINUX
    # --------------------------------------------------------

    if parece_bash(texto):

        return {
            "intencao": "executar_bash",
            "linguagem": "bash",
            "nome": None,
            "pedido": texto,
            "confianca": 0.96,
            "motivo": (
                "O pedido corresponde a uma operação "
                "direta de Linux/Bash."
            )
        }

    # --------------------------------------------------------
    # 7. CONHECIMENTO
    # --------------------------------------------------------

    if parece_consulta_conhecimento(texto):

        return {
            "intencao": "consultar_conhecimento",
            "linguagem": None,
            "nome": None,
            "pedido": texto,
            "confianca": 0.90,
            "motivo": (
                "O usuário está solicitando conhecimento, "
                "explicação ou consulta."
            )
        }

    # --------------------------------------------------------
    # 8. CONVERSA
    # --------------------------------------------------------

    return {
        "intencao": "conversar",
        "linguagem": None,
        "nome": None,
        "pedido": texto,
        "confianca": 0.90,
        "motivo": (
            "Nenhuma operação executável foi identificada "
            "com segurança; fallback para conversa."
        )
    }


# ============================================================
# FIREBASE
# ============================================================

def obter_firebase_url():
    candidatos = [
        os.environ.get("FIREBASE_DATABASE_URL"),
        os.environ.get("FIREBASE_URL"),
        os.environ.get("FIREBASE_DATABASE"),
    ]

    for valor in candidatos:
        if valor:
            return valor.rstrip("/")

    return None


def sincronizar_firebase(resultado):
    """
    Firebase é secundário.

    Se não existir configuração, retorna False.
    Se falhar, o analisador continua funcionando.
    """

    firebase_url = obter_firebase_url()

    if not firebase_url:
        return False

    try:

        caminho = (
            firebase_url
            + "/nexus/intent_memory/current.json"
        )

        dados = dict(resultado)

        request = urllib.request.Request(
            caminho,
            data=json.dumps(
                dados,
                ensure_ascii=False
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="PUT"
        )

        with urllib.request.urlopen(
            request,
            timeout=5
        ) as response:

            return (
                200 <= response.status < 300
            )

    except Exception as e:

        print(
            "AVISO_FIREBASE_INTENT:",
            str(e),
            file=sys.stderr
        )

        return False


# ============================================================
# MEMÓRIA LOCAL
# ============================================================

def registrar_memoria_local(resultado):
    try:

        root = os.environ.get(
            "NEXUS_ROOT",
            os.path.expanduser(
                "~/sentinela_dev"
            )
        )

        pasta = os.path.join(
            root,
            "nexus_tools",
            "memory"
        )

        os.makedirs(
            pasta,
            exist_ok=True
        )

        arquivo = os.path.join(
            pasta,
            "intent_memory.json"
        )

        dados = []

        if os.path.exists(arquivo):

            try:

                with open(
                    arquivo,
                    "r",
                    encoding="utf-8"
                ) as f:

                    existente = json.load(f)

                    if isinstance(
                        existente,
                        list
                    ):
                        dados = existente

            except Exception:
                dados = []

        dados.append(resultado)

        # Mantém somente as últimas 100 intenções.

        dados = dados[-100:]

        with open(
            arquivo,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                dados,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:

        print(
            "AVISO_MEMORIA_LOCAL:",
            str(e),
            file=sys.stderr
        )


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:

        resultado = {
            "intencao": "conversar",
            "linguagem": None,
            "nome": None,
            "pedido": "",
            "confianca": 1.0,
            "motivo": "Nenhum pedido recebido."
        }

    else:

        pedido = " ".join(
            sys.argv[1:]
        ).strip()

        resultado = analisar_localmente(
            pedido
        )

    # --------------------------------------------------------
    # GARANTIA DE SEGURANÇA
    # --------------------------------------------------------

    if resultado.get("intencao") not in VALID_INTENTS:

        resultado["intencao"] = "conversar"

        resultado["linguagem"] = None

        resultado["nome"] = None

        resultado["confianca"] = 0.0

        resultado["motivo"] = (
            "Intenção inválida; fallback seguro "
            "para conversa."
        )

    # --------------------------------------------------------
    # GARANTIA DO LIMITE DE NOME
    # --------------------------------------------------------

    if resultado.get("nome"):

        resultado["nome"] = normalizar_nome(
            resultado["nome"]
        )

        resultado["nome_maximo"] = MAX_NOME

    # --------------------------------------------------------
    # MEMÓRIA LOCAL
    # --------------------------------------------------------

    registrar_memoria_local(
        resultado
    )

    # --------------------------------------------------------
    # FIREBASE
    # --------------------------------------------------------

    firebase_ok = sincronizar_firebase(
        resultado
    )

    resultado["firebase_sync"] = firebase_ok

    # --------------------------------------------------------
    # SAÍDA ÚNICA JSON
    # --------------------------------------------------------

    print(
        json.dumps(
            resultado,
            ensure_ascii=False
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
