

import subprocess

def consultar(comando):

    testes = [
        [comando, "--help"],
        ["man", comando],
    ]

    for cmd in testes:
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            texto = (r.stdout + "\n" + r.stderr).strip()

            if texto:
                return texto[:3000]

        except Exception:
            pass

    return None


if __name__ == "__main__":
    import sys

    print(consultar(sys.argv[1]) or "Nada encontrado.")
