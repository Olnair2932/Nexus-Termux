

import subprocess
from pathlib import Path

BASE = Path(__file__).parent

print("=== SELF IMPROVE ===")

etapas = [
    ("Sincronizando Workspace",
     ["python3", str(BASE / "workspace_manager.py")]),

    ("Executando testes",
     ["python3", str(BASE / "test_runner.py")]),
]

for nome, comando in etapas:

    print("\\n>>", nome)

    r = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    print(r.stdout)

    if r.returncode != 0:

        print("Falhou:")
        print(r.stderr)

        raise SystemExit(1)

print("\\n✅ Sistema pronto para autoevolução.")
