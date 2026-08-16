#!/usr/bin/env python3

from pathlib import Path

ROOT = Path.home() / "sentinela_dev"
SERVER = ROOT / "server.js"

texto = SERVER.read_text(encoding="utf-8")

marcador = """default:
        try {
            const { execSync } = require("child_process");

            let acaoRouter = intent.acao;
"""

if marcador not in texto:
    print("❌ Bloco default não encontrado.")
    raise SystemExit(1)

novo = """default:

        // ============================================================
        // EXECUTOR DINÂMICO DE SKILLS
        // ============================================================
        // Qualquer ação existente em skills.json pode ser executada
        // sem precisar criar um novo case no switch.
        // ============================================================

        try {
            const fs = require("fs");
            const path = require("path");
            const { execSync } = require("child_process");

            const skillsFile = path.join(
                CONFIG.ROOT,
                "skills.json"
            );

            const dadosSkills = JSON.parse(
                fs.readFileSync(
                    skillsFile,
                    "utf8"
                )
            );

            const skillsDinamicas =
                dadosSkills.skills || {};

            const skillDinamica =
                skillsDinamicas[intent.acao];

            if (skillDinamica) {

                console.log(
                    "🔧 EXECUTOR DINÂMICO:",
                    intent.acao
                );

                const executor =
                    skillDinamica.executor;

                if (executor === "python") {

                    if (!skillDinamica.script) {
                        respostaFinal =
                            "Skill sem script: " +
                            intent.acao;
                        break;
                    }

                    const script =
                        path.resolve(
                            CONFIG.ROOT,
                            skillDinamica.script
                        );

                    const pastaFerramentas =
                        path.resolve(
                            CONFIG.ROOT,
                            "nexus_tools"
                        );

                    if (
                        !script.startsWith(
                            pastaFerramentas +
                            path.sep
                        )
                    ) {
                        respostaFinal =
                            "Execução bloqueada.";
                        break;
                    }

                    if (!fs.existsSync(script)) {
                        respostaFinal =
                            "Script inexistente: " +
                            skillDinamica.script;
                        break;
                    }

                    const parametros =
                        intent.params || "";

                    const argumentos =
                        parametros.trim()
                            ? " " +
                              JSON.stringify(
                                  parametros.trim()
                              )
                            : "";

                    console.log(
                        "🐍 Executando Python:",
                        skillDinamica.script
                    );

                    respostaFinal =
                        execSync(
                            `python3 "${script}"${argumentos}`,
                            {
                                cwd: CONFIG.ROOT,
                                encoding: "utf8",
                                maxBuffer:
                                    1024 * 1024
                            }
                        ).trim();

                    console.log(
                        "✅ Skill dinâmica executada:",
                        intent.acao
                    );

                    break;
                }

                if (executor === "bash") {

                    if (
                        !skillDinamica.comando
                    ) {
                        respostaFinal =
                            "Skill bash sem comando: " +
                            intent.acao;
                        break;
                    }

                    respostaFinal =
                        execSync(
                            skillDinamica.comando,
                            {
                                cwd: CONFIG.ROOT,
                                encoding: "utf8",
                                maxBuffer:
                                    1024 * 1024
                            }
                        ).trim();

                    console.log(
                        "✅ Skill Bash executada:",
                        intent.acao
                    );

                    break;
                }

                respostaFinal =
                    "Executor não suportado: " +
                    executor;

                break;
            }

            // ========================================================
            // COMPORTAMENTO ORIGINAL DO DEFAULT
            // ========================================================

            const { execSync } = require("child_process");

            let acaoRouter = intent.acao;
"""

texto = texto.replace(
    marcador,
    novo,
    1
)

SERVER.write_text(
    texto,
    encoding="utf-8"
)

print("====================================")
print(" EXECUTOR DINÂMICO DO NEXUS")
print("====================================")
print("server.js atualizado.")
print()
print("Skills Python agora podem ser")
print("executadas diretamente pela ação.")
print()
print("Exemplo:")
print("  teste_tool")
print("  -> nexus_tools/teste_tool.py")
print("====================================")
