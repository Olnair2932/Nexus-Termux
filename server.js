require("dotenv").config();

const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');
const fsp = require('fs').promises;
const { exec } = require('child_process');
const { execSync } = require("child_process");

function registrarAprendizado(frase, acao) {
    try {
        execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/learning_memory.py`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8"
            }
        );
    } catch(e) {
        console.log("Memória:", e.message);
    }
}


const fs = require('fs');
const { initializeApp, cert } = require("firebase-admin/app");
const { getDatabase } = require("firebase-admin/database");




// ==========================================
// FIREBASE REALTIME DATABASE
// ==========================================


let db = null;


async function buscarConhecimentoFirebase(termo) {

    if (!db) {
        return "";
    }

    try {

        const snapshot = await db
            .ref("nexus/conhecimento")
            .once("value");

        const dados = snapshot.val();

        if (!dados) {
            return "";
        }

        const palavras = termo
            .toLowerCase()
            .split(/\s+/)
            .filter(p => p.length > 2);

        for (const nome in dados) {

            if (palavras.some(p => nome.toLowerCase().includes(p))) {

                console.log(
                    "Memória Firebase encontrada:",
                    nome
                );

                return dados[nome].conteudo || "";
            }
        }

        return "";

    } catch(e) {

        console.log(
            "Erro memória Firebase:",
            e.message
        );

        return "";
    }
}


// ============================================================
// SALVAR HTML GERADO NO FIREBASE REALTIME
// ============================================================

async function salvarHTMLFirebase(arquivo, prompt = "", modelo = "gemini-3.1-flash-lite") {

    if (!db) {
        console.log("Firebase indisponível para HTML.");
        return null;
    }

    try {

        const conteudo = fs.readFileSync(
            arquivo,
            "utf8"
        );

        const nome = path.basename(
            arquivo,
            ".html"
        );

        const dados = {
            titulo: nome,
            prompt: prompt,
            html: conteudo,
            arquivo_local: arquivo,
            modelo: modelo,
            criado_em: new Date().toISOString()
        };

        await db
            .ref("nexus/html_gerados/" + nome)
            .set(dados);

        console.log(
            "HTML salvo no Firebase:",
            "nexus/html_gerados/" + nome
        );

        return nome;

    } catch (e) {

        console.log(
            "Erro Firebase HTML:",
            e.message
        );

        return null;
    }
}


// ============================================================
// SALVAR NOVA VERSÃO DE HTML EDITADO NO FIREBASE
// ============================================================

async function salvarHTMLEditadoFirebase(nome, html, prompt = "") {
    if (!db) {
        console.log("Firebase indisponível para HTML editado.");
        return null;
    }

    try {
        const nomeLimpo = path.basename(nome, ".html");

        const dados = {
            titulo: nomeLimpo,
            prompt: prompt,
            html: html,
            arquivo_local: "",
            modelo: "gemini-3.1-flash-lite",
            tipo: "html_editado",
            original: nomeLimpo,
            criado_em: new Date().toISOString()
        };

        const novoNome =
            "nexus_editado_" +
            new Date().toISOString()
                .replace(/[-:TZ.]/g, "")
                .slice(0, 15);

        await db
            .ref("nexus/html_gerados/" + novoNome)
            .set(dados);

        console.log(
            "HTML editado salvo no Firebase:",
            "nexus/html_gerados/" + novoNome
        );

        return novoNome;

    } catch (e) {
        console.log(
            "Erro ao salvar HTML editado no Firebase:",
            e.message
        );
        return null;
    }
}

// ============================================================
// BUSCAR HTML GERADO NO FIREBASE REALTIME
// ============================================================

async function buscarHTMLFirebase(nome) {
    if (!db) {
        console.log("Firebase indisponível para HTML.");
        return null;
    }

    try {
        const nomeLimpo = path.basename(nome, ".html");

        const snapshot = await db
            .ref("nexus/html_gerados/" + nomeLimpo)
            .once("value");

        const dados = snapshot.val();

        if (!dados || !dados.html) {
            console.log("HTML não encontrado no Firebase:", nomeLimpo);
            return null;
        }

        console.log(
            "HTML recuperado do Firebase:",
            nomeLimpo
        );

        return {
            nome: nomeLimpo,
            html: dados.html,
            dados: dados
        };

    } catch (e) {
        console.log(
            "Erro ao buscar HTML no Firebase:",
            e.message
        );
        return null;
    }
}

async function salvarConhecimentoFirebase(arquivo) {

    if (!db) {
        console.log("Firebase indisponível.");
        return;
    }

    try {

        const conteudo = fs.readFileSync(
            arquivo,
            "utf8"
        );

        const nome = path.basename(
            arquivo,
            ".md"
        );

        await db
            .ref("nexus/conhecimento/" + nome)
            .set({
                arquivo,
                conteudo,
                atualizado_em: new Date().toISOString()
            });

        console.log(
            "Conhecimento salvo no Firebase:",
            nome
        );

    } catch(e) {

        console.log(
            "Erro Firebase conhecimento:",
            e.message
        );

    }
}


async function carregarMemoriaFirebase() {
    if (!db) return;

    try {
        const snapshot = await db.ref("nexus/memoria").once("value");
        const memoria = snapshot.val();

        if (!memoria) {
            console.log("Memória Firebase vazia.");
            return;
        }

        fs.writeFileSync(
            CONFIG.BRAIN_FILE,
            JSON.stringify(memoria, null, 2),
            "utf8"
        );

        console.log("🧠 Memória carregada do Firebase.");
    } catch(e) {
        console.log("Erro ao carregar memória:", e.message);
    }
}


async function sincronizarMemoriaFirebase() {
    if (!db) return;

    try {
        const memoria = fs.readFileSync(
            CONFIG.BRAIN_FILE,
            "utf8"
        );

        await db
            .ref("nexus/memoria")
            .set(JSON.parse(memoria));

        console.log("Memória sincronizada com Firebase.");
    } catch(e) {
        console.log("Erro sincronizar memória:", e.message);
    }
}

if (process.env.private_key) {

    const serviceAccount = JSON.parse(process.env.private_key);

    initializeApp({
        credential: cert(serviceAccount),
        databaseURL: "https://finance-master-629d1-default-rtdb.firebaseio.com"
    });

    db = getDatabase();

    console.log("Firebase Realtime conectado.");

} else {

    console.log("Firebase desabilitado (Termux/local).");

}

// ==========================================

// --- CONFIGURAÇÃO ---
const CONFIG = {
    PORT: 3003,
    ROOT: __dirname,
    BRAIN_FILE: path.join(__dirname, "brain.json"),
};


function detectarAmbiente() {
    try {
        const resultado = execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/detectar_ambiente.py`,
            {
                encoding: "utf8"
            }
        );

        return JSON.parse(resultado);

    } catch(e) {
        console.log("Falha detector ambiente:", e.message);

        return {
            ambiente: "linux",
            root: process.cwd()
        };
    }
}

