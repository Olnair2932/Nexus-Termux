from pathlib import Path

arquivo = Path("server.js")

texto = arquivo.read_text(encoding="utf-8")

alvo = """    await syncBrain(); // Carrega o cérebro
"""

novo = """    console.log("🧬 Carregando evolução Nexus...");

    try {
        const { execSync } = require("child_process");

        const evolucao = execSync(
            "python3 -m nexus_tools.evolution_loader",
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8"
            }
        );

        console.log(evolucao);

    } catch(e) {
        console.log(
            "Evolution Loader:",
            e.message
        );
    }

    await syncBrain(); // Carrega o cérebro
"""

if "python3 -m nexus_tools.evolution_loader" in texto:
    print("Evolution Loader já integrado.")
else:
    if alvo not in texto:
        print("Ponto de inserção não encontrado.")
    else:
        texto = texto.replace(alvo, novo)
        arquivo.write_text(texto, encoding="utf-8")
        print("Evolution Loader integrado no bootstrap.")

