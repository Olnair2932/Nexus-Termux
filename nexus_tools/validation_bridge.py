import json
import subprocess
import sys

def validar_melhoria():

    try:
        resultado = subprocess.run(
            [
                sys.executable,
                "-m",
                "nexus_tools.improvement_validator"
            ],
            capture_output=True,
            text=True
        )

        dados = json.loads(resultado.stdout)

        return dados.get("status") == "OK"

    except Exception as e:
        return False


if __name__ == "__main__":
    print(validar_melhoria())
