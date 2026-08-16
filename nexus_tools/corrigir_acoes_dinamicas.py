#!/usr/bin/env python3

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.js"

texto = SERVER.read_text(encoding="utf-8")

inicio = texto.find("// Normalização de ações inválidas")
if inicio == -1:
    print("ERRO: bloco de acoesValidas não encontrado.")
    raise SystemExit(1)

fim = texto.find("// Lógica de Ação", inicio)
if fim == -1:
    print("ERRO: final do bloco de ações não encontrado.")
    raise SystemExit(1)

novo_bloco = r'''// Normalização de ações válidas
// As skills registradas em skills.json são automaticamente aceitas.
// Isso evita manter manualmente uma lista limitada de ações.

let acoesValidas;

try {
    const fs = require("fs");
    const caminhoSkills = path.join(CONFIG.ROOT, "skills.json");

    const dadosSkills = JSON.parse(
        fs.readFileSync(caminhoSkills, "utf8")
    );

    acoesValidas = new Set(
        Object.keys(dadosSkills.skills || {})
    );

    // Ação interna de conversa
    acoesValidas.add("conversar");

    console.log(
        `✅ Ações carregadas dinamicamente: ${acoesValidas.size}`
    );

} catch (erro) {

    console.log(
        "⚠️ Não foi possível carregar skills.json:",
        erro.message
    );

    // Fallback mínimo
    acoesValidas = new Set([
        "conversar",
        "executar_comando",
        "executar_script"
    ]);
}

if (!acoesValidas.has(intent.acao)) {

    console.log("⚠️ Ação desconhecida:", intent.acao);

    try {
        const { registrar } = require("./nexus_tools/logger");

        registrar(
            "ERRO",
            `Ação desconhecida: ${intent.acao}`
        );

    } catch (e) {

        console.log(
            "Falha ao registrar log:",
            e.message
        );
    }

    if (intent.msg && intent.msg.trim()) {

        respostaFinal = intent.msg;

        intent.acao = "conversar";
        intent.params = intent.params || "";

        return res.json({
            nexus: respostaFinal,
            intent,
            shell: execResult
        });
    }

    intent.acao = "conversar";
}

'''

texto = texto[:inicio] + novo_bloco + texto[fim:]

SERVER.write_text(texto, encoding="utf-8")

print("====================================")
print(" CORREÇÃO DE AÇÕES DO NEXUS")
print("====================================")
print("server.js atualizado.")
print("As ações agora serão carregadas")
print("automaticamente de skills.json.")
print("====================================")
