

from pathlib import Path
from datetime import datetime
import json

BASE = Path.home() / "sentinela_dev"

def gerar_readme():
    registro = BASE / "tools_registry.json"

    ferramentas = []

    if registro.exists():
        dados = json.loads(registro.read_text(encoding="utf-8"))
        ferramentas = dados.get("tools", [])

    texto = f"""# Nexus Core - README Interno

Versão: 1.0

Última atualização:
{datetime.now().isoformat()}

## Status

Sistema operacional.

## Recursos

- Sincronização
- Logs
- Memória
- Auditoria
- Backup
- Rollback
- Validação de sintaxe
- Autocorreção controlada
- Otimização de dashboard
- Histórico de evolução

## Ferramentas registradas

"""

    for ferramenta in ferramentas:
        texto += f"- {ferramenta['nome']} -> {ferramenta['objetivo']} ({ferramenta['status']})\n"

    texto += """

## Política de segurança

- Alterações somente no workspace
- Backup antes de aplicar mudanças
- Testes antes da publicação
- Todas as ações registradas em logs

## Evolução

O Nexus registra sugestões, aprovações e melhorias aplicadas.

"""

    arquivo = BASE / "README_NEXUS.md"
    arquivo.write_text(texto, encoding="utf-8")

    print("✅ README_NEXUS.md atualizado.")


if __name__ == "__main__":
    gerar_readme()
