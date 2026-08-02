# Terraform

Data:
2026-08-01T17:54:44.193830

# Terraform

## Definição
O Terraform é uma ferramenta de código aberto, desenvolvida pela HashiCorp, utilizada para a automação de infraestrutura. Ele permite definir, provisionar e gerenciar recursos de nuvem (como AWS, Azure, Google Cloud) e serviços locais por meio de arquivos de configuração declarativos. O conceito central do Terraform é a **Infraestrutura como Código (IaC)**, que permite tratar a infraestrutura da mesma forma que o código de uma aplicação, facilitando o versionamento, o teste e a reprodutibilidade.

## Funcionamento
O funcionamento do Terraform baseia-se em um fluxo de trabalho dividido em três etapas principais:

1.  **Escrita (Write):** O usuário define a infraestrutura desejada utilizando a linguagem **HCL (HashiCorp Configuration Language)**. Os arquivos de configuração (.tf) descrevem quais recursos (instâncias de servidores, bancos de dados, redes) devem existir.
2.  **Planejamento (Plan):** Ao executar o comando `terraform plan`, o Terraform compara o estado atual da infraestrutura (armazenado em um arquivo chamado `terraform.tfstate`) com a configuração desejada escrita nos arquivos. Ele gera um plano de execução que detalha quais ações serão tomadas (criação, alteração ou exclusão de recursos).
3.  **Aplicação (Apply):** Ao executar o comando `terraform apply`, o Terraform utiliza provedores (plugins que se conectam às APIs dos serviços de nuvem) para executar as chamadas de API necessárias e colocar a infraestrutura no estado desejado.

## Aplicações
*   **Provisionamento Multi-Cloud:** Gerenciar recursos em diferentes provedores de nuvem simultaneamente com uma única ferramenta.
*   **Ambientes Reprodutíveis:** Criar ambientes de desenvolvimento, homologação e produção idênticos, garantindo que o que funciona em um também funcionará no outro.
*   **Gerenciamento de Ciclo de Vida:** Adicionar, atualizar ou destruir recursos de infraestrutura de forma controlada.
*   **Automação de CI/CD:** Integrar o provisionamento de infraestrutura em pipelines de integração e entrega contínua.

## Vantagens
*   **Independência de Fornecedor:** Permite gerenciar diversos provedores em uma linguagem unificada.
*   **Estado (State):** O arquivo de estado rastreia quem criou o quê e mapeia os recursos reais para a configuração, permitindo identificar derivações na configuração (*drift*).
*   **Simulação (Dry Run):** O comando `plan` permite ver exatamente o que será alterado antes de qualquer impacto real no ambiente.
*   **Comunidade e Ecossistema:** Possui um vasto conjunto de módulos prontos mantidos pela comunidade e pelos próprios provedores de nuvem.
*   **Gerenciamento de Dependências:** O Terraform constrói um gráfico de dependências, garantindo que os recursos sejam criados ou destruídos na ordem correta.

## Limitações
*   **Complexidade do Estado:** O arquivo de estado é um ponto crítico. Se corrompido ou perdido, o Terraform perde a referência sobre a infraestrutura existente, exigindo intervenção manual complexa para recuperar o gerenciamento.
*   **Curva de Aprendizado:** O uso de HCL e a compreensão de conceitos como módulos, variáveis e state management exigem tempo de estudo.
*   **Gerenciamento de Configuração Interna:** O Terraform é excelente para provisionar infraestrutura, mas não é a ferramenta ideal para configurar o interior do sistema operacional (como instalar softwares específicos ou gerenciar arquivos de configuração dentro de um servidor), para isso, ferramentas como Ansible são mais adequadas.
*   **Limitações dos Provedores:** A qualidade e a agilidade da atualização dos recursos no Terraform dependem da manutenção dos plugins feitos pelos provedores de nuvem.

## Referências Oficiais
*   **Documentação do Terraform (HashiCorp):** https://developer.hashicorp.com/terraform/docs
*   **Terraform Registry (Módulos e Providers):** https://registry.terraform.io/
*   **GitHub Oficial:** https://github.com/hashicorp/terraform