const AMBIENTE = detectarAmbiente();

console.log("[AMBIENTE]", AMBIENTE);



const intentMap = JSON.parse(
    fs.readFileSync(
        path.join(CONFIG.ROOT, "intent_map.json"),
        "utf8"
    )
);


const app = express();
app.use(cors());
app.use(express.json({ limit: '5mb' }));
app.use(express.static('public'));

// ============================================================

// ============================================================
// ÍNDICE DOS HTMLs GERADOS PELO NEXUS
// ============================================================

app.get("/html_gerados/", async (req, res) => {
    try {
        if (!db) {
            return res.status(503).send("Firebase indisponível.");
        }

        const snapshot = await db
            .ref("nexus/html_gerados")
            .once("value");

        const dados = snapshot.val() || {};

        const arquivos = Object.entries(dados)
            .sort((a, b) => {
                const da = a[1]?.criado_em || "";
                const dbb = b[1]?.criado_em || "";
                return String(dbb).localeCompare(String(da));
            });

        const cards = arquivos.map(([nome, item]) => {
            const titulo = String(item?.titulo || nome)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;");

            const data = String(item?.criado_em || "")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");

            return `
                <a class="card"
                   href="/html_gerados/${encodeURIComponent(nome)}.html">
                    <div class="card-title">${titulo}</div>
                    <div class="card-meta">${data}</div>
                    <div class="open">ABRIR PAINEL →</div>
                </a>
            `;
        }).join("");

        res.type("html").send(`<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Nexus SRE | HTMLs Gerados</title>

<style>
:root {
    --bg: #05080c;
    --panel: #0c1219;
    --border: #1e3542;
    --cyan: #00f2ff;
    --green: #00ff41;
    --text: #d9e2e8;
    --muted: #71808a;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background:
        radial-gradient(
            circle at top,
            #10202b 0,
            var(--bg) 45%
        );
    color: var(--text);
    font-family: "Courier New", monospace;
    padding: 20px;
}

header {
    max-width: 1100px;
    margin: auto;
    padding: 20px;
    border: 1px solid var(--border);
    background: var(--panel);
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 0 25px rgba(0,242,255,.08);
}

.logo {
    color: var(--cyan);
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 2px;
}

.status {
    color: var(--green);
    font-size: 13px;
}

.dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    margin-right: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 12px var(--green);
}

main {
    max-width: 1100px;
    margin: 20px auto;
}

.title {
    margin-bottom: 20px;
}

.title h1 {
    margin: 0 0 8px;
    color: var(--cyan);
}

.title p {
    margin: 0;
    color: var(--muted);
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(260px, 1fr));
    gap: 15px;
}

.card {
    display: block;
    text-decoration: none;
    color: inherit;
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 20px;
    transition: .2s;
}

.card:hover {
    border-color: var(--cyan);
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0,242,255,.12);
}

.card-title {
    color: var(--text);
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 12px;
}

.card-meta {
    color: var(--muted);
    font-size: 11px;
    margin-bottom: 18px;
}

.open {
    color: var(--cyan);
    font-size: 12px;
}

.empty {
    border: 1px dashed var(--border);
    padding: 30px;
    text-align: center;
    color: var(--muted);
}

@media (max-width: 600px) {
    body {
        padding: 10px;
    }

    header {
        padding: 15px;
    }

    .logo {
        font-size: 16px;
    }
}
</style>
</head>

<body>

<header>
    <div class="logo">
        NEXUS SRE SYSTEM
    </div>

    <div class="status">
        <span class="dot"></span>
        ONLINE
    </div>
</header>

<main>

    <div class="title">
        <h1>HTMLs GERADOS</h1>
        <p>
            Interfaces armazenadas no Firebase Realtime
        </p>
    </div>

    <div class="grid">
        ${
            cards ||
            '<div class="empty">Nenhum HTML gerado.</div>'
        }
    </div>

</main>

</body>
</html>`);

    } catch (erro) {
        console.error(
            "Erro índice HTML:",
            erro.message
        );

        res.status(500).send(
            "Erro ao carregar índice dos HTMLs."
        );
    }
});

// SERVIR HTMLs GERADOS PELO NEXUS
// ============================================================
const HTML_GERADOS_DIR = path.join(CONFIG.ROOT, "html_gerados");
app.use("/html_gerados", express.static(HTML_GERADOS_DIR));

app.get("/html_gerados/:nome", async (req, res) => {
    try {
        const nome = req.params.nome.replace(/\.html$/i, "");

        // Primeiro procura no armazenamento local
        const arquivoLocal = path.join(
            HTML_GERADOS_DIR,
            nome + ".html"
        );

        if (fs.existsSync(arquivoLocal)) {
            return res.sendFile(arquivoLocal);
        }

        // Se não existir localmente, procura no Firebase Realtime
        if (!db) {
            return res.status(503).send("Firebase indisponível.");
        }

        const snapshot = await db
            .ref("nexus/html_gerados/" + nome)
            .once("value");

        const dados = snapshot.val();

        if (!dados || !dados.html) {
            return res.status(404).send("HTML não encontrado no Firebase.");
        }

        console.log("HTML recuperado do Firebase:", nome);

        res.type("html").send(dados.html);

    } catch (erro) {
        console.error("Erro ao recuperar HTML:", erro);
        res.status(500).send("Erro ao recuperar HTML.");
    }
});


let brainMemory = null; // Cache do cérebro em memória

// --- CORE UTILS ---

