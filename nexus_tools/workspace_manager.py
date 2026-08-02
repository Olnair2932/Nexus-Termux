

from pathlib import Path
import shutil

BASE = Path.home() / "sentinela_dev"

ORIGENS = [
    BASE / "server.js",
    BASE / "public/index.html",
]

ORIGENS += list((BASE / "nexus_tools").glob("*.py"))

DESTINO = BASE / "workspace"

def sincronizar():

    copiados = 0

    for arq in ORIGENS:

        if not arq.exists():
            continue

        if arq.suffix == ".py":
            pasta = DESTINO / "python"

        elif arq.suffix == ".js":
            pasta = DESTINO / "javascript"

        elif arq.suffix == ".html":
            pasta = DESTINO / "html"

        else:
            pasta = DESTINO / "temp"

        pasta.mkdir(parents=True, exist_ok=True)

        shutil.copy2(
            arq,
            pasta / arq.name
        )

        copiados += 1

    print(f"✅ {copiados} arquivos sincronizados para o Workspace.")


if __name__ == "__main__":
    sincronizar()
