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
            `python3 nexus_tools/learning_memory.py`,
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


function detectarAmbiente() {
    try {
        const resultado = execSync(
            "python3 nexus_tools/detectar_ambiente.py",
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



// --- CONFIGURAÇÃO ---
const CONFIG = {
    PORT: 3003,
    ROOT: __dirname,
    BRAIN_FILE: path.join(__dirname, "brain.json"),};

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

let brainMemory = null; // Cache do cérebro em memória

// --- CORE UTILS ---

/** Executa comandos shell com Promise e log */
function shell(cmd) {
    console.log(`[SHELL] Executando: ${cmd}`);
    return new Promise((resolve) => {
        const cwdAtual = execSync(
            "python3 nexus_tools/cwd_manager.py get",
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


async function processarIntencao(promptUsuario) {

    // AUTO_CONHECIMENTO_GENERATIVO

    try {

        const { execSync } = require("child_process");

        if (promptUsuario.toLowerCase().startsWith("aprender ")) {

            const consulta = promptUsuario.substring(9).trim();

            const contexto = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${consulta.replace(/"/g,'\\"')}"`,
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
                `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
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
            `python3 nexus_tools/consolidar_conhecimento.py "${promptUsuario.replace(/"/g,'\\"')}"`,
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

            return {
                acao: "conversar",
                msg: consultaConsolidada,
                ragLocal: true
            };

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
                `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
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
            `python3 nexus_tools/memory_lookup.py "${promptUsuario.replace(/"/g, '\"')}"`,
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

            if (memoria.startsWith("AUTO_BUILD:")) {

                return {
                    acao: memoria.replace("AUTO_BUILD:", ""),
                    params: "",
                    autoBuild: true,
                    msg: "Ferramenta será criada automaticamente."
                };

            }

            if (acoesPermitidas.includes(memoria)) {

                return {
                    acao: memoria,
                    params: "",
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
            `python3 nexus_tools/auto_conhecimento_generativo.py "${promptUsuario.replace(/"/g,'\\"')}"`,
            {
                cwd: CONFIG.ROOT,
                encoding: "utf8",
                maxBuffer: 1024 * 1024
            }
        ).trim();

    } catch(e) {

        console.log("AUTO_CONHECIMENTO:", e.message);

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

        return {
            acao: "conversar",
            msg: contextoLocal
        };

    }

    const systemPrompt = `Você é o NEXUS SRE, um sistema operacional inteligente para Termux/Linux.

BASE DE CONHECIMENTO LOCAL

${contextoLocal}

Utilize primeiro o conhecimento local acima.
Se ele não responder completamente à pergunta,
complemente utilizando seu conhecimento geral.


MISSÃO
- Conversar naturalmente.
- Interpretar intenções.
- Responder perguntas.
- Executar comandos quando necessário.

Responda SOMENTE JSON.

Formato:

{
  "acao":"",
  "params":"",
  "msg":""
}

Ações permitidas:

- conversar
- executar_comando
- executar_script
- listar_arquivos
- listar_ferramentas
- buscar_arquivo
- criar_arquivo
- editar_arquivo
- instalar_pacote
- status_sistema
- parar_musica

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

"informações do Termux"
→ termux-info

"testar internet"
→ curl -I https://google.com

Nunca execute comandos destrutivos como:

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

    const intent =
        intentMemoria ||
        await processarIntencao(texto);


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

    
// Lógica de Ação

switch (intent.acao) {

    case "status_sistema":
        respostaFinal = intent.msg || "Sistema operacional pronto.";
        break;

    case "buscar_arquivo":

        try {

            const { execSync } = require("child_process");

            respostaFinal = execSync(
                `python3 nexus_tools/auto_conhecimento_generativo.py "${intent.params || promptUsuario}"`,
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
                        `python3 nexus_tools/cwd_manager.py set "${destino}"`,
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
                        `python3 shell_executor.py ${JSON.stringify(intent.params)}`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8"
                        }
                    );

                    const resultado = JSON.parse(retorno);

                    execResult = resultado;

                    switch (resultado.executor) {

                        case "termux-battery-status": {
                            const bateria = JSON.parse(resultado.stdout);
                            respostaFinal =
                                `Bateria: ${bateria.percentage}%
\n` +
                                `Temperatura: ${bateria.temperature}°C\n` +
                                `Estado: ${bateria.status}`;
                            break;
                        }

                        case "termux-volume": {
                            const volumes = JSON.parse(resultado.stdout);
                            respostaFinal = volumes
                                .map(v => `${v.stream}: ${v.volume}/${v.max_volume}`)
                                .join("\n");
                            break;
                        }

                        case "termux-torch":
                            respostaFinal = "Lanterna acionada com sucesso.";
                            break;

                        default:
                            
switch (resultado.executor) {

    case "termux-battery-status": {
        const bateria = JSON.parse(resultado.stdout);
        respostaFinal =
            `Bateria: ${bateria.percentage}%
` +
            `Temperatura: ${bateria.temperature}°C
` +
            `Estado: ${bateria.status}`;
        break;
    }

    case "termux-volume": {
        const volumes = JSON.parse(resultado.stdout);
        respostaFinal = volumes
            .map(v => `${v.stream}: ${v.volume}/${v.max_volume}`)
            .join("\n");
        break;
    }

    case "termux-torch":
        respostaFinal = "Lanterna acionada com sucesso.";
        break;

    default:
        respostaFinal =
            resultado.stdout ||
            resultado.stderr ||
            resultado.erro ||
            "Comando executado.";
}

                    }

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
                intent.autoBuild ||
                (
                    !skillsValidacao.skills[chave] &&
                    !intentMap.acoes[chave]
                )
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
                        `python3 nexus_tools/file_creator.py criar_tool ${novaTool} "Ferramenta criada automaticamente pelo Nexus" "${texto}" "print('Ferramenta ${novaTool} criada automaticamente pelo Nexus')"`,
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
                `python3 nexus_tools/command_router.py ${chave}`,
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

