

from pathlib import Path
from datetime import datetime
import json

BASE = Path.home() / "sentinela_dev"

def atualizar_versao():
    arquivo = BASE / "version.json"

    dados = {
        "nome": "Nexus Core",
        "versao_atual": "1.0",
        "proxima_versao": "1.1",
        "status": "desenvolvimento_continuo",
        "ultima_atualizacao": datetime.now().isoformat(),
        "melhorias": [
            "README interno automático",
            "Sistema de sugestões",
            "Histórico de evolução"
        ]
    }

    arquivo.write_text(
        json.dumps(dados, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    changelog = BASE / "CHANGELOG_NEXUS.md"

    texto = f"""# Nexus Core Changelog

## Versão 1.0

Data:
{datetime.now().isoformat()}

### Adicionado

- Gerenciamento de ferramentas
- Auditoria automática
- Sincronização de workspace
- Autocorreção controlada
- Sistema de sugestões
- Documentação automática

### Próxima versão

1.1

Planejado:
- Melhorias no dashboard
- Novos módulos de manutenção
- Evolução controlada
"""

    changelog.write_text(texto, encoding="utf-8")

    print("✅ Sistema de versão atualizado.")
    print("✅ CHANGELOG_NEXUS.md criado.")


if __name__ == "__main__":
    atualizar_versao()
