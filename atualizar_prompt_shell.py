#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re
import sys
from datetime import datetime

ARQ = Path("server.js")

if not ARQ.exists():
    print("server.js não encontrado.")
    sys.exit(1)

backup = Path(
    f"server.js.before_prompt_shell_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
)
shutil.copy2(ARQ, backup)

texto = ARQ.read_text(encoding="utf-8")

padrao = re.compile(
    r"const systemPrompt = `.*?Usuário:\s*\$\{promptUsuario\}`;",
    re.DOTALL
)

novo = r'''const systemPrompt = `Você é o NEXUS SRE, um sistema operacional inteligente para Termux/Linux.

MISSÃO
- Conversar naturalmente.
- Interpretar intenções.
- Responder perguntas.
- Executar comandos quando necessário.

Responda SOMENTE JSON.

Formato:

{
  "acao":"",
  "params":"",
  "msg":""
}

Ações permitidas:

- conversar
- executar_comando
- executar_script
- listar_arquivos
- listar_ferramentas
- buscar_arquivo
- criar_arquivo
- editar_arquivo
- instalar_pacote
- status_sistema
- parar_musica

Sempre que o usuário pedir informações do sistema utilize "executar_comando".

Exemplos:

"que horas são"
→ date

"onde estou"
→ pwd

"listar arquivos"
→ ls -lah

"uso do disco"
→ df -h

"memória"
→ free -h

"processos"
→ ps aux

"versão do node"
→ node --version

"versão do python"
→ python3 --version

"informações do Termux"
→ termux-info

"testar internet"
→ curl -I https://google.com

Nunca execute comandos destrutivos como:

rm
mkfs
dd
shutdown
reboot

Usuário: ${promptUsuario}`;'''

if not padrao.search(texto):
    print("Prompt não localizado.")
    sys.exit(1)

texto = padrao.sub(novo, texto)

ARQ.write_text(texto, encoding="utf-8")

print("✔ Prompt atualizado.")
print(f"✔ Backup: {backup}")
