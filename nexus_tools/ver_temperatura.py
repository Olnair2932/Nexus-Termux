
import subprocess
import json

def main():
    try:
        dados = json.loads(
            subprocess.check_output(
                ["termux-battery-status"],
                encoding="utf-8"
            )
        )

        temperatura = dados.get("temperature", "N/A")
        bateria = dados.get("percentage", "N/A")
        status = dados.get("status", "N/A")
        conectado = dados.get("plugged", "N/A")
        saude = dados.get("health", "N/A")

        print(f"🌡️ Temperatura: {temperatura}°C")
        print(f"🔋 Bateria: {bateria}%")
        print(f"⚡ Status: {status}")
        print(f"🔌 Conexão: {conectado}")
        print(f"❤️ Saúde: {saude}")

    except Exception as e:
        print("Erro ao consultar temperatura:", e)

if __name__ == "__main__":
    main()
