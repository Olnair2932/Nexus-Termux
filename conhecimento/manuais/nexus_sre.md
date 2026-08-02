# Nexus SRE

## Visão geral

O Nexus SRE é um sistema inteligente desenvolvido para Termux/Linux.
Ele combina execução segura de comandos, memória local, RAG e automação.

## Memória

O Nexus utiliza:

- brain.json para memória operacional.
- knowledge.json para conhecimento aprendido.
- pasta conhecimento/manuais para documentação local.

## RAG Local

O sistema consulta primeiro:

1. Documentação local.
2. Conhecimento aprendido.
3. Arquivos do projeto.

Quando encontra informação, responde sem criar ferramentas desnecessárias.

## Dashboard

O Dashboard funciona como terminal inteligente:

- Recebe comandos em linguagem natural.
- Consulta a base local.
- Executa ações autorizadas.
- Exibe resultados.

## Segurança

O Nexus utiliza:

- Backup antes de alterações.
- Validação de ações.
- Registro de eventos.
- Execução controlada.

## Ferramentas

O Nexus possui recursos para:

- Consultar memória.
- Pesquisar arquivos.
- Executar comandos seguros.
- Gerenciar conhecimento.
- Automatizar tarefas.

## Evolução

O Nexus pode aprender novos conhecimentos através da função aprender.

Exemplo:

aprender "tema" "informação"

O conhecimento fica salvo para consultas futuras.
