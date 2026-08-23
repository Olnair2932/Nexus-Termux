require("dotenv").config();

const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');
const fsp = require('fs').promises;
const { exec, execFile } = require('child_process');
const { execSync, execFileSync } = require("child_process");

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
const multer = require('multer');
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

        const dados = JSON.parse(memoria);

        // Firebase Realtime Database não aceita ".", "#", "$", "/", "[", "]"
        // em nomes de propriedades. Sanitizamos somente as chaves.
        function sanitizarChavesFirebase(valor) {
            if (Array.isArray(valor)) {
                return valor.map(sanitizarChavesFirebase);
            }

            if (valor && typeof valor === "object") {
                const resultado = {};

                for (const [chave, conteudo] of Object.entries(valor)) {
                    const chaveSegura = chave
                        .replace(/[.#$\/\[\]]/g, "_");

                    resultado[chaveSegura] =
                        sanitizarChavesFirebase(conteudo);
                }

                return resultado;
            }

            return valor;
        }

        const dadosFirebase =
            sanitizarChavesFirebase(dados);

        await db
            .ref("nexus/memoria")
            .set(dadosFirebase);

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
                    <div class="card-actions">
                        <a
                            class="open"
                            href="/html_gerados/${encodeURIComponent(nome)}.html">
                            ABRIR PAINEL →
                        </a>

                        <button
                            class="btn-edit"
                            type="button"
                            onclick="editarHTML(${JSON.stringify(nome)})">
                            ✏️ EDITAR
                        </button>

                        <button
                            class="btn-delete"
                            type="button"
                            onclick="excluirHTML(${JSON.stringify(nome)})">
                            🗑 EXCLUIR
                        </button>
                    </div>
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

.card-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
}

.card-actions a,
.card-actions button {
    border: 1px solid var(--border);
    padding: 8px 10px;
    font-family: inherit;
    font-size: 11px;
    cursor: pointer;
    text-decoration: none;
}

.btn-edit {
    color: #58a6ff;
    background: #0b1622;
}

.btn-delete {
    color: #ff4d4d;
    background: #260d0d;
}

.btn-edit:hover {
    border-color: #58a6ff;
}

.btn-delete:hover {
    border-color: #ff4d4d;
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


<script>
async function editarHTML(nome) {
    try {
        await navigator.clipboard.writeText(nome);

        alert(
            "Código do HTML copiado para a área de transferência."
        );

    } catch (erro) {
        alert(
            "Não foi possível copiar o código: " +
            erro.message
        );
    }
}

async function excluirHTML(nome) {
    const confirmar = confirm(
        "Deseja realmente excluir este HTML?"
    );

    if (!confirmar) {
        return;
    }

    try {
        const resposta = await fetch(
            "/api/html_gerados/" +
            encodeURIComponent(nome),
            {
                method: "DELETE"
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro ||
                "Erro ao excluir HTML."
            );
        }

        alert("HTML excluído com sucesso.");

        window.location.reload();

    } catch (erro) {
        alert(
            "Erro ao excluir HTML: " +
            erro.message
        );
    }
}
</script>

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


// ============================================================
// API: EXCLUIR HTML GERADO
// ============================================================

app.delete("/api/html_gerados/:nome", async (req, res) => {
    try {
        const { execSync } = require("child_process");

        let nome = String(
            req.params.nome || ""
        ).trim();

        nome = path.basename(nome);
        nome = nome.replace(/\.html$/i, "");

        if (!nome) {
            return res.status(400).json({
                erro: "Nome do HTML não informado."
            });
        }

        const scriptExcluir = path.resolve(
            CONFIG.ROOT,
            "nexus_tools/excluir_html.py"
        );

        const pastaFerramentas = path.resolve(
            CONFIG.ROOT,
            "nexus_tools"
        );

        if (
            !scriptExcluir.startsWith(
                pastaFerramentas + path.sep
            )
        ) {
            return res.status(403).json({
                erro: "Execução bloqueada."
            });
        }

        if (!fs.existsSync(scriptExcluir)) {
            return res.status(404).json({
                erro:
                    "Script excluir_html.py não encontrado."
            });
        }

        console.log(
            "🗑️ API excluindo HTML:",
            nome
        );

        const resultado = execSync(
            `python3 "${scriptExcluir}" ` +
            `${JSON.stringify(nome)}`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024
            }
        ).trim();

        return res.json({
            ok: true,
            nome,
            resultado
        });

    } catch (erro) {
        console.error(
            "Erro na API de exclusão:",
            erro.message
        );

        return res.status(500).json({
            ok: false,
            erro: erro.message
        });
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
        "criar uma página html",
        "criar uma pagina html",
        "criar página html",
        "criar pagina html",
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


// ============================================================
// GATILHOS DE GERAÇÃO DE NOVAS FERRAMENTAS
// ============================================================

function detectarGerarFerramenta(prompt) {
    const texto = (prompt || "")
        .toLowerCase()
        .replace(/^nexus[,:]?\s*/i, "")
        .trim();

    const gatilhos = [
        "criar uma ferramenta",
        "crie uma ferramenta",
        "criar nova ferramenta",
        "crie uma nova ferramenta",
        "gerar uma ferramenta",
        "gere uma ferramenta",
        "gerar nova ferramenta",
        "gere uma nova ferramenta",
        "desenvolver uma ferramenta",
        "desenvolva uma ferramenta",
        "programar uma ferramenta",
        "programe uma ferramenta",
        "implementar uma ferramenta",
        "implemente uma ferramenta",
        "construir uma ferramenta",
        "construa uma ferramenta",
        "fazer uma ferramenta",
        "faça uma ferramenta",
        "criar um utilitário",
        "crie um utilitário",
        "gerar um utilitário",
        "gere um utilitário",
        "criar um script",
        "crie um script",
        "gerar um script",
        "gere um script",
        "criar automação",
        "crie uma automação",
        "gerar automação",
        "gere uma automação",
        "criar executor",
        "crie um executor",
        "gerar executor",
        "gere um executor",
        "criar comando personalizado",
        "crie um comando personalizado",
        "gerar comando personalizado",
        "gere um comando personalizado",
        "criar skill",
        "crie uma skill",
        "criar uma nova skill",
        "gerar skill",
        "gere uma skill",
        "criar recurso",
        "crie um novo recurso",
        "adicionar ferramenta",
        "adicione uma ferramenta",
        "adicionar nova ferramenta",
        "adicione uma nova ferramenta",
        "criar ferramenta automaticamente",
        "crie a ferramenta automaticamente",
        "gere automaticamente uma ferramenta",
        "criar nova capacidade",
        "desenvolver nova capacidade",
        "adicionar nova capacidade"
    ];

    const encontrado = gatilhos.find(gatilho =>
        texto.includes(gatilho)
    );

    if (!encontrado) {
        return null;
    }

    return {
        acao: "gerar_ferramenta",
        params: texto,
        autoBuild: true,
        msg: "Gerando nova ferramenta automaticamente."
    };
}


// ============================================================
// GATILHOS DE EXECUÇÃO DE FERRAMENTAS
// ============================================================

function detectarExecutarFerramenta(prompt) {
    const texto = (prompt || "")
        .toLowerCase()
        .replace(/^nexus[,:]?\s*/i, "")
        .trim();

    const gatilhos = [
        "executar a ferramenta",
        "execute a ferramenta",
        "executar ferramenta",
        "execute ferramenta",
        "rodar a ferramenta",
        "rode a ferramenta",
        "usar a ferramenta",
        "use a ferramenta",
        "chamar a ferramenta",
        "chame a ferramenta",
        "acionar a ferramenta",
        "acione a ferramenta",
        "ativar a ferramenta",
        "ative a ferramenta",
        "executar o utilitário",
        "execute o utilitário",
        "rodar o utilitário",
        "rode o utilitário",
        "executar o script",
        "execute o script",
        "rodar o script",
        "rode o script",
        "executar a skill",
        "execute a skill",
        "usar a skill",
        "use a skill",
        "executar o executor",
        "execute o executor",
        "acionar o executor",
        "acione o executor",
        "testar a ferramenta",
        "teste a ferramenta",
        "testar ferramenta",
        "teste ferramenta",
        "executar a nova ferramenta",
        "execute a nova ferramenta",
        "rodar a nova ferramenta",
        "rode a nova ferramenta"
    ];

    const encontrado = gatilhos
        .sort((a, b) => b.length - a.length)
        .find(gatilho => texto.startsWith(gatilho));

    if (!encontrado) {
        return null;
    }

    // Remove o gatilho e preserva somente:
    // nome_da_ferramenta [argumentos]
    const restante = texto
        .substring(encontrado.length)
        .trim();

    if (!restante) {
        return {
            acao: "executar_ferramenta",
            params: "",
            msg: "Informe o nome da ferramenta que deseja executar."
        };
    }

    return {
        acao: "executar_ferramenta",
        params: restante,
        msg: "Executando ferramenta solicitada."
    };
}


// ============================================================
// GATILHOS COMBINADOS: GERAR E EXECUTAR
// ============================================================

function detectarGerarEExecutarFerramenta(prompt) {
    const texto = (prompt || "")
        .toLowerCase()
        .replace(/^nexus[,:]?\s*/i, "")
        .trim();

    const gatilhos = [
        "criar e executar uma ferramenta",
        "crie e execute uma ferramenta",
        "gerar e executar uma ferramenta",
        "gere e execute uma ferramenta",
        "criar e rodar uma ferramenta",
        "crie e rode uma ferramenta",
        "gerar e rodar uma ferramenta",
        "gere e rode uma ferramenta",
        "criar ferramenta para",
        "crie uma ferramenta para",
        "gerar ferramenta para",
        "gere uma ferramenta para",
        "criar um script para",
        "crie um script para",
        "gerar um script para",
        "gere um script para",
        "criar automação para",
        "crie uma automação para",
        "gerar automação para",
        "gere uma automação para"
    ];

    const encontrado = gatilhos.find(gatilho =>
        texto.includes(gatilho)
    );

    if (!encontrado) {
        return null;
    }

    return {
        acao: "gerar_e_executar_ferramenta",
        params: texto,
        autoBuild: true,
        msg: "Gerando e executando nova ferramenta."
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

AMBIENTE
- Tipo: ${AMBIENTE.ambiente}
- Sistema: ${AMBIENTE.sistema || process.platform}
- Root: ${AMBIENTE.root}

REGRAS DE AMBIENTE
- Se estiver no Render, não use comandos exclusivos do Termux.
- Se estiver no Termux, recursos do Termux podem ser utilizados.
- Sempre considere o ambiente antes de escolher uma ação.

CONTEXTO
BASE DE CONHECIMENTO LOCAL:
${contextoLocal}

MEMÓRIA FIREBASE:
${contextoFirebase}

CONHECIMENTO CONSOLIDADO:
${contextoRAG}

Use esse contexto apenas como auxílio para compreender a solicitação.
Não copie a documentação como resposta.
Não transforme conteúdo recuperado em uma ação automaticamente.

MISSÃO
Você é o componente responsável por INTERPRETAR a linguagem natural do usuário e decidir qual operação o servidor deve realizar.

O usuário pode falar normalmente.
Ele NÃO precisa conhecer:
- nomes de scripts;
- nomes de ferramentas;
- comandos Linux;
- comandos Bash;
- comandos Python.

Você deve converter a intenção natural do usuário para uma ação que EXISTE no servidor.

REGRA FUNDAMENTAL

PRIMEIRO determine a intenção.

DEPOIS escolha a ação.

DEPOIS monte os parâmetros.

NUNCA invente uma ação.

NUNCA execute uma operação quando o usuário estiver apenas conversando ou pedindo explicação.

DECISÃO DE CONVERSA

Use:

"conversar"

quando o usuário:
- cumprimentar;
- fizer conversa casual;
- perguntar quem é o Nexus;
- perguntar como o Nexus funciona;
- pedir uma explicação;
- pedir opinião ou orientação que não exija execução no sistema;
- fizer uma pergunta conceitual.

Exemplos:

"Olá"
→ conversar

"Oi Nexus"
→ conversar

"Explique o Nexus"
→ conversar

"Como você funciona?"
→ conversar

"Para que serve o Firebase?"
→ conversar

DECISÃO DE EXECUÇÃO

Se o usuário estiver pedindo que algo seja REALIZADO no sistema, não use "conversar".

Escolha a ação executável correspondente.

COMANDOS LINUX / BASH

Se a intenção puder ser realizada diretamente por um comando Linux ou Bash:

→ executar_comando

Exemplos:

"liste os arquivos"
→ executar_comando
params: ls -lah

"onde estou?"
→ executar_comando
params: pwd

"qual a versão do Python?"
→ executar_comando
params: python3 --version

"qual a versão do Node?"
→ executar_comando
params: node --version

"mostre os processos"
→ executar_comando
params: ps aux

"qual o espaço disponível?"
→ executar_comando
params: df -h

SCRIPT OU FERRAMENTA PYTHON

Se o usuário pedir para executar um script Python ou uma ferramenta existente:

→ executar_script

Exemplos:

"execute teste.py"
→ executar_script
params: teste.py

"execute teste.py com abc"
→ executar_script
params: teste.py abc

"rode a ferramenta suggestion_manager"
→ executar_script
params: suggestion_manager

LISTAGEM DE ARQUIVOS

Se o usuário pedir para listar arquivos ou diretórios:

→ listar_arquivos

Exemplos:

"liste os HTML gerados"
→ listar_arquivos
params: html_gerados

"mostre os arquivos da pasta html_gerados"
→ listar_arquivos
params: html_gerados

Se o usuário disser apenas "ls", trate como pedido para listar arquivos:

→ listar_arquivos
params: .

ARMAZENAMENTO

Se pedir informações sobre espaço em disco:

→ ver_armazenamento

STATUS DO SISTEMA

Se pedir informações gerais sobre o estado do sistema:

→ status_sistema

ARQUIVOS E CONHECIMENTO

Se pedir para consultar, localizar ou pesquisar conhecimento/arquivos:

→ buscar_arquivo

AUTOAPRENDIZADO

Se pedir explicitamente para aprender sobre um assunto:

→ auto_aprender

Exemplos:

"aprenda Python"
→ auto_aprender
params: Python

"aprenda sobre Firebase"
→ auto_aprender
params: Firebase

INTERNET

Se pedir uma consulta na internet:

→ acessar_web

EDITOR HTML

Existe uma ferramenta chamada "editar_html".

Ela NÃO é uma ação principal.

Ela é uma ferramenta executada através de:

→ executar_script

Quando o usuário pedir edição de HTML, coloque o nome da ferramenta e seus argumentos em "params".

Exemplo:

"altere o título principal do landing.html para NEXUS SRE"

Resultado:

{
  "acao": "executar_script",
  "params": "editar_html landing.html altere o título principal para NEXUS SRE",
  "msg": "Editando o HTML."
}

NUNCA faça:

{
  "acao": "editar_html"
}

A ação correta é sempre:

{
  "acao": "executar_script"
}

e "editar_html" fica dentro de "params".

FERRAMENTAS EXISTENTES

Quando houver uma ferramenta específica no sistema para realizar a solicitação, prefira executar essa ferramenta em vez de inventar uma implementação diferente.

Para executar uma ferramenta Python existente:

→ executar_script

Preserve os argumentos fornecidos pelo usuário.

AÇÕES VÁLIDAS

As ações são carregadas dinamicamente de skills.json.

Use SOMENTE uma das ações abaixo:

- aprender__interpretar_linguagem_natural
- aprender__interpretar_linguagem_natural__ollama
- aprender_auto_aprendizado
- aprender_bash
- aprender_com_auto_conhecimento_generativo
- aprender_com_auto_conhecimento_generativo_a_otimizar_sistema
- aprender_com_auto_conhecimento_generativo_analisar_reescrever_otimizar_arquivos
- aprender_com_auto_conhecimento_generativo_backup
- aprender_com_auto_conhecimento_generativo_ingl_s
- aprender_comandos_shell
- aprender_docker
- aprender_instalar_pacotes
- aprender_instalar_pacotes_ia
- aprender_instalar_python_3
- aprender_linux
- aprender_navega__o_shell
- aprender_node_module
- aprender_novo_conhecimento
- aprender_python_3
- aprender_sre
- atualizar_lista_comandos
- atualizar_memoria
- auto_conhecimento_generativo
- auto_fix
- auto_learning
- auto_skill_generator
- backup_checker
- baixar_bibliotecas
- baixar_lynx
- bash_executor
- brain_agent
- buscar_conhecimento
- command_router
- command_router.backup_v32.2
- command_router.before_cli_args_v32.2
- command_router.before_integration_v32.2
- consertar_if_autobuild
- consolidar_conhecimento
- copiar_clipboard
- criar_arquivo
- criar_indice_conhecimento
- cwd_manager
- da_um_ls
- dashboard_builder
- dashboard_editor
- dashboard_optimizer
- detectar_ambiente
- editar_html
- entra_na_pasta___sentinela_dev
- error_to_suggestion
- events
- evolution_history
- evolution_loader
- excluir_html
- executar_comando_aprender_node_module
- execution_engine
- explique_o_brain_json
- explique_o_nexus_sre
- explique_o_nexus_sree
- explique_o_que___o_que_voc__sabe_pesquise_base_de_conhecimento_arquivo_documenta__o_manual
- explique_tudo_sobre_ollama
- file_creator
- gerar_codigo
- github
- improvement_applier
- improvement_executor
- improvement_guard
- improvement_learning
- improvement_planner
- improvement_validator
- indexar_conhecimento
- informacoes_dispositivo
- iniciar_aprender_com_auto_conhecimento_generativo_analisar_reescrever_otimizar_arquivos
- instalar_python_3
- integrar_ambiente_system_prompt
- knowledge
- known
- learn
- learning_memory
- learning_queue
- ler_textos_p_blico_online_de_conhecimento
- limpar_registro_comando
- listar_comandos_funcionando
- listar_ferramentas
- listar_processos
- log_analyzer
- logger
- memory_lookup
- mode
- mostrar_toast
- nexus_aplica_o_comando_no_termux_de_ligar_a_lanterna
- notificar
- o_que___ollama
- oi
- ol__nexus_ligar_lanterna
- patch_aprendizado_assistido
- patch_auto_conhecimento
- patch_bloquear_auto_tool_rag
- patch_bloqueio_file_creator_rag
- patch_bloqueio_rag_autobuild_final
- patch_buscar_arquivo
- patch_conhecimento_pasta
- patch_conhecimento_pasta_v2
- patch_conhecimento_pasta_v3
- patch_consulta_rag
- patch_consulta_rag_v2
- patch_dashboard_consolidado_rag
- patch_normalizar_consulta_rag
- patch_rag_antes_executor
- patch_rag_autobuild_seguro
- patch_rag_completo
- patch_rag_completo_v2
- patch_rag_consolidado_stop
- patch_rag_final
- patch_rag_gemini
- patch_rag_intent_final
- patch_unificar_rag
- pesquisar_e_aprender
- pesquisar_fonte_conhecimento
- quality
- readme_generator
- rebuild_skills
- recall
- repair_agent
- repair_executor
- rollback
- salvar_fonte_web
- self_improve
- sim
- status_monitor
- status_sistema
- suggestion_analyzer
- suggestion_approver
- suggestion_manager
- summarize_help
- sync_manager
- syntax_checker
- system_sync
- termux_knowledge
- termux_tools
- test_runner
- teste3
- teste4
- teste_tool
- teste_tool2
- tool_auditor
- tool_discovery
- tool_manager
- tool_validator
- universal_executor
- update_manager
- validation_bridge
- ver_armazenamento
- ver_bateria
- ver_clipboard
- ver_data_hora
- ver_disco
- ver_hora
- ver_localizacao
- ver_logs
- ver_memoria
- ver_rede
- ver_temperatura
- ver_volume
- ver_wifi
- vibrar
- workspace_manager

Não invente outras ações.

IMPORTANTE

- "editar_html" NÃO é uma ação.
- "editar_html" é uma ferramenta.
- Ferramentas são executadas usando "executar_script".
- Comandos Linux/Bash usam "executar_comando".
- Scripts Python existentes usam "executar_script".
- Conversas e explicações usam "conversar".
- Não transforme uma operação solicitada pelo usuário em conversa.
- Não transforme uma pergunta conceitual em execução.
- Não invente comandos quando uma ferramenta específica já existe.
- Não invente nomes de ferramentas.
- Não execute comandos destrutivos como rm, mkfs, dd, shutdown ou reboot, salvo quando forem explicitamente necessários e autorizados.

FORMATO OBRIGATÓRIO

Responda SOMENTE com JSON válido.

Não use Markdown.
Não use blocos de código.
Não coloque explicações antes ou depois do JSON.

Formato:

{
  "acao": "",
  "params": "",
  "msg": ""
}

"acao" deve ser exatamente uma das ações válidas.

"params" deve conter os parâmetros necessários para a execução.

"msg" deve ser uma mensagem curta e natural.

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


// ============================================================
// HISTÓRICO PERSISTENTE NO FIREBASE
// Mantém somente as últimas 5 conversas.
// ============================================================
async function salvarHistoricoFirebase(entrada, acao, resposta, ok) {
    try {
        if (!db) {
            console.log("Firebase indisponível para histórico.");
            return;
        }

        const refHistorico = db.ref("nexus/historico");
        const snapshot = await refHistorico.once("value");

        let historico = snapshot.val() || [];

        if (!Array.isArray(historico)) {
            historico = Object.values(historico);
        }

        historico.push({
            timestamp: Date.now(),
            entrada: String(entrada || ""),
            acao: String(acao || ""),
            resposta: String(resposta || ""),
            ok: ok !== false
        });

        // Mantém somente as 5 conversas mais recentes.
        historico = historico.slice(-5);

        await refHistorico.set(historico);

        console.log(
            "Firebase histórico atualizado:",
            historico.length,
            "conversas"
        );

    } catch (erro) {
        console.log(
            "Falha ao salvar histórico Firebase:",
            erro.message
        );
    }
}

// --- ROTAS API ---



// ==========================================
// ANÚNCIO MULTIMÍDIA
// Recebe produto + imagens + vídeo
// em uma única requisição multipart.
// ==========================================

const diretorioUploadsAnuncio = path.join(
    CONFIG.ROOT,
    "workspace",
    "uploads_anuncios"
);

fs.mkdirSync(
    diretorioUploadsAnuncio,
    { recursive: true }
);

const storageAnuncio = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, diretorioUploadsAnuncio);
    },

    filename: (req, file, cb) => {
        const extensao = path.extname(file.originalname || "");
        const nomeSeguro =
            path.basename(
                file.originalname || "arquivo",
                extensao
            )
            .replace(/[^a-zA-Z0-9_-]/g, "_");

        cb(
            null,
            Date.now() +
            "_" +
            nomeSeguro +
            extensao
        );
    }
});

const uploadAnuncio = multer({
    storage: storageAnuncio,
    limits: {
        files: 11,
        fileSize: 200 * 1024 * 1024
    }
});

app.post(
    "/api/anuncio-multimidia",
    uploadAnuncio.fields([
        {
            name: "video",
            maxCount: 1
        },
        {
            name: "imagens",
            maxCount: 10
        },
        {
            name: "imagens[]",
            maxCount: 10
        }
    ]),
    async (req, res) => {

        const arquivosCriados = [];

        try {

            console.log("==========================================");
            console.log("🎨 CRIADOR DE ANÚNCIO MULTIMÍDIA");
            console.log("==========================================");

            // ------------------------------------------
            // DADOS DO PRODUTO
            // ------------------------------------------

            const dadosRaw =
                req.body?.dados ||
                req.body?.produto;

            if (!dadosRaw) {
                return res.status(400).json({
                    ok: false,
                    erro:
                        "Envie os dados do produto no campo 'dados'."
                });
            }

            let produto;

            try {
                produto =
                    typeof dadosRaw === "string"
                        ? JSON.parse(dadosRaw)
                        : dadosRaw;
            } catch (erro) {
                return res.status(400).json({
                    ok: false,
                    erro:
                        "JSON do produto inválido.",
                    detalhe: erro.message
                });
            }

            if (
                !produto ||
                typeof produto !== "object" ||
                Array.isArray(produto)
            ) {
                return res.status(400).json({
                    ok: false,
                    erro:
                        "Os dados do produto devem ser um objeto JSON."
                });
            }

            // ------------------------------------------
            // NOME DO HTML
            // ------------------------------------------

            const nomeBase =
                String(
                    produto.nome ||
                    produto.produto ||
                    "anuncio_multimidia"
                )
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/[^a-zA-Z0-9_-]/g, "_")
                .replace(/^_+|_+$/g, "")
                .toLowerCase();

            const nomeHtml =
                nomeBase +
                "_" +
                Date.now() +
                ".html";

            // ------------------------------------------
            // IMAGENS
            // ------------------------------------------

            const camposImagens = [
                ...(req.files?.imagens || []),
                ...(req.files?.["imagens[]"] || [])
            ];

            const imagens = camposImagens.map(
                arquivo => {
                    arquivosCriados.push(
                        arquivo.path
                    );

                    return arquivo.path;
                }
            );

            // ------------------------------------------
            // VÍDEO
            // ------------------------------------------

            const arquivoVideo =
                req.files?.video?.[0];

            if (!arquivoVideo) {
                return res.status(400).json({
                    ok: false,
                    erro:
                        "Nenhum vídeo foi enviado. Use o campo 'video'."
                });
            }

            arquivosCriados.push(
                arquivoVideo.path
            );

            // ------------------------------------------
            // MONTA PRODUTO PARA O PYTHON
            // ------------------------------------------

            produto.imagens = imagens;
            produto.video = arquivoVideo.path;
            produto._nome_html = nomeHtml;

            console.log(
                "Produto:",
                produto.nome || "Sem nome"
            );

            console.log(
                "Imagens:",
                imagens.length
            );

            console.log(
                "Vídeo:",
                arquivoVideo.originalname
            );

            // ------------------------------------------
            // EXECUTA CRIADOR PYTHON
            // ------------------------------------------

            const script =
                path.join(
                    CONFIG.ROOT,
                    "nexus_tools",
                    "criar_anuncio_multimidia.py"
                );

            execFile(
                "python3",
                [
                    script,
                    nomeHtml,
                    JSON.stringify(produto)
                ],
                {
                    cwd: CONFIG.ROOT,
                    timeout: 180000,
                    maxBuffer: 20 * 1024 * 1024,
                    env: process.env
                },
                async (erro, stdout, stderr) => {

                    // ----------------------------------
                    // LIMPA UPLOADS TEMPORÁRIOS
                    // ----------------------------------

                    for (
                        const arquivo of arquivosCriados
                    ) {
                        try {
                            await fsp.unlink(
                                arquivo
                            );
                        } catch (_) {}
                    }

                    if (erro) {

                        console.error(
                            "❌ Erro anúncio multimídia:",
                            erro.message
                        );

                        return res.status(500).json({
                            ok: false,
                            erro: erro.message,
                            stdout: stdout || "",
                            stderr: stderr || ""
                        });
                    }

                    console.log(
                        "✅ Anúncio multimídia criado."
                    );

                    return res.json({
                        ok: true,
                        ferramenta:
                            "criar_anuncio_multimidia.py",
                        resultado:
                            stdout || "",
                        stderr:
                            stderr || "",
                        produto: {
                            nome:
                                produto.nome || "",
                            preco:
                                produto.preco || ""
                        },
                        arquivos: {
                            imagens:
                                imagens.length,
                            video: true
                        },
                        html:
                            "https://nexus-termux.onrender.com/html_gerados/" +
                            nomeHtml
                    });
                }
            );

        } catch (erro) {

            for (
                const arquivo of arquivosCriados
            ) {
                try {
                    await fsp.unlink(
                        arquivo
                    );
                } catch (_) {}
            }

            console.error(
                "❌ Erro rota anúncio:",
                erro
            );

            return res.status(500).json({
                ok: false,
                erro: erro.message
            });
        }
    }
);


// ==========================================
// EXECUTOR DIRETO DE FERRAMENTAS PYTHON
// Usado pelo botão "Executar Script" do Dashboard
// Não depende do Gemini.
// ==========================================

app.post("/api/script", async (req, res) => {
    try {
        const { ferramenta, args = [] } = req.body || {};

        if (!ferramenta) {
            return res.status(400).json({
                erro: "Nome da ferramenta não informado."
            });
        }

        if (!Array.isArray(args)) {
            return res.status(400).json({
                erro: "args deve ser uma lista."
            });
        }

        // Limita argumentos para evitar abuso do executor.
        if (args.length > 20) {
            return res.status(400).json({
                erro: "Quantidade máxima de argumentos excedida."
            });
        }

        for (const arg of args) {
            if (typeof arg !== "string") {
                return res.status(400).json({
                    erro: "Todos os argumentos devem ser texto."
                });
            }
        }

        // Aceita somente nome simples de arquivo/ferramenta.
        // Bloqueia caminhos, espaços e comandos de shell.
        if (!/^[a-zA-Z0-9_-]+(?:\\.py)?$/.test(ferramenta)) {
            return res.status(400).json({
                erro: "Nome de ferramenta inválido."
            });
        }

        const nome = ferramenta.endsWith(".py")
            ? ferramenta
            : ferramenta + ".py";

        const caminho = path.join(
            CONFIG.ROOT,
            "nexus_tools",
            nome
        );

        // Impede acesso fora de nexus_tools.
        const raizTools = path.resolve(
            CONFIG.ROOT,
            "nexus_tools"
        );

        const caminhoReal = path.resolve(caminho);

        if (
            caminhoReal !== raizTools &&
            !caminhoReal.startsWith(raizTools + path.sep)
        ) {
            return res.status(403).json({
                erro: "Acesso ao caminho não permitido."
            });
        }

        if (!fs.existsSync(caminhoReal)) {
            return res.status(404).json({
                erro: `Ferramenta não encontrada: ${nome}`
            });
        }

        console.log("==========================================");
        console.log("🔧 EXECUTOR DIRETO DO DASHBOARD");
        console.log("Ferramenta:", nome);
        console.log("Arquivo:", caminhoReal);
        console.log("==========================================");

        execFile(
            "python3",
            [caminhoReal, ...args],
            {
                cwd: CONFIG.ROOT,
                timeout: 120000,
                maxBuffer: 10 * 1024 * 1024,
                env: process.env
            },
            (erro, stdout, stderr) => {

                if (erro) {
                    console.error(
                        "❌ Erro ao executar ferramenta:",
                        erro.message
                    );

                    return res.status(500).json({
                        ok: false,
                        erro: erro.message,
                        stdout: stdout || "",
                        stderr: stderr || ""
                    });
                }

                console.log("✅ Ferramenta executada:", nome);

                return res.json({
                    ok: true,
                    ferramenta: nome,
                    resultado: stdout || stderr || "Executado com sucesso."
                });
            }
        );

    } catch (erro) {
        console.error("❌ Erro /api/script:", erro);

        return res.status(500).json({
            ok: false,
            erro: erro.message
        });
    }
});

app.post("/api/chat", async (req, res) => {
    const { texto, voz } = req.body;
    const brain = await syncBrain();

    // NEXUS DIRECT SKILL ROUTER
    // Prioriza frases explicitamente registradas em skills.json
    // antes do processamento inteligente/IA.
    let intentSkillDireta = null;

    try {
        const catalogoSkillsDireto = require("./skills.json");
        const skillsDiretas = catalogoSkillsDireto.skills || {};

        const entradaSkillDireta = texto
            .toLowerCase()
            .replace(/nexus[,\\s:]*/g, "")
            .trim();

        for (const nomeSkill of Object.keys(skillsDiretas)) {
            const skill = skillsDiretas[nomeSkill];

            if (!skill || !Array.isArray(skill.frases)) {
                continue;
            }

            const encontrouFrase = skill.frases.some(frase => {
                const f = String(frase).toLowerCase().trim();
                return f && entradaSkillDireta === f;
            });

            if (encontrouFrase) {
                intentSkillDireta = {
                    acao: nomeSkill,
                    params: "",
                    executor: skill.executor || "python",
                    autoBuild: false,
                    msg: "Executando skill registrada diretamente."
                };

                console.log(
                    "🎯 SKILL DIRETA:",
                    entradaSkillDireta,
                    "=>",
                    nomeSkill
                );

                break;
            }
        }

    } catch (e) {
        console.log(
            "Erro no roteador direto de skills:",
            e.message
        );
    }

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

    const textoNormalizado = texto
        .replace(/^nexus[\s,:-]*/i, "")
        .trim();

    const textoEditarHTML = textoNormalizado
        .match(/^editar[_\s]+html\s+(.+)$/i);

    const textoExecutarScript = textoNormalizado
        .match(/^executar[_\s]+script\s+(.+)$/i);

    // ============================================================
    // ROTEADOR DE NOVOS GATILHOS DE FERRAMENTAS
    // Prioridade: gerar+executar > gerar > executar > gerador HTML
    // ============================================================
    const intentGerarEExecutarFerramenta =
        detectarGerarEExecutarFerramenta(texto);

    const intentGerarFerramenta =
        detectarGerarFerramenta(texto);

    const intentExecutarFerramenta =
        detectarExecutarFerramenta(texto);

    const intentGerarCodigo =
        detectarGerarCodigo(texto);

    if (intentGerarEExecutarFerramenta) {
        intent = intentGerarEExecutarFerramenta;

        console.log(
            "🚀🔧 GATILHO GERAR + EXECUTAR:",
            intent.params
        );

    } else if (intentGerarFerramenta) {
        intent = intentGerarFerramenta;

        console.log(
            "🛠️ GATILHO GERAR FERRAMENTA:",
            intent.params
        );

    } else if (intentExecutarFerramenta) {
        intent = intentExecutarFerramenta;

        console.log(
            "▶️ GATILHO EXECUTAR FERRAMENTA:",
            intent.params
        );

    } else if (intentGerarCodigo) {
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
            intentSkillDireta ||
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


// Normalização de ações válidas
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

    // Retorno antecipado somente para conversa
    if (
        intent.acao === "conversar" &&
        intent.msg &&
        intent.msg.trim()
    ) {
        respostaFinal = intent.msg;
        intent.params = intent.params || "";

        return res.json({
            nexus: respostaFinal,
            intent,
            shell: execResult
        });
    }

}
// Lógica de Ação

switch (intent.acao) {

    case "status_sistema":
        try {
            const { execSync } = require("child_process");

            respostaFinal = execSync(
                `python3 nexus_tools/command_router.py status_sistema`,
                {
                    cwd: CONFIG.ROOT,
                    encoding: "utf8"
                }
            ).trim();

        } catch (e) {
            respostaFinal =
                "Erro ao executar status_sistema: " + e.message;
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








    case "executar_ferramenta":








        /*








         * GATILHO DE EXECUÇÃO DE FERRAMENTA








         * Reaproveita o executor oficial de executar_script.








         */








        intent.acao = "executar_script";








        intent.params = (intent.params || "").trim();









        if (!intent.params) {








            respostaFinal =








                "Informe o nome da ferramenta que deseja executar.";








            break;








        }









        // FALLTHROUGH INTENCIONAL









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
            // NORMALIZAÇÃO: criar_arquivo
            // file_creator.py espera: arquivo <nome>
            // O usuário envia: criar_arquivo <nome>
            // ============================================================
            if (tool === "criar_arquivo") {
                const nomeArquivo = (argumentosFerramenta || "").trim();

                if (!nomeArquivo) {
                    respostaFinal =
                        "Uso: criar_arquivo <nome>";
                    break;
                }

                argumentosFerramenta =
                    "arquivo " + nomeArquivo;
            }

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

                const argumentosPython = argumentosFerramenta
                    ? argumentosFerramenta.match(/"[^"]*"|'[^']*'|\S+/g)?.map(arg => {
                        if (
                            (arg.startsWith('"') && arg.endsWith('"')) ||
                            (arg.startsWith("'") && arg.endsWith("'"))
                        ) {
                            return arg.slice(1, -1);
                        }
                        return arg;
                    }) || []
                    : [];

                console.log(
                    "🐍 EXECUTANDO PYTHON:",
                    script,
                    "ARG:",
                    JSON.stringify(argumentosPython)
                );

                respostaFinal = execFileSync(
                    "python3",
                    [script, ...argumentosPython],
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

    // SALVA AS 5 ÚLTIMAS CONVERSAS NO FIREBASE
    await salvarHistoricoFirebase(
        texto,
        intent.acao,
        respostaFinal,
        execResult ? execResult.success : true
    );

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
// API_COMANDOS_FUNCIONANDO
// -------------------------------------------------------
app.get("/api/comandos-funcionando", async (req, res) => {
    try {
        if (!db) {
            return res.json({
                success: false,
                comandos: [],
                erro: "Firebase indisponível."
            });
        }

        const snapshot = await db
            .ref("nexus/comandos_funcionando")
            .once("value");

        const dados = snapshot.val() || {};

        const comandos = Object.entries(dados)
            .map(([chave, info]) => ({
                chave: chave,
                comando: info && info.comando
                    ? info.comando
                    : chave,
                resultado: info && info.resultado
                    ? info.resultado
                    : "",
                status: info && info.status
                    ? info.status
                    : "funcionando",
                ambiente: info && info.ambiente
                    ? info.ambiente
                    : "",
                ultima_confirmacao: info && info.ultima_confirmacao
                    ? info.ultima_confirmacao
                    : ""
            }))
            .sort((a, b) =>
                String(b.ultima_confirmacao)
                    .localeCompare(String(a.ultima_confirmacao))
            );

        res.json({
            success: true,
            total: comandos.length,
            comandos: comandos
        });

    } catch (erro) {
        console.log(
            "Erro ao consultar comandos funcionando:",
            erro.message
        );

        res.status(500).json({
            success: false,
            comandos: [],
            erro: erro.message
        });
    }
});

// -------------------------------------------------------
// API_SALVAR_PERGUNTA
// -------------------------------------------------------
app.post("/api/salvar-pergunta", async (req, res) => {
    try {
        if (!db) {
            return res.status(503).json({
                success: false,
                erro: "Firebase indisponível."
            });
        }

        const texto = String(req.body.texto || "").trim();

        if (!texto) {
            return res.status(400).json({
                success: false,
                erro: "Pergunta ou comando não informado."
            });
        }

        const tipo = String(
            req.body.tipo || "pergunta"
        ).trim();

        const acao = String(
            req.body.acao || ""
        ).trim();

        const agora = Date.now();

        const dados = {
            texto: texto,
            tipo: tipo,
            acao: acao,
            timestamp: agora,
            data: new Date(agora).toISOString()
        };

        const ref = db
            .ref("nexus/perguntas_salvas")
            .push();

        await ref.set(dados);

        console.log(
            "Pergunta/comando salvo no Firebase:",
            ref.key
        );

        res.json({
            success: true,
            id: ref.key,
            registro: dados
        });

    } catch (erro) {
        console.log(
            "Erro ao salvar pergunta/comando:",
            erro.message
        );

        res.status(500).json({
            success: false,
            erro: erro.message
        });
    }
});

// -------------------------------------------------------
// API_HISTORICO
// -------------------------------------------------------
app.get("/api/historico", async (req, res) => {
    try {
        if (!db) {
            return res.json({
                success: false,
                historico: [],
                erro: "Firebase indisponível."
            });
        }

        const snapshot = await db
            .ref("nexus/historico")
            .once("value");

        let historico = snapshot.val() || [];

        if (!Array.isArray(historico)) {
            historico = Object.values(historico);
        }

        historico = historico.slice(-5).reverse();

        res.json({
            success: true,
            historico: historico
        });

    } catch (erro) {
        console.log(
            "Erro ao consultar histórico Firebase:",
            erro.message
        );

        res.status(500).json({
            success: false,
            historico: [],
            erro: erro.message
        });
    }
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