/** Executa comandos shell com Promise e log */
function shell(cmd) {
    console.log(`[SHELL] Executando: ${cmd}`);
    return new Promise((resolve) => {
        const cwdAtual = execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/cwd_manager.py get`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8"
            }
        ).trim();

        exec(cmd, { cwd: cwdAtual, timeout: 120000 }, (err, stdout, stderr) => {
            resolve({
                success: !err,
                code: err ? err.code : 0,
                stdout: stdout.trim(),
                stderr: stderr.trim()
            });
        });
    });
}

/** Gerenciamento do Arquivo de Estado (Brain) */
async function syncBrain(data = null) {
    try {
        if (data) {
            brainMemory = data;
            await fsp.writeFile(CONFIG.BRAIN_FILE, JSON.stringify(data, null, 2));
        } else {
            if (!brainMemory) {
                const raw = await fsp.readFile(CONFIG.BRAIN_FILE, "utf8");
                brainMemory = JSON.parse(raw);
            }
        }
        return brainMemory;
    } catch (e) {
        brainMemory = { protocolos: {}, historico_sre: [] };
        return brainMemory;
    }
}

/** Termux TTS engine */
function falar(texto) {
    if (!texto) return;
    const limpo = texto
        .replace(/[*_#`]/g, "") // Remove markdown
        .replace(/https?:\/\/\S+/g, "link") // Simplifica URLs
        .replace(/["'$]/g, "") // Proteção de shell
        .substring(0, 500);

    exec(`termux-tts-speak "${limpo}"`);
}

// --- INTELECTO (IA) ---

/** Extrai JSON de strings mesmo se a IA incluir blocos de código markdown */
function parseIAJson(raw) {
    try {
        const match = raw.match(/\{[\s\S]*\}/);
        return match ? JSON.parse(match[0]) : null;
    } catch (e) {
        return null;
    }
}


async function registrarAprendizadoAutomatico(frase, acao) {
    console.log("DEBUG APRENDIZADO:", frase, "=>", acao);
    try {
        const fs = require("fs");
        const path = require("path");

        const brainPath = path.join(
            CONFIG.ROOT,
            "brain.json"
        );

        let brain = JSON.parse(
            fs.readFileSync(
                brainPath,
                "utf8"
            )
        );

        if (!brain.memoria_aprendizado)
            brain.memoria_aprendizado = {};

        let chave = frase
            .toLowerCase()
            .replace(/nexus[,:\s]*/g, "")
            .trim();

        if (!chave)
            return;

        let memoria =
            brain.memoria_aprendizado[chave];

        if (!memoria) {
            memoria = {
                acao: acao,
                acertos: 0,
                ultima_confirmacao: "OK"
            };
        }

        memoria.acao = acao;
        memoria.acertos += 1;
        memoria.ultima_confirmacao = "OK";

        brain.memoria_aprendizado[chave] = memoria;

        fs.writeFileSync(
            brainPath,
            JSON.stringify(
                brain,
                null,
                4
            ),
            "utf8"
        );

          await sincronizarMemoriaFirebase();

        console.log(
            "🧠 Aprendizado salvo:",
            chave,
            "->",
            acao
        );

    } catch(e) {
        console.log(
            "Erro aprendizado:",
            e.message
        );
    }
}



// ============================================================
// GATILHOS DIRETOS DO GERADOR DE CÓDIGO
// ============================================================

function detectarGerarCodigo(prompt) {
    const texto = (prompt || "")
        .toLowerCase()
        .replace(/^nexus[,:]?\s*/i, "")
        .trim();

    const gatilhos = [
        "criar uma landing page",
        "gerar uma página html",
        "criar um site",
        "fazer uma página html",
        "criar código html",
        "criar um html",
        "criar html",
        "gerar um html",
        "gerar html",
        "criar uma página web",
        "criar painel html",
        "gerar painel html",
        "criar um painel",
        "criar painel",
        "criar um painel principal",
        "painel principal do nexus",
        "criar interface do nexus",
        "criar dashboard",
        "gerar dashboard",
        "criar dashboard do nexus",
        "gerar dashboard do nexus",
        "gerar_html:",
        "gerar_html",
        "gerar html:",
        "gerar html "
    ];

    const encontrado = gatilhos.find(gatilho =>
        texto.includes(gatilho)
    );

    if (!encontrado) {
        return null;
    }

    return {
        acao: "executar_script",
        params: `gerar_codigo ${texto}`,
        msg: "Gerando código com Nexus/Gemini."
    };
}

async function processarIntencao(promptUsuario) {

    let contextoRAG = "";

    // AUTO_CONHECIMENTO_GENERATIVO

    try {

        const { execSync } = require("child_process");

        if (promptUsuario.toLowerCase().startsWith("aprender ")) {

            const consulta = promptUsuario.substring(9).trim();

            const contexto = execSync(
                `python3 ${CONFIG.ROOT}/nexus_tools/auto_conhecimento_generativo.py "${consulta.replace(/"/g,'\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

            return {
                acao: "conversar",
                msg: contexto
            };

        }

    } catch(e) {
        console.log("AUTO_CONHECIMENTO:", e.message);
    }


    // 🧠 Consulta memória aprendida antes do Gemini

    // CONSULTA_RAG_LOCAL

    try {

        const pergunta = promptUsuario.toLowerCase();

        if (
            pergunta.startsWith("explique") ||
            pergunta.startsWith("o que é") ||
            pergunta.startsWith("o que voce") ||
            pergunta.startsWith("o que você") ||
            pergunta.startsWith("pesquise") ||
            pergunta.startsWith("manual") ||
            pergunta.startsWith("documentação") ||
            pergunta.startsWith("documentacao") ||
            pergunta.includes("readme") ||
            pergunta.includes(".md") ||
            pergunta.includes(".json")
        ) {

            const { execSync } = require("child_process");

            const respostaLocal = execSync(
                `python3 ${CONFIG.ROOT}/nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

            if (
                respostaLocal &&
                !respostaLocal.includes("Nenhum conhecimento")
            ) {

                return {
                    acao: "conversar",
                    msg: respostaLocal
                };

            }

        }

    } catch(e) {

        console.log("CONSULTA_RAG_LOCAL:", e.message);

    }



    // RAG_CONSOLIDADO_DASHBOARD

    try {

        const { execSync } = require("child_process");

        const consultaConsolidada = execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/consolidar_conhecimento.py "${promptUsuario.replace(/"/g,'\\"')}"`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024
            }
        ).trim();


        if (
            consultaConsolidada &&
            !consultaConsolidada.includes("Nenhum conhecimento")
        ) {

            // RAG_CONSOLIDADO_STOP_AUTOBUILD

            contextoRAG = consultaConsolidada;
            console.log("RAG enviado como contexto para IA.");

            // Não retorna aqui.
            // O contexto será usado junto com a pergunta do usuário.

        }


    } catch(e) {

        console.log(
            "RAG_CONSOLIDADO_DASHBOARD:",
            e.message
        );

    }


