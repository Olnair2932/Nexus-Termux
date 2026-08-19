NEXUS SRE
README - VERSAO ATUAL

==================================================
SOBRE O NEXUS
==================================================

O Nexus SRE é um sistema de inteligência e automação
desenvolvido para executar ferramentas, aprender
conhecimento, gerenciar memória, criar páginas HTML
e automatizar a criação de anúncios multimídia.

O projeto evoluiu de um sistema simples de execução
de scripts para uma plataforma integrada com:

- Node.js
- Python
- Gemini
- Firebase Realtime Database
- Cloudinary
- Render
- Termux
- GitHub

==================================================
STATUS ATUAL
==================================================

NEXUS SRE OPERACIONAL

O sistema possui:

- Dashboard web
- Terminal interativo
- Execução de ferramentas Python
- Sistema de memória
- Aprendizado automático
- Base de conhecimento
- RAG / recuperação de conhecimento
- Firebase Realtime Database
- Geração de páginas HTML
- Edição de HTML com Gemini
- Upload de imagens
- Upload de vídeos
- Criador de anúncios multimídia
- Geração automática de anúncios com Gemini
- Player de vídeo com áudio
- Botão de compra pelo WhatsApp
- Histórico de conversas
- Sistema de auditoria
- Monitoramento do ambiente
- Compatibilidade com Render e Termux

==================================================
CRIADOR DE ANÚNCIOS MULTIMÍDIA
==================================================

O Nexus possui um fluxo completo para criação de
anúncios multimídia.

O usuário pode fornecer:

- Nome do produto
- Preço
- Descrição
- Benefícios
- Número do WhatsApp
- Imagens
- Vídeo

O Dashboard permite selecionar imagens e vídeo
diretamente pelo dispositivo.

O Nexus envia os arquivos para o backend através
da API:

/api/anuncio-multimidia

O servidor recebe os arquivos utilizando Multer.

As imagens e vídeos são processados pelo Python
e enviados para o Cloudinary.

O Gemini é utilizado para gerar a página HTML
do anúncio.

==================================================
FLUXO DO ANÚNCIO
==================================================

Dashboard
    |
    v
Upload de imagens e vídeo
    |
    v
/ api/anuncio-multimidia
    |
    v
Node.js / Express / Multer
    |
    v
criar_anuncio_multimidia.py
    |
    +----> Cloudinary
    |        |
    |        +--> Imagens
    |        |
    |        +--> Vídeo
    |
    +----> Gemini
    |        |
    |        +--> HTML do anúncio
    |
    v
html_gerados/
    |
    v
Página publicada pelo Nexus

==================================================
VÍDEO
==================================================

O Nexus suporta vídeos MP4 enviados pelo usuário.

Os vídeos são armazenados no Cloudinary como
resource_type="video".

O anúncio recebe uma URL segura do Cloudinary.

O player HTML utiliza:

<video controls>

com:

<source ... type="video/mp4">

Foi realizado teste com vídeo contendo áudio,
e o vídeo foi reproduzido corretamente com som.

==================================================
IMAGENS
==================================================

O Dashboard permite enviar imagens do produto.

São aceitas múltiplas imagens.

Os arquivos são enviados para:

nexus/anuncios

no Cloudinary.

As URLs retornadas pelo Cloudinary são utilizadas
na galeria do anúncio.

==================================================
WHATSAPP
==================================================

Os anúncios podem possuir botão de compra pelo
WhatsApp.

Exemplo:

https://wa.me/SEUNUMERO

O número é recebido através dos dados do produto.

==================================================
ARQUITETURA
==================================================

                    NEXUS SRE
                        |
                +-------+-------+
                |               |
             Dashboard       server.js
                |               |
                |        +------+------+
                |        |      |      |
                |      Gemini Python Firebase
                |               |
                |          Nexus Tools
                |               |
                |           Cloudinary
                |
                +--> Upload
                     Imagens
                     Vídeos

==================================================
COMPONENTES PRINCIPAIS
==================================================

server.js

Núcleo Node.js do Nexus.

Responsável por:

