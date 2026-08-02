

from pathlib import Path
import shutil
from datetime import datetime

BASE = Path.home() / "sentinela_dev"

BACKUPS = BASE / "backups"

BACKUPS.mkdir(exist_ok=True)

def backup(arquivo):

    arq = Path(arquivo)

    if not arq.exists():
        return None

    destino = BACKUPS / (
        arq.name +
        "." +
        datetime.now().strftime("%Y%m%d_%H%M%S") +
        ".bak"
    )

    shutil.copy2(arq, destino)

    print("Backup:", destino.name)

    return destino


def restaurar(backup_file, destino):

    shutil.copy2(
        backup_file,
        destino
    )

    print("Restaurado:", destino)


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print(" rollback.py backup arquivo")
        print(" rollback.py restore backup destino")
        raise SystemExit

    if sys.argv[1] == "backup":
        backup(sys.argv[2])

    elif sys.argv[1] == "restore":
        restaurar(
            sys.argv[2],
            sys.argv[3]
        )