// RAG_COMPLETO_NEXUS_V2

    try {

        const { execSync } = require("child_process");

        const consulta =
            promptUsuario.toLowerCase();

        if (
            consulta.includes("base de conhecimento") ||
            consulta.includes("documentação") ||
            consulta.includes("documentacao") ||
            consulta.includes("manual") ||
            consulta.includes("readme") ||
            consulta.includes(".md") ||
            consulta.includes(".json") ||
            consulta.includes("pesquise")
        ) {

            const resposta = execSync(
                `python3 ${CONFIG.ROOT}/nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 2 * 1024 * 1024
                }
            ).trim();


            if (resposta) {

                return {
                    acao: "conversar",
                    msg: resposta
                };

            }

        }

    } catch(e) {

        console.log(
            "RAG_COMPLETO_NEXUS_V2:",
            e.message
        );

    }



    try {
        const { execSync } = require("child_process");

        const memoria = execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/memory_lookup.py "${promptUsuario.replace(/"/g, '\"')}"`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8"
            }
        ).trim();

        console.log(
            "[MEMORY_LOOKUP]",
            promptUsuario,
            "=>",
            memoria
        );

        if (memoria) {

            console.log("🧠 Memória encontrada:", memoria);

            const catalogoSkills = require("./skills.json");

            const acoesPermitidas = [
                ...Object.keys(catalogoSkills.skills || {}),
                ...Object.keys(intentMap.acoes || {})
            ];

            if (
                memoria.startsWith("AUTO_BUILD:") &&
                !acoesPermitidas.includes(
                    memoria.replace("AUTO_BUILD:", "")
                )
            ) {

                return {
                    acao: memoria.replace("AUTO_BUILD:", ""),
                    params: "",
                    autoBuild: true,
                    msg: "Ferramenta será criada automaticamente."
                };

            }

            if (
                memoria === "ver_memoria" &&
                promptUsuario.toLowerCase().includes("ferramentas")
            ) {

                return {
                    acao: "listar_ferramentas",
                    params: "",
                    msg: "Ação corrigida pela memória Nexus."
                };

            }

            if (acoesPermitidas.includes(memoria)) {

                return {
                    acao: memoria,
                    params: promptUsuario,
                    msg: "Ação recuperada da memória Nexus."
                };

            }

            console.log("⚠️ Ação ignorada:", memoria);

        }

    } catch (e) {
        console.log("Memória indisponível:", e.message);
    }

    // BASE_CONHECIMENTO_LOCAL_RAG

    let contextoLocal = "";

    try {

        contextoLocal = execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024
            }
        ).trim();

    } catch(e) {

        console.log("AUTO_CONHECIMENTO:", e.message);

    }



    // MEMORIA FIREBASE RAG

    let contextoFirebase = "";

    try {

        contextoFirebase = await buscarConhecimentoFirebase(
            promptUsuario
        );

        if (contextoFirebase) {


          console.log(
                "Firebase RAG encontrado:",
                contextoFirebase.length,
                "caracteres"
            );

        }

    } catch(e) {

        console.log(
            "Firebase RAG erro:",
            e.message
        );

    }


    // RAG_FINAL_STOP_AUTO_BUILD

    if (
        contextoLocal &&
        contextoLocal.length > 50 &&
        (
            contextoLocal.includes("DOCUMENTAÇÃO NEXUS") ||
            contextoLocal.includes("CONHECIMENTO APRENDIDO")
        )
    ) {

        console.log("RAG local mantido como contexto para IA.");

    }

    const systemPrompt = `Você é o NEXUS SRE, um sistema operacional inteligente.

AMBIENTE DETECTADO
- Tipo: ${AMBIENTE.ambiente}
- Sistema: ${AMBIENTE.sistema || process.platform}
- Root: ${AMBIENTE.root}

REGRAS
- Se o ambiente for "render", nunca utilize comandos exclusivos do Termux (termux-info, termux-battery-status, termux-tts-speak).
- Se o ambiente for "termux", utilize normalmente os comandos do Termux.


BASE DE CONHECIMENTO LOCAL

${contextoLocal}

MEMORIA FIREBASE

${contextoFirebase}

BASE DE CONHECIMENTO CONSOLIDADO

${contextoRAG}

Use o conhecimento local e consolidado como contexto auxiliar.
Não responda apenas copiando a base de conhecimento.
Explique a resposta naturalmente, combinando o contexto recuperado com seu conhecimento geral quando necessário.


MISSÃO
- Conversar naturalmente.
- Interpretar intenções.
- Responder perguntas.
- Executar comandos python, bash, e outros quando necessário.

Responda SOMENTE JSON.

Formato:

{
  "acao":"",
  "params":"",
  "msg":""
}

Ações permitidas:

- conversar
- explicar_resultado
- executar_comando
- executar_script
- criar_script
- listar_arquivos
- utilizar_ferramentas
- criar_script
- listar_ferramentas
- buscar_arquivo
- criar_arquivo
- salvar_arquivo
- editar_arquivo
- instalar_pacote
- status_sistema
- parar_musica
- criar_diretórios
- acessar_web
- auto_aprender

- hora_sistema
Sempre que o usuário pedir informações do sistema utilize "executar_comando".

Exemplos:

"que horas são"
→ date

"onde estou"
→ pwd

"listar arquivos"
→ ls -lah

"uso do disco"
→ df -h

"memória"
→ free -h

"processos"
→ ps aux

"versão do node"
→ node --version

"versão do python"
→ python3 --version

"informações do Render"
→ render-info

"pesquisar internet"
→ curl -I https://google.com

somente use comandos destrutivos quando necessário como:

rm
mkfs
dd
shutdown
reboot

Usuário: ${promptUsuario}`;


