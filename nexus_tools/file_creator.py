from pathlib import Path
import sys
from pathlib import Path as _Path

ROOT_IMPORT = _Path(__file__).resolve().parent.parent

if str(ROOT_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_IMPORT))

from nexus_tools.firebase_storage import salvar_arquivo
import sys
import json
import subprocess
import ast
import re

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "nexus_tools"
SKILLS = ROOT / "skills.json"

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
                    encontrados.append(node.func.id)

            if isinstance(node.func, ast.Attribute):

                nome = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"

                if nome in proibidos:
                    encontrados.append(nome)

    if encontrados:
        return (
            False,
            "Operações proibidas encontradas: "
            + ", ".join(encontrados)
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
        return False, teste.stderr.strip()

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


def criar_tool(
    nome,
    descricao,
    frases,
    codigo_python
):

    nome = normalizar_nome_tool(nome)

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

    conteudo = "Arquivo criado pelo Nexus.\n"

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

    modo = args[0]

    if modo == "criar_tool":

        if len(args) < 5:
            print(
                "Uso: criar_tool "
                "nome descricao frases codigo"
            )
            raise SystemExit(1)

        nome = args[1]
        descricao = args[2]

        frases = [
            x.strip()
            for x in args[3].split(",")
            if x.strip()
        ]

        codigo = args[4]

        sucesso = criar_tool(
            nome,
            descricao,
            frases,
            codigo
        )

        if not sucesso:
            raise SystemExit(1)

    elif modo == "arquivo":

        nome = (
            args[1]
            if len(args) > 1
            else "usuario.txt"
        )

        criar_arquivo(nome)

    else:

        print(
            "Modo desconhecido:",
            modo
        )


if __name__ == "__main__":
    main()
