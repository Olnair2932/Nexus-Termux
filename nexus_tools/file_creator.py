#!/usr/bin/env python3

from pathlib import Path
import sys
import json
import subprocess
import ast
import re
import os
import urllib.request
import urllib.error
import time

ROOT_IMPORT = Path(__file__).resolve().parent.parent

if str(ROOT_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_IMPORT))

from nexus_tools.firebase_storage import salvar_arquivo


ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "nexus_tools"
SKILLS = ROOT / "skills.json"

MODEL = "gemini-3.1-flash-lite"


# O Nexus pode criar ferramentas novas, mas não pode sobrescrever
# componentes críticos do próprio núcleo.
BLOQUEADOS = {
    "server",
    "command_router",
    "file_creator",
    "auto_skill_generator",
    "rollback",
    "backup_checker",
}


def carregar_skills():
    if not SKILLS.exists():
        return {"skills": {}}

    try:
        return json.loads(
            SKILLS.read_text(encoding="utf-8")
        )

    except Exception:
        return {"skills": {}}


def salvar_skills(dados):
    SKILLS.write_text(
        json.dumps(
            dados,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def normalizar_nome_tool(nome):
    nome = str(nome).lower().strip()

    nome = re.sub(
        r"[^a-z0-9_]+",
        "_",
        nome
    )

    nome = re.sub(
        r"_+",
        "_",
        nome
    ).strip("_")

    if not nome:
        nome = "nova_ferramenta"

    if nome[0].isdigit():
        nome = "tool_" + nome

    if nome in BLOQUEADOS:
        nome = "tool_" + nome

    return nome[:80]


def validar_codigo(codigo):
    """
    Validação estrutural antes de registrar a ferramenta.
    """

    try:
        arvore = ast.parse(codigo)

    except SyntaxError as e:
        return False, f"Erro de sintaxe: {e}"

    proibidos = {
        "os.system",
        "subprocess.Popen",
        "subprocess.call",
        "eval",
        "exec",
        "compile",
    }

    encontrados = []

    for node in ast.walk(arvore):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id in {
                    "eval",
                    "exec",
                    "compile",
                }:
                    encontrados.append(
                        node.func.id
                    )

            if isinstance(node.func, ast.Attribute):

                nome = (
                    f"{getattr(node.func.value, 'id', '')}."
                    f"{node.func.attr}"
                )

                if nome in proibidos:
                    encontrados.append(nome)

    if encontrados:

        return (
            False,
            "Operações proibidas encontradas: "
            + ", ".join(sorted(set(encontrados)))
        )

    return True, "Código estruturalmente válido."


def testar_codigo(script):

    teste = subprocess.run(
        [
            "python3",
            "-m",
            "py_compile",
            str(script)
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True
    )

    if teste.returncode != 0:

        return (
            False,
            teste.stderr.strip()
        )

    return True, "py_compile aprovado."


def registrar_skill(nome, descricao, frases):

    dados = carregar_skills()

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

    salvar_skills(dados)


def gerar_codigo_gemini(
    nome,
    descricao,
    frases
):
    """
    Gera a implementação Python da ferramenta usando Gemini.
    """

    api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "variável GEMINI_API_KEY não encontrada."
        )

    prompt = f"""
Você é o arquiteto de ferramentas Python do Nexus.

Crie uma ferramenta Python REAL, COMPLETA e FUNCIONAL.

NOME DA FERRAMENTA:
{nome}

DESCRIÇÃO:
{descricao}

FRASES DE ATIVAÇÃO:
{", ".join(frases)}

REGRAS OBRIGATÓRIAS:

1. Responda SOMENTE com código Python.
2. Não use Markdown.
3. Não use ```python.
4. O código deve funcionar com Python 3.
5. A implementação deve realmente executar a finalidade solicitada.
6. Não use placeholders.
7. Não use TODO como substituto da implementação.
8. Não gere código fictício.
9. Não modifique server.js.
10. Não modifique file_creator.py.
11. Não modifique skills.json diretamente.
12. Não instale pacotes.
13. Prefira a biblioteca padrão do Python.
14. Não use eval().
15. Não use exec().
16. Não use compile().
17. Não use os.system().
18. Não use subprocess.Popen().
19. Não use subprocess.call().
20. Não execute comandos arbitrários do sistema.
21. Não tente obter ou expor GEMINI_API_KEY.
22. Não inclua nenhuma chave ou segredo no código.
23. Use variáveis de ambiente somente quando uma integração externa for realmente necessária.
24. Trate erros de entrada.
25. Produza mensagens úteis no terminal.
26. A ferramenta deve possuir um ponto de entrada:

if __name__ == "__main__":
    ...

27. Use sys.argv quando a ferramenta precisar receber argumentos.
28. Mantenha a implementação simples e robusta.
29. Não explique o código fora do código Python.
30. O código será validado por AST e py_compile antes de ser aceito.

IMPORTANTE:

A ferramenta será salva automaticamente pelo Nexus em:

nexus_tools/{nome}.py

Você deve retornar SOMENTE o conteúdo desse arquivo.

OBJETIVO:
Implementar exatamente:

{descricao}
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
        "?key=" + api_key
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192
        }
    }

    dados = json.dumps(
        payload
    ).encode("utf-8")

    requisicao = urllib.request.Request(
        url,
        data=dados,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    resultado = None

    for tentativa in range(1, 4):

        try:

            print(
                f"🤖 Gemini Tool Generator "
                f"{tentativa}/3..."
            )

            with urllib.request.urlopen(
                requisicao,
                timeout=90
            ) as resposta:

                resultado = json.loads(
                    resposta.read().decode("utf-8")
                )

            break

        except urllib.error.HTTPError as erro:

            corpo = erro.read().decode(
                "utf-8",
                errors="replace"
            )

            if (
                erro.code == 503
                and tentativa < 3
            ):

                espera = tentativa * 5

                print(
                    f"⚠️ Gemini indisponível (503). "
                    f"Nova tentativa em {espera}s..."
                )

                time.sleep(espera)

                continue

            raise RuntimeError(
                f"Erro HTTP Gemini {erro.code}: "
                f"{corpo}"
            )

        except Exception as erro:

            if tentativa >= 3:
                raise RuntimeError(
                    f"Erro ao chamar Gemini: {erro}"
                )

            print(
                f"⚠️ Falha Gemini: {erro}"
            )

            time.sleep(
                tentativa * 2
            )

    if resultado is None:

        raise RuntimeError(
            "Gemini não retornou resultado."
        )

    try:

        codigo = (
            resultado["candidates"][0]
            ["content"]["parts"][0]["text"]
            .strip()
        )

    except (
        KeyError,
        IndexError,
        TypeError
    ):

        raise RuntimeError(
            "Gemini não retornou código Python válido."
        )

    # Remove cercas Markdown caso o modelo envie.
    if codigo.startswith("```"):

        linhas = codigo.splitlines()

        if (
            linhas
            and linhas[0].strip().startswith("```")
        ):
            linhas = linhas[1:]

        if (
            linhas
            and linhas[-1].strip() == "```"
        ):
            linhas = linhas[:-1]

        codigo = "\n".join(
            linhas
        ).strip()

    if not codigo:

        raise RuntimeError(
            "Gemini retornou código vazio."
        )

    return codigo


def criar_tool(
    nome,
    descricao,
    frases,
    codigo_python=None
):

    nome = normalizar_nome_tool(
        nome
    )

    if nome in BLOQUEADOS:

        print(
            f"❌ Ferramenta protegida: {nome}"
        )

        return False

    TOOLS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    script = TOOLS_DIR / f"{nome}.py"

    if script.exists():

        print(
            f"⚠️ Ferramenta já existe: {nome}"
        )

        return False

    # Quando solicitado pelo Nexus, o código é gerado
    # diretamente pelo Gemini.
    if (
        codigo_python is None
        or codigo_python == "__GERAR_COM_GEMINI__"
    ):

        print(
            "🤖 Gerando implementação com Gemini..."
        )

        try:

            codigo_python = gerar_codigo_gemini(
                nome,
                descricao,
                frases
            )

        except Exception as erro:

            print(
                "❌ Falha no Gemini:",
                erro
            )

            return False

    if not isinstance(
        codigo_python,
        str
    ):

        print(
            "❌ Código da ferramenta inválido."
        )

        return False

    # Primeira validação.
    valido, mensagem = validar_codigo(
        codigo_python
    )

    if not valido:

        print(
            "❌ Ferramenta rejeitada:",
            mensagem
        )

        return False

    # Escreve somente depois da validação.
    script.write_text(
        codigo_python,
        encoding="utf-8"
    )

    # Segunda validação: compilação real.
    sucesso, resultado = testar_codigo(
        script
    )

    if not sucesso:

        try:
            script.unlink()

        except Exception:
            pass

        print(
            "❌ Ferramenta removida após falha:",
            resultado
        )

        return False

    registrar_skill(
        nome,
        descricao,
        frases
    )

    print(
        "========================================"
    )

    print(
        "✅ NEXUS TOOL ARCHITECT"
    )

    print(
        "========================================"
    )

    print(
        "Ferramenta:",
        nome
    )

    print(
        "Descrição:",
        descricao
    )

    print(
        "Script:",
        script
    )

    print(
        "Validação:",
        resultado
    )

    print(
        "Skill registrada:",
        nome
    )

    print(
        "========================================"
    )

    return True


def criar_arquivo(nome):

    arquivo = ROOT / nome

    conteudo = (
        "Arquivo criado pelo Nexus.\n"
    )

    arquivo.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo.write_text(
        conteudo,
        encoding="utf-8"
    )

    try:

        salvar_arquivo(
            nome,
            conteudo
        )

        print(
            "Arquivo criado:",
            arquivo
        )

        print(
            "☁️ Arquivo persistido no Firebase:",
            nome
        )

    except Exception as erro:

        print(
            "⚠️ Arquivo criado localmente, "
            "mas não foi possível salvar no Firebase:",
            erro
        )


def main():

    args = sys.argv[1:]

    if not args:

        print(
            "Uso:"
        )

        print(
            "  file_creator.py criar_tool "
            "nome descricao frases codigo"
        )

        print(
            "  file_creator.py arquivo nome"
        )

        return

    comando = args[0]

    if comando == "criar_tool":

        if len(args) < 5:

            print(
                "❌ Uso inválido:"
            )

            print(
                "file_creator.py criar_tool "
                "nome descricao frases codigo"
            )

            return

        nome = args[1]
        descricao = args[2]
        frases = args[3]

        codigo_python = " ".join(
            args[4:]
        )

        frases_lista = [
            item.strip()
            for item in frases.split(",")
            if item.strip()
        ]

        sucesso = criar_tool(
            nome,
            descricao,
            frases_lista,
            codigo_python
        )

        if not sucesso:
            raise SystemExit(1)

        return

    if comando == "arquivo":

        if len(args) < 2:

            print(
                "❌ Nome do arquivo não informado."
            )

            raise SystemExit(1)

        criar_arquivo(
            args[1]
        )

        return

    print(
        f"❌ Comando desconhecido: {comando}"
    )


if __name__ == "__main__":
    main()