try {
        const res = await axios.post(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key=${process.env.GEMINI_API_KEY}`,
            { contents: [{ role: "user", parts: [{ text: systemPrompt }] }] }
        );

        const textoIA = res.data.candidates[0].content.parts[0].text;
        console.log("RESPOSTA GEMINI:", textoIA);
        return parseIAJson(textoIA) || { acao: "conversar", msg: textoIA };
    } catch (err) {
        console.log("ERRO GEMINI:", err.response?.data || err.message);
        return { acao: "status_sistema", msg: "Erro de conexão com a mente central." };
    }
}

// --- ROTAS API ---

app.post("/api/chat", async (req, res) => {
    const { texto, voz } = req.body;
    const brain = await syncBrain();

    // NEXUS INTENT MEMORY ROUTER
    let intentMemoria = null;

    try {
        const mapa =
            brain.mapa_intencao_memoria || {};

        const entrada =
            texto
                .toLowerCase()
                .replace(/nexus[,:\s]*/g, "")
                .trim();

        for (const nome in mapa) {
            const item = mapa[nome];

            if (
                item.frases.some(frase =>
                    entrada.includes(frase.toLowerCase())
                )
            ) {
                intentMemoria = {
                    acao: item.acao,
                    params: "",
                    msg: "Ação recuperada da memória de intenção."
                };

                console.log(
                    "🧠 Intent memória:",
                    item.acao
                );

                break;
            }
        }

    } catch(e) {
        console.log(
            "Erro intent memória:",
            e.message
        );
    }

    let intent;

    const textoNormalizado = (prompt || "")
        .replace(/^nexus[\s,:-]*/i, "")
        .trim();

    const textoEditarHTML = textoNormalizado
        .match(/^editar[_\s]+html\s+(.+)$/i);

    const textoExecutarScript = textoNormalizado
        .match(/^executar[_\s]+script\s+(.+)$/i);

    const intentGerarCodigo = detectarGerarCodigo(prompt || "");

    if (intentGerarCodigo) {
        intent = intentGerarCodigo;

        console.log(
            "🚀 GATILHO DIRETO GERADOR:",
            intent.params
        );

    } else if (textoEditarHTML) {
        intent = {
            acao: "executar_script",
            params: `editar_html ${textoEditarHTML[1].trim()}`,
            msg: "Executando editor HTML solicitado."
        };

        console.log(
            "📝 GATILHO DIRETO EDITAR_HTML:",
            intent.params
        );

    } else if (textoExecutarScript) {
        intent = {
            acao: "executar_script",
            params: textoExecutarScript[1].trim(),
            msg: "Executando ferramenta solicitada."
        };

        console.log(
            "🔧 EXECUTAR_SCRIPT explícito:",
            intent.params
        );

    } else {
        intent =
            intentMemoria ||
            await processarIntencao(texto);
    }


    // RAG_FORCA_CONVERSA_FINAL

    if (
        intent &&
        intent.msg &&
        (
            intent.msg.includes("NEXUS CONHECIMENTO CONSOLIDADO") ||
            intent.msg.includes("CONHECIMENTO APRENDIDO") ||
            intent.msg.includes("DOCUMENTAÇÃO NEXUS")
        )
    ) {

        console.log(
            "RAG local encontrado. Bloqueando AutoBuild."
        );

        intent.acao = "conversar";
        intent.autoBuild = false;

    }


    // RAG_INTENT_FINAL_FIX

    if (
        intent &&
        intent.ragLocal === true
    ) {

        console.log(
            "RAG local detectado. Forçando conversa."
        );

        intent.acao = "conversar";
        intent.autoBuild = false;

    }

    console.log("========== DEBUG ==========");
    console.log("Intent:", JSON.stringify(intent, null, 2));
    console.log("Params:", intent.params);
    console.log("===========================");


    let execResult = null;
    let respostaFinal = intent.msg || "Comando processado.";


// Normalização de ações inválidas
const acoesValidas = new Set([
    "conversar",
    "executar_comando",
    "executar_script",
    "buscar_arquivo",
    "listar_arquivos",
    "listar_ferramentas",
    "ver_armazenamento",
    "status_sistema",
    "acessar_web",
    "auto_aprender"
]);

if (!acoesValidas.has(intent.acao)) {
    console.log("⚠️ Ação desconhecida:", intent.acao);

    try {
        const { registrar } = require("./nexus_tools/logger");
        registrar(
            "ERRO",
            `Ação desconhecida: ${intent.acao}`
        );
    } catch (e) {
        console.log("Falha ao registrar log:", e.message);
    }

    if (intent.msg && intent.msg.trim()) {
        respostaFinal = intent.msg;

        // Normaliza a ação antes da resposta
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

// Lógica de Ação

switch (intent.acao) {

    case "status_sistema":
        try {
            const os = require("os");

            respostaFinal = JSON.stringify({
                sistema: os.type(),
                plataforma: os.platform(),
                ambiente: process.env.RENDER ? "render" : "local",
                root: CONFIG.ROOT,
                hostname: os.hostname(),
                memoria_total: os.totalmem(),
                memoria_livre: os.freemem(),
                uptime: os.uptime()
            }, null, 2);

        } catch (e) {
            respostaFinal =
                "Erro ao obter status: " + e.message;
        }
        break;

    case "acessar_web":
        respostaFinal =
            intent.msg ||
            "Consulta web processada.";
        break;

    case "auto_aprender":
        try {

            const { execSync } = require("child_process");

            respostaFinal = execSync(
                `python3 ${CONFIG.ROOT}/nexus_tools/pesquisar_e_aprender.py ${JSON.stringify(intent.params || promptUsuario)}`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

        } catch (e) {

            respostaFinal =
                "Erro ao aprender: " + e.message;

        }

        break;

    case "buscar_arquivo":

        try {

            const { execSync } = require("child_process");

            respostaFinal = execSync(
                `python3 ${CONFIG.ROOT}/nexus_tools/auto_conhecimento_generativo.py "${intent.params || promptUsuario}"`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8",
                    maxBuffer: 1024 * 1024
                }
            ).trim();

        } catch(e) {

            respostaFinal =
                "Erro ao consultar a base de conhecimento: " +
                e.message;

        }

        break;

    case "listar_arquivos":
        try {
            const resultado = await shell(
                "ls -lah " + (intent.params || CONFIG.ROOT)
            );

            respostaFinal =
                resultado.stdout ||
                resultado.stderr ||
                "Nenhum arquivo encontrado.";

        } catch(e) {
            respostaFinal =
                "Erro ao listar arquivos: " + e.message;
        }
        break;



    case "ver_armazenamento":
        try {
            const { execSync } = require("child_process");

            respostaFinal = execSync("df -h", {
                encoding: "utf8"
            });

        } catch(e) {

            respostaFinal =
                "Erro ao verificar armazenamento: " + e.message;

        }

        break;

    case "listar_ferramentas":
        try {
            const fs = require("fs");
            const skills = JSON.parse(
                fs.readFileSync(CONFIG.ROOT + "/skills.json","utf8")
            );

            respostaFinal =
                Object.keys(skills.skills || {})
                    .sort()
                    .join("\n");

        } catch(e) {

            respostaFinal =
                "Erro ao listar ferramentas: " + e.message;

        }

        break;








    case "executar_script":
        try {

            const fs = require("fs");
            const path = require("path");
            const { execSync } = require("child_process");

            const skills = JSON.parse(
                fs.readFileSync(
                    path.join(CONFIG.ROOT, "skills.json"),
                    "utf8"
                )
            ).skills || {};

            let tool = (intent.params || "").trim();
            let argumentosFerramenta = "";

            // Se houver argumentos após o nome da ferramenta,
            // separa o primeiro token como ferramenta e preserva
            // todo o restante como argumento.
            const partesFerramenta = tool.match(/^(\S+)(?:\s+(.+))?$/);

            if (partesFerramenta) {
                tool = partesFerramenta[1];
                argumentosFerramenta = partesFerramenta[2] || "";
            }

            // Normaliza comandos enviados pela IA
            tool = tool
                .replace(/^python3\s+/i, "")
                .replace(/^python\s+/i, "")
                .trim();

            // Remove caminho e extensão
            tool = path.basename(tool);
            tool = tool.replace(/\.py$/i, "");

            console.log("🔧 Ferramenta normalizada:", tool);

            // Tenta resolver nomes sem separadores.
            // Exemplo: testetool -> teste_tool
            if (!(tool in skills)) {
                const normalizado = tool
                    .toLowerCase()
                    .replace(/[_\-\s]/g, "");

                const encontrada = Object.keys(skills).find(nome =>
                    nome
                        .toLowerCase()
                        .replace(/[_\-\s]/g, "") === normalizado
                );

                if (encontrada) {
                    console.log(
                        "🔧 Skill resolvida:",
                        tool,
                        "->",
                        encontrada
                    );
                    tool = encontrada;
                }
            }

            if (!(tool in skills)) {
                respostaFinal =
                    "Ferramenta não encontrada: " + tool;
                break;
            }

            const skill = skills[tool];

            // ============================================================
            // EDITOR HTML COM ORIGEM NO FIREBASE
            // ============================================================
            if (tool === "editar_html") {
                try {
                    const partesEdicao = argumentosFerramenta.match(
                        /^(\S+(?:\.html)?)\s+(.+)$/
                    );

                    if (!partesEdicao) {
                        respostaFinal =
                            "Uso: editar_html <nome_html> <alteração>";
                        break;
                    }

                    const nomeHTML = partesEdicao[1].trim();
                    const alteracaoHTML = partesEdicao[2].trim();

                    console.log(
                        "📝 Editando HTML:",
                        nomeHTML
                    );

                    const htmlFirebase =
                        await buscarHTMLFirebase(nomeHTML);

                    if (!htmlFirebase) {
                        respostaFinal =
                            "HTML não encontrado no Firebase: " +
                            nomeHTML;
                        break;
                    }

                    const scriptEditor = path.resolve(
                        CONFIG.ROOT,
                        "nexus_tools/editar_html.py"
                    );

                    const pastaFerramentas = path.resolve(
                        CONFIG.ROOT,
                        "nexus_tools"
                    );

                    if (
                        !scriptEditor.startsWith(
                            pastaFerramentas + path.sep
                        )
                    ) {
                        respostaFinal =
                            "Execução do editor bloqueada.";
                        break;
                    }

                    /*
                     * O editor Python trabalha com arquivo local.
                     * Criamos temporariamente o HTML recuperado do Firebase.
                     */
                    const pastaHTML = path.resolve(
                        CONFIG.ROOT,
                        "html_gerados"
                    );

                    fs.mkdirSync(
                        pastaHTML,
                        { recursive: true }
                    );

                    const arquivoTemporario =
                        path.join(
                            pastaHTML,
                            path.basename(nomeHTML, ".html") + ".html"
                        );

                    fs.writeFileSync(
                        arquivoTemporario,
                        htmlFirebase.html,
                        "utf8"
                    );

                    const resultadoEditor = execSync(
                        `python3 "${scriptEditor}" ` +
                        `${JSON.stringify(path.basename(arquivoTemporario))} ` +
                        `${JSON.stringify(alteracaoHTML)}`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8",
                            maxBuffer: 4 * 1024 * 1024
                        }
                    ).trim();

                    respostaFinal = resultadoEditor;

                    /*
                     * Localiza o novo HTML criado pelo editor.
                     */
                    const marcadorEditado =
                        "=== HTML EDITADO SALVO ===";

                    const inicioEditado =
                        resultadoEditor.indexOf(
                            marcadorEditado
                        );

                    if (inicioEditado >= 0) {
                        const trechoEditado =
                            resultadoEditor.substring(
                                inicioEditado +
                                marcadorEditado.length
                            );

                        const linhasEditado =
                            trechoEditado
                                .split("\n")
                                .map(l => l.trim())
                                .filter(Boolean);

                        const arquivoEditado =
                            linhasEditado[0];

                        if (
                            arquivoEditado &&
                            arquivoEditado.endsWith(".html") &&
                            fs.existsSync(arquivoEditado)
                        ) {
                            const htmlEditado =
                                fs.readFileSync(
                                    arquivoEditado,
                                    "utf8"
                                );

                            const nomeSalvo =
                                await salvarHTMLEditadoFirebase(
                                    nomeHTML,
                                    htmlEditado,
                                    alteracaoHTML
                                );

                            if (nomeSalvo) {
                                respostaFinal +=
                                    "\n\n=== FIREBASE ===\n" +
                                    "HTML editado sincronizado com Firebase.\n" +
                                    "Nova versão: " +
                                    nomeSalvo;
                            }
                        }
                    }

                    /*
                     * Remove somente o arquivo temporário usado
                     * para alimentar o editor.
                     */
                    try {
                        if (fs.existsSync(arquivoTemporario)) {
                            fs.unlinkSync(arquivoTemporario);
                        }
                    } catch (limpezaErro) {
                        console.log(
                            "Aviso ao remover HTML temporário:",
                            limpezaErro.message
                        );
                    }

                } catch (editorErro) {
                    respostaFinal =
                        "Erro ao editar HTML: " +
                        editorErro.message;
                }

                break;
            }

            // ============================================================
            // EXECUTOR PYTHON
            // ============================================================
            if (skill.executor === "python") {

                const script = path.resolve(
                    CONFIG.ROOT,
                    skill.script
                );

                const pasta = path.resolve(
                    CONFIG.ROOT,
                    "nexus_tools"
                );

                if (!script.startsWith(pasta + path.sep)) {
                    respostaFinal =
                        "Execução bloqueada.";
                    break;
                }

                if (!fs.existsSync(script)) {
                    respostaFinal =
                        "Script inexistente: " + skill.script;
                    break;
                }

                const argumentosShell = argumentosFerramenta
                    ? ` ${JSON.stringify(argumentosFerramenta)}`
                    : "";

                respostaFinal = execSync(
                    `python3 "${script}"${argumentosShell}`,
                    {
                        cwd: CONFIG.ROOT,
                        encoding: "utf8",
                        maxBuffer: 1024 * 1024
                    }
                ).trim();


            // ============================================================
            // SALVAR HTML GERADO NO FIREBASE
            // ============================================================
            if (
                tool === "gerar_codigo" &&
                respostaFinal.includes("=== HTML SALVO ===")
            ) {
                try {
                    const inicio = respostaFinal.indexOf(
                        "=== HTML SALVO ==="
                    );

                    const trecho = respostaFinal.substring(
                        inicio + "=== HTML SALVO ===".length
                    );

                    const linhasHTML = trecho
                        .split("\n")
                        .map(l => l.trim())
                        .filter(Boolean);

                    const arquivoHTML = linhasHTML[0];

                    if (
                        arquivoHTML &&
                        arquivoHTML.endsWith(".html") &&
                        fs.existsSync(arquivoHTML)
                    ) {
                        console.log(
                            "☁️ Enviando HTML gerado para Firebase:",
                            arquivoHTML
                        );

                        await salvarHTMLFirebase(
                            arquivoHTML,
                            argumentosFerramenta,
                            "gemini-3.1-flash-lite"
                        );

                        respostaFinal +=
                            "\n\n=== FIREBASE ===\n" +
                            "HTML sincronizado com Firebase.";
                    } else {
                        console.log(
                            "⚠️ Caminho do HTML gerado não encontrado:",
                            arquivoHTML
                        );
                    }

                } catch (firebaseErro) {
                    console.log(
                        "⚠️ HTML gerado, mas não foi possível salvar no Firebase:",
                        firebaseErro.message
                    );
                }
            }

            // EXECUTOR BASH
            } else if (skill.executor === "bash") {

                if (!skill.comando || !skill.comando.trim()) {
                    respostaFinal =
                        "Comando bash não definido na ferramenta.";
                    break;
                }

                console.log(
                    "🔧 Executando Bash:",
                    skill.comando
                );

                respostaFinal = execSync(
                    skill.comando,
                    {
                        cwd: CONFIG.ROOT,
                        encoding: "utf8",
                        maxBuffer: 1024 * 1024
                    }
                ).trim();

            } else {

                respostaFinal =
                    "Executor não permitido: " +
                    (skill.executor || "não definido");
                break;
            }

            // REGISTRA AUTOMATICAMENTE COMO FUNCIONANDO
            // SOMENTE APÓS EXECUÇÃO BEM-SUCEDIDA.
            // Ferramentas de gerenciamento da própria memória
            // não devem registrar a si mesmas.
            const ferramentasNaoRegistrar = new Set([
                "atualizar_lista_comandos",
                "listar_comandos_funcionando",
                "limpar_registro_comando"
            ]);

            if (!ferramentasNaoRegistrar.has(tool)) {
                try {
                    execSync(
                        `python3 ${CONFIG.ROOT}/nexus_tools/atualizar_lista_comandos.py ${JSON.stringify(tool)} ${JSON.stringify(respostaFinal)}`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8",
                            maxBuffer: 1024 * 1024
                        }
                    );

                    console.log(
                        "✅ Comando confirmado e registrado:",
                        tool
                    );

                } catch (registroErro) {
                    console.log(
                        "⚠️ Executado, mas não foi possível registrar no Firebase:",
                        registroErro.message
                    );
                }
            }

        } catch(e) {

            respostaFinal =
                "Erro ao executar ferramenta:\n\n" +
                (
                    e.stderr?.toString() ||
                    e.stdout?.toString() ||
                    e.message
                );
        }

        break;

default:
        try {
            const { execSync } = require("child_process");

            let acaoRouter = intent.acao;


            if (intent.acao === "executar_comando") {

                if (
                    intent.params &&
                    intent.params.trim().startsWith("cd ")
                ) {

                    const destino = intent.params
                        .trim()
                        .substring(3)
                        .trim();

                    execSync(
                        `python3 ${CONFIG.ROOT}/nexus_tools/cwd_manager.py set "${destino}"`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8"
                        }
                    );

                    respostaFinal =
                        "Diretório alterado para: " + destino;

                    break;

                }


                try {

                    const retorno = execSync(
                        `python3 ${CONFIG.ROOT}/shell_executor.py ${JSON.stringify(intent.params)}`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8"
                        }
                    );

                    const resultado = JSON.parse(retorno);

                    execResult = resultado;


respostaFinal =
    resultado.stdout ||
    resultado.stderr ||
    resultado.erro ||
    "Comando executado.";

break;

if (

                        resultado.executor === "termux-battery-status"
                    ) {

                        const bat = JSON.parse(resultado.stdout);

                        respostaFinal =
                            `Bateria: ${bat.percentage}%\n` +
                            `Temperatura: ${bat.temperature}°C\n` +
                            `Estado: ${bat.status}`;

                    } else if (
                        resultado.executor === "termux-volume"
                    ) {

                        const vols = JSON.parse(resultado.stdout);

                        respostaFinal = vols
                            .map(v => `${v.stream}: ${v.volume}/${v.max_volume}`)
                            .join("\n");

                    } else if (
                        resultado.executor === "termux-torch"
                    ) {

                        respostaFinal = "Lanterna acionada.";

                    } else {

                        respostaFinal =
                            resultado.stdout ||
                            resultado.stderr ||
                            resultado.erro ||
                            "Comando executado.";

                    }

                    break;

                } catch (e) {

                    respostaFinal =
                        "Erro ao executar comando Shell: " + e.message;

                    break;

                }

            }



            if (
                intent.acao === "executar_comando" &&
                (
                    intent.params === "pkg list-installed" ||
                    intent.params === "apt list --installed"
                )
            ) {
                acaoRouter = "listar_ferramentas";
            }

            let chave =
                intentMap.comandos[intent.params] ||
                intentMap.acoes[intent.acao] ||
                acaoRouter;

            // Validação de ação antes da execução
            const skillsValidacao = require("./skills.json");


            // RAG_SKIP_AUTO_TOOL

            if (
                intent.acao &&
                (
                    intent.acao.startsWith("explique") ||
                    intent.acao.startsWith("o_que") ||
                    intent.acao.includes("pesquise")
                )
            ) {

                console.log(
                    "RAG respondeu. Ignorando criação automática de ferramenta."
                );

                intent.autoBuild = false;

            }


// RAG_LOCAL_BLOQUEIA_AUTOBUILD

            if (
                intent.autoBuild &&
                !skillsValidacao.skills[chave] &&
                !intentMap.acoes[chave]
            ) {


                // BLOQUEIO_FILE_CREATOR_RAG

                if (
                    intent.acao === "conversar" ||
                    intent.ragLocal === true
                ) {

                    console.log(
                        "RAG local: criação automática cancelada."
                    );

                    respostaFinal =
                        intent.msg ||
                        "Resposta encontrada na base local.";

                    break;

                }

                console.log(
                    "🛠️ Ferramenta inexistente:",
                    chave
                );

                try {

                    const { execSync } = require("child_process");

                    const normalizar_nome_tool = (nome) =>
                        nome
                            .toLowerCase()
                            .replace(/[^a-z0-9_]/g, "_")
                            .replace(/^_+|_+$/g, "");

                    const novaTool =
                        normalizar_nome_tool(
                            texto
                        );

                    console.log(
                        "🔧 Criando ferramenta automática:",
                        novaTool
                    );

                    execSync(
                        `python3 ${CONFIG.ROOT}/nexus_tools/file_creator.py criar_tool ${novaTool} "Ferramenta criada automaticamente pelo Nexus" "${texto}" "print('Ferramenta ${novaTool} criada automaticamente pelo Nexus')"`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8"
                        }
                    );

                    chave = novaTool;
                    intent.acao = novaTool;

                    console.log(
                        "✅ Ferramenta criada:",
                        novaTool
                    );

                } catch(e) {

                    console.log(
                        "❌ Falha no auto builder:",
                        e.message
                    );

                    respostaFinal =
                        "Não consegui criar a ferramenta automaticamente.";

                    break;
                }
            }

// Atualiza a ação para refletir a executada
intent.acao = chave;

            const retorno = execSync(
                `python3 ${CONFIG.ROOT}/nexus_tools/command_router.py ${chave}`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8"
                }
            );

            execResult = {
                success: true,
                executor: intent.executor || "desconhecido",
                output: retorno.toString().trim()
            };

            respostaFinal =
                intent.msg ||
                "Execução concluída com sucesso.";

            // 🧠 Aprende após execução bem sucedida
            const blacklist = [
                "executar_comando",
                "status_sistema",
                "notificacao"
            ];

            const catalogoSkills = require("./skills.json");

              const acaoOficial =
                  catalogoSkills.skills[chave] ||
                  intentMap.acoes[chave] ||
                  intentMap.comandos[chave];

              if (
                  !blacklist.includes(chave) &&
                  acaoOficial
              ) {

                  await registrarAprendizadoAutomatico(
                      texto,
                      chave
                  );

              } else {

                  console.log(
                      "⚠️ Aprendizado bloqueado:",
                      chave
                  );

              }

              // 🧠 NEXUS LEARNING MEMORY
            try {
                execSync(
                    `python3 -c "from nexus_tools.learning_memory import registrar_acerto; registrar_acerto('${texto.replace("'", "\\'")}', '${chave}')"` ,
                    {
                        cwd: CONFIG.ROOT,
                        encoding: "utf8"
                    }
                );

                console.log("🧠 Memória atualizada:", chave);

            } catch (memErro) {
                console.log("Falha memória:", memErro.message);
            }

        } catch (e) {

            respostaFinal = intent.msg || "Falha ao executar ferramenta.";

        }
        break;
}

// Atualizar Memória

    if (!brain.historico) brain.historico = [];

    brain.historico.push({
        t: Date.now(),
        entrada: texto,
        acao: intent.acao,
        resposta: respostaFinal,
        ok: execResult ? execResult.success : true
    });

    if (brain.historico.length > 100)
        brain.historico.shift();

    await syncBrain(brain);

    if (voz) falar(respostaFinal);

    // NEXUS EXECUTOR INFO
    try {

        const skills = require("./skills.json");

        const skill =
            skills.skills[intent.acao];

        if (skill) {
            intent.executor =
                skill.executor;

            intent.script =
                skill.script || "";

            intent.comando =
                skill.comando || "";
        }

    } catch(e) {
        console.log(
            "Erro executor info:",
            e.message
        );
    }

    res.json({
        nexus: respostaFinal,
        intent: intent,
        shell: execResult
    });
});

// -------------------------------------------------------
// API_APRENDER_CONHECIMENTO
// -------------------------------------------------------

app.post("/api/aprender", async (req, res) => {

    const { tema } = req.body;

    if (!tema || !tema.trim()) {
        return res.json({
            success: false,
            erro: "Tema não informado."
        });
    }

    try {

        const { execSync } = require("child_process");

        const resultado = execSync(
            `python3 ${CONFIG.ROOT}/nexus_tools/pesquisar_e_aprender.py ${JSON.stringify(tema.trim())}`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024 * 10
            }
        );

        // SALVA CONHECIMENTO NO FIREBASE
        try {

            const matchArquivo = resultado.match(
                /Arquivo:\s*(.*\.md)/
            );

            if (matchArquivo) {

                const caminhoArquivo = matchArquivo[1].trim();

                await salvarConhecimentoFirebase(
                    caminhoArquivo
                );

            }

        } catch(firebaseErro) {

            console.log(
                "Falha ao enviar conhecimento Firebase:",
                firebaseErro.message
            );

        }

        res.json({
            success: true,
            output: resultado
        });

    } catch (e) {

        res.json({
            success: false,
            erro: e.message
        });

    }

});


/** Status rápido para monitoramento externo */
app.get("/api/health", (req, res) => {
    res.json({
        status: "ONLINE"
    });
});

/** Execução de comandos manuais (DEBUG) */
app.post("/api/terminal", async (req, res) => {
    const { cmd, secret } = req.body;
    // Adicione uma validação de senha aqui se expuser para a internet!
    const result = await shell(cmd);
    res.json(result);
});

// --- BOOT ---



function consultarBrain(pergunta) {

    try {

        const { execSync } = require("child_process");

        return execSync(
            `python3 ${__dirname}/nexus_tools/brain_agent.py ${JSON.stringify(pergunta)}`,
            {
                encoding: "utf8"
            }
        ).trim();

    } catch (e) {

        console.log("Brain:", e.message);

        return null;

    }

}


async function bootstrap() {

    await carregarMemoriaFirebase();
console.clear();
    console.log(`
    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ v32.2
    `);

    await syncBrain(); // Carrega o cérebro
    app.listen(CONFIG.PORT, "0.0.0.0", () => {
        console.log(`[SERVER] Nexus SRE operando na porta ${CONFIG.PORT}`);
        console.log(`[PATH] Root: ${CONFIG.ROOT}`);
    });
}

bootstrap();

// Tratamento de erros globais
process.on("uncaughtException", (err) => console.error("[FATAL ERROR]", err));
process.on("unhandledRejection", (err) => console.error("[PROMISE REJECTION]", err));

