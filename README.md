# ChitChat
Este projeto foi desenvolvido por terceiro com diversas vunerabilidades, a proposta é corrigir, testar e mitigar falhas de segurança da aplicação
Repositório original: https://github.com/NESCAU-UFLA/VulnerableWebApp

## Sumário
* <a href="#primeiros-passos">Primeiros passos</a>
  * <a href="#pré-requisitos">Pré-requisitos</a>;
  * <a href="#comando-para-execução-do-projeto">Comando para execução do projeto</a>;
* <a href="#sobre-a-aplicação">Sobre a Aplicação</a>
  * <a href="#vulnerabilidades-listadas-no-projeto-original">Vulnerabilidades listadas no projeto original</a>;
* <a href="#tecnologias-utilizadas">Tecnologias Utilizadas</a>;
* <a href="#diretórios">Diretórios</a>;
* <a href="#autores">Autores</a>.

## Primeiros passos
Antes de começar a usar o projeto certifique-se de seguir os **pré-requisitos** para a base do seu funcionamento.

### Pré-requisitos
* Certifique-se de ter o Docker instalado na maquina segue documentação: <a href="https://www.docker.com/">Docker</a>.

### Comando para execução do projeto
Acessando o diretório do projeto no terminal já com o docker instalado na maquina digite:
docker-compose -u --build e acesse no navegador o https://localhost:8080

## Sobre a Aplicação
Trata-se de um fórum em que os usuários podem compartilhar mensagens entre si através de suas postagens.
* O usuário pode cadastrar, editar e excluir sua conta, além de cadastrar, editar e excluir suas próprias postagens.
* O administrador pode, além das funções já existentes de um usuário comum (com exceção de excluir sua conta), pode excluir as postagens dos demais usuários e suas contas.

### Vulnerabilidades listadas no projeto original
* Falta de uma política de senhas;
* Tratamento de erro inapropriado;
* Falta de proteção a ataques de força bruta;
* Informações sensíveis são salvas "em claro" no banco de dados, ou seja, sem o uso de criptografia;
* *XSS (Cross-Site Scripting)*
  * *Reflected;*
  * *Stored;*
* *SQL Injection*
  * *In-band;*
  * *Inferential;*
* *Unrestricted File Upload;*
* *File Inclusion*
  * *LFI;*
  * *RFI;*
* *Command Execution;*
* *CSRF (Cross-Site Request Forgery).*

## Tecnologias Utilizadas
* HTML5 e CSS3
* JavaScript e jQuery versão 3.5.2
* PHP versão 7.2.24
* Apache versão 2.4.29
* MySQL versão 5.7.27
* Docker versão 28.3.2
* Docker-compose versão 28.3.2

## Diretórios
```sh
D:.
|-- docker-compose.yml
|-- Dockerfile
|-- LICENSE.md
|-- README.md
|-- db
|   |-- banco.sql
|   |-- forum.mwb
|-- docs
|   |-- Diagrama de Classe VWA.png
|   |-- Diagrama ER.png
\-- src
    |-- index.php
    |-- config
    |   |-- geral.php
    |-- controller
    |   |-- postagem.php
    |   |-- usuario.php
    |-- model
    |   |-- Postagem.php
    |   |-- Usuario.php
    |-- modules
    |   |-- functions.js
    |   |-- functions.php
    |   |-- jquery-3.5.1.min.js
    |   |-- style.css
    |-- persistence
    |   |-- dbconfig.php
    |   |-- PostagemDAO.php
    |   |-- UsuarioDAO.php
    |-- uploads
    |   |-- default.png
    |   |-- gatinho.jpeg
    |   |-- wirebond_mask.png
    \-- view
        |-- cadastrar.php
        |-- home.php
        |-- perfil.php
        |-- post.php
        \-- teste-de-conexao.php
```

## Autores
* <b>Rafael Vasconcelos - Líder da equipe</b>
* <b>Kayque Setubal - Documentador/QA</b>
* <b>Henrique Heruster - Desenvolvedor</b> 
