# 💬 ChitChat: Corrigindo Vulnerabilidades em Aplicações Web

Este projeto é uma iniciativa de segurança focada na identificação, correção e mitigação de falhas em uma aplicação web inicialmente desenvolvida por terceiros. O **ChitChat** serve como um ambiente controlado para estudar e praticar a segurança de aplicações, transformando vulnerabilidades conhecidas em lições valiosas.

🔍 **Objetivo Principal:** Transformar uma aplicação web com diversas vulnerabilidades em um sistema mais robusto e seguro, servindo como ferramenta educacional e prática para engenheiros de software e entusiastas de segurança.

🔗 **Repositório Original:** [NESCAU-UFLA/VulnerableWebApp](https://github.com/NESCAU-UFLA/VulnerableWebApp)

---

## 🎯 Sumário

*   [✨ Sobre o Projeto](#-sobre-o-projeto)
*   [🚀 Primeiros Passos](#-primeiros-passos)
    *   [Pré-requisitos](#pré-requisitos)
    *   [Instalação e Execução](#instalação-e-execução)
*   [📖 Funcionalidades da Aplicação](#-funcionalidades-da-aplicação)
*   [🧪 Vulnerabilidades Identificadas](#-vulnerabilidades-identificadas)
*   [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
*   [📂 Estrutura do Projeto](#-estrutura-do-projeto)
*   [🤝 Como Contribuir](#-como-contribuir)
*   [📜 Licença](#-licença)
*   [👥 Autores](#-autores)

---

## ✨ Sobre o Projeto

O **ChitChat** é um fórum simples onde usuários podem compartilhar mensagens através de postagens. Ele foi intencionalmente construído com diversas vulnerabilidades, o que o torna uma plataforma ideal para **testar, aprender e aplicar conhecimentos em segurança da informação**. Nosso trabalho consiste em analisar a aplicação, identificar as falhas e desenvolver soluções para mitigá-las, tornando-o um sistema mais seguro para a interação dos usuários.

### Funcionalidades Atuais:

*   **Usuários Comuns:**
    *   Cadastro, edição e exclusão de contas.
    *   Criação, edição e exclusão de suas próprias postagens.
*   **Administradores:**
    *   Todas as funcionalidades de um usuário comum (exceto exclusão de conta própria).
    *   Capacidade de excluir postagens e contas de outros usuários.

---

## 🚀 Primeiros Passos

Siga as instruções abaixo para configurar e executar o projeto **ChitChat** em sua máquina local.

### Pré-requisitos

Para garantir o funcionamento adequado da aplicação, você precisará ter o **Docker** instalado em seu sistema.

*   🐳 **Docker:** Certifique-se de ter o Docker e o Docker Compose instalados.
    *   [Documentação Oficial do Docker](https://www.docker.com/)

### Instalação e Execução

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/seu-usuario/ChitChat.git
    cd ChitChat
    ```

2.  **Construa e Inicie os Contêineres Docker:**
    No diretório raiz do projeto, execute o seguinte comando:
    ```bash
    docker-compose up --build
    ```
    Este comando construirá as imagens Docker (se necessário) e iniciará os serviços da aplicação (servidor web e banco de dados).

3.  **Acesse a Aplicação:**
    Após os contêineres estarem em execução, abra seu navegador e acesse:
    🌐 [http://localhost:8080](http://localhost:8080)

---

## 📖 Funcionalidades da Aplicação

### Como Usar e Testar:

Para interagir com o ChitChat e explorar suas funcionalidades (ou vulnerabilidades antes da correção!):

1.  **Registro de Usuário:**
    *   Na página inicial, procure por um link ou botão para "Cadastrar" ou "Registrar".
    *   Preencha os campos com um nome de usuário, senha.
    *   Crie uma conta para começar a usar a aplicação.

2.  **Login:**
    *   Após o registro, ou se já tiver uma conta, utilize suas credenciais para fazer login.

3.  **Criação de Postagem:**
    *   Uma vez logado, procure pela opção "Nova Postagem" ou similar.
    *   Escreva uma mensagem no campo de texto e publique-a. Sua postagem aparecerá no fórum.

4.  **Interação:**
    *   Explore as postagens de outros usuários.
    *   Se você for um administrador, tente excluir postagens de outros usuários para testar as permissões.

> 💡 **Dica:** Ao testar, você pode tentar inserir caracteres especiais ou scripts em campos de entrada de texto (como nome de usuário, senha ou conteúdo da postagem) para observar o comportamento da aplicação em relação às vulnerabilidades conhecidas. **Faça isso apenas em um ambiente controlado como este projeto.**

---

## 🧪 Vulnerabilidades Identificadas

Este projeto visa corrigir as seguintes vulnerabilidades presentes na versão original da aplicação. Esta lista serve como um guia para os pontos críticos que estão sendo abordados.

*   **Falta de uma política de senhas robusta:** Permite senhas fracas.
*   **Tratamento de erro inapropriado:** Mensagens de erro detalhadas que podem revelar informações sensíveis.
*   **Falta de proteção a ataques de força bruta:** Ausência de mecanismos para bloquear ou atrasar tentativas repetidas de login.
*   **Informações sensíveis salvas "em claro" no banco de dados:** Senhas e outros dados críticos não são criptografados.
*   **Cross-Site Scripting (XSS):**
    *   **Reflected XSS:** Entradas do usuário refletidas sem sanitização.
    *   **Stored XSS:** Entradas do usuário armazenadas no banco de dados e executadas em futuras visualizações.
*   **SQL Injection:**
    *   **In-band SQLi:** Erros ou resultados visíveis.
    *   **Inferential SQLi (Blind SQLi):** Baseado em respostas booleanas ou temporais.
*   **Unrestricted File Upload:** Permite o upload de arquivos maliciosos para o servidor.
*   **File Inclusion:**
    *   **Local File Inclusion (LFI):** Inclui arquivos locais do servidor.
    *   **Remote File Inclusion (RFI):** Inclui arquivos de servidores remotos.
*   **Command Execution:** Permite a execução de comandos arbitrários no servidor.
*   **Cross-Site Request Forgery (CSRF):** Falta de proteção contra requisições forjadas.

---

## 🛠️ Tecnologias Utilizadas

As seguintes tecnologias são a base para o desenvolvimento e funcionamento do ChitChat:

*   **Frontend:**
    *   `HTML5` e `CSS3`
    *   `JavaScript` e `jQuery` (versão 3.5.2)
*   **Backend:**
    *   `PHP` (versão 7.2.24)
    *   `Apache` (versão 2.4.29)
*   **Banco de Dados:**
    *   `MySQL` (versão 5.7.27)
*   **Containerização:**
    *   `Docker` (versão 28.3.2)
    *   `Docker-compose` (versão 28.3.2)

---

## 📂 Estrutura do Projeto

A organização dos arquivos e diretórios do projeto segue a estrutura abaixo:

```
├── 📁 db/
│   ├── 🗄️ banco.sql
│   └── 📄 forum.mwb
├── 📁 src/
│   ├── 📁 config/
│   │   └── 🐘 geral.php
│   ├── 📁 controller/
│   │   ├── 🐘 postagem.php
│   │   └── 🐘 usuario.php
│   ├── 📁 model/
│   │   ├── 🐘 Postagem.php
│   │   └── 🐘 Usuario.php
│   ├── 📁 modules/
│   │   ├── 📄 functions.js
│   │   ├── 🐘 functions.php
│   │   ├── 📄 jquery-3.5.1.min.js 🚫 (auto-hidden)
│   │   └── 🎨 style.css
│   ├── 📁 persistence/
│   │   ├── 🐘 PostagemDAO.php
│   │   ├── 🐘 UsuarioDAO.php
│   │   └── 🐘 dbconfig.php
│   ├── 📁 uploads/
│   │   ├── 🖼️ default.png
│   │   ├── 🖼️ gatinho.jpeg 🚫 (auto-hidden)
│   │   └── 🖼️ wirebond_mask.png
│   ├── 📁 view/
│   │   ├── 🐘 cadastrar.php
│   │   ├── 🐘 home.php
│   │   ├── 🐘 perfil.php
│   │   ├── 🐘 post.php
│   │   └── 🐘 teste-de-conexao.php
│   └── 🐘 index.php
├── 🚫 .gitignore
├── 🐳 Dockerfile
├── 📜 LICENSE.md
├── 📖 README.md
└── ⚙️ docker-compose.yml
```

## 🤝 Como Contribuir

Sua contribuição é muito bem-vinda para tornar o **ChitChat** um projeto ainda melhor e mais seguro!

### Reportando Problemas (Issues)

Se você encontrar um bug, uma vulnerabilidade ou tiver uma sugestão de melhoria:

1.  Abra uma nova [Issue](https://github.com/seu-usuario/ChitChat/issues) no repositório.
2.  Descreva o problema ou sugestão de forma clara e detalhada. Se for um bug, inclua os passos para reproduzi-lo.

### Sugerindo Recursos (Feature Requests)

Tem uma ideia para uma nova funcionalidade ou melhoria de segurança?

1.  Verifique se já existe uma Issue similar.
2.  Crie uma nova Issue com a tag `feature request` e descreva sua ideia, explicando o valor que ela agrega ao projeto.

---

## 📜 Licença

Este projeto está licenciado sob a licença `MIT`. Veja o arquivo [LICENSE.md](LICENSE.md) para mais detalhes.

---

## �� Autores

A equipe por trás do projeto **ChitChat** é composta por:

*   **Rafael Vasconcelos** - Líder da equipe
*   **Kayque Setubal** - Documentador/QA
*   **Henrique Heruster** - Desenvolvedor