- API
- Dashboard
- Execução de ferramentas
- Comunicação com Gemini
- Firebase
- Upload de arquivos
- Execução Python
- Memória
- Histórico
- Ambiente Render/Termux

public/index.html

Dashboard web do Nexus.

Possui:

- Terminal
- Campo de perguntas
- Execução
- Aprendizado
- Visualização de páginas
- Editor HTML com Gemini
- Criador de anúncio multimídia
- Upload de imagens
- Upload de vídeo

nexus_tools/

Diretório das ferramentas Python do Nexus.

Entre as ferramentas utilizadas:

- learning_memory.py
- memory_lookup.py
- consolidar_conhecimento.py
- pesquisar_e_aprender.py
- indexar_conhecimento.py
- auto_conhecimento_generativo.py
- brain_agent.py
- criar_anuncio_multimidia.py
- status_monitor.py

==================================================
MEMÓRIA
==================================================

O Nexus possui memória local e persistente.

Arquivos e estruturas utilizados:

- brain.json
- Firebase Realtime Database

Dados relacionados à memória podem ser
sincronizados com:

nexus/memoria

==================================================
CONHECIMENTO
==================================================

O Nexus possui uma base de conhecimento local.

Estrutura principal:

conhecimento/

Inclui:

- documentos aprendidos
- índice
- conhecimento consolidado

O índice principal é:

conhecimento/indice.json

O Nexus pode pesquisar e aprender novos assuntos
utilizando ferramentas Python.

==================================================
FIREBASE
==================================================

O Firebase Realtime Database é utilizado para
persistência.

Estruturas utilizadas incluem:

nexus/memoria

nexus/conhecimento

nexus/html_gerados

Isso permite manter informações mesmo quando
o ambiente do Render é reiniciado.

==================================================
CLOUDINARY
==================================================

O Cloudinary é utilizado para armazenamento
de mídia.

Imagens:

nexus/anuncios

Vídeos:

nexus/anuncios/videos

O Nexus utiliza as URLs seguras retornadas pelo
Cloudinary para montar os anúncios.

==================================================
RENDER
==================================================

O Nexus está hospedado no Render.

Ambiente detectado:

render

Diretório principal:

/opt/render/project/src

O servidor utiliza Node.js e Python.

==================================================
TERMUX
==================================================

O desenvolvimento e testes também são realizados
através do Termux.

Diretório principal utilizado:

~/sentinela_dev

O projeto pode ser sincronizado com GitHub e
implantado no Render.

==================================================
GITHUB
==================================================

Repositório:

Nexus-Termux

Organização do projeto permite manter o código
versionado e realizar deploy no Render.

==================================================
SEGURANÇA
==================================================

O Nexus possui mecanismos para limitar a execução
de ferramentas.

A API /api/script:

- valida o nome da ferramenta
- limita a quantidade de argumentos
- aceita somente argumentos de texto
- impede caminhos fora de nexus_tools
- executa ferramentas Python controladas
- possui timeout de execução

O projeto também utiliza validação de sintaxe
antes de publicar alterações importantes.

==================================================
EVOLUÇÃO
==================================================

O Nexus evoluiu de um executor de scripts para um
sistema integrado de automação.

Principais evoluções:

1. Execução de ferramentas Python
2. Memória local
3. Memória Firebase
4. Base de conhecimento
5. RAG
6. Aprendizado automático
7. Integração com Gemini
8. Integração com Cloudinary
9. Geração automática de HTML
10. Upload de imagens
11. Upload de vídeos
12. Anúncios multimídia
13. Dashboard com upload
14. Vídeo com áudio funcionando
15. Integração Render + Firebase + GitHub

==================================================
RESULTADO
==================================================

O Nexus atualmente consegue receber os dados de
um produto juntamente com imagens e vídeo, processar
os arquivos, armazenar a mídia no Cloudinary, utilizar
Gemini para gerar o anúncio e publicar uma página HTML
com:

- Produto
- Preço
- Descrição
- Benefícios
- Imagens
- Vídeo
- Áudio do vídeo
- Botão de WhatsApp

O objetivo é continuar evoluindo o Nexus para que
o processo de criação de conteúdo multimídia seja
cada vez mais automático.

==================================================
FIM
==================================================
