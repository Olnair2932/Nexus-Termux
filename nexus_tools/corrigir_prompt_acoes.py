#!/usr/bin/env python3

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.js"
SKILLS = ROOT / "skills.json"

server = SERVER.read_text(encoding="utf-8")
dados = __import__("json").loads(SKILLS.read_text(encoding="utf-8"))

skills = dados.get("skills", {})

# Algumas entradas são ferramentas internas/backups e não devem
# ser apresentadas ao Gemini como ações principais.
ignorar = {
    "conversar",
}

acoes = sorted(
    nome for nome in skills
    if nome not in ignorar
)

lista = "\n".join(f"- {nome}" for nome in acoes)

novo_bloco = f"""AÇÕES VÁLIDAS

As ações são carregadas dinamicamente de skills.json.

Use SOMENTE uma das ações abaixo:

{lista}

Não invente outras ações."""

padrao = re.compile(
    r'AÇÕES VÁLIDAS\s+'
    r'Use SOMENTE estas ações:\s+'
    r'(?:-\s*[^\n]+\s*)+'
    r'Não invente outras ações\.',
    re.MULTILINE
)

novo_server, quantidade = padrao.subn(novo_bloco, server, count=1)

if quantidade != 1:
    print("❌ Não foi possível localizar o bloco AÇÕES VÁLIDAS.")
    print("Nenhuma alteração foi feita.")
    raise SystemExit(1)

backup = SERVER.with_name("server.js.backup_antes_prompt_dinamico")
backup.write_text(server, encoding="utf-8")

SERVER.write_text(novo_server, encoding="utf-8")

print("====================================")
print(" PROMPT DE AÇÕES DINÂMICO")
print("====================================")
print(f"Ações carregadas: {len(acoes)}")
print(f"Backup criado: {backup.name}")
print("server.js atualizado.")
print()
print("Primeiras ações:")
for nome in acoes[:10]:
    print(" +", nome)
print()
print("====================================")
