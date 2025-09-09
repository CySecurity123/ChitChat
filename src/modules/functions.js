
function mostrarFormDados() {
    $('#dados')[0].style.display = 'none';
    $('#resultado')[0].style.display = 'none';
    $('#postagensDoUsuario')[0].style.display = 'none';
    $('#formDados')[0].style.display = 'block';
    $('#formImagem')[0].style.display = 'block';
    $('#formSenha')[0].style.display = 'block';
}

function esconderFormDados() {
    $('#dados')[0].style.display = 'block';
    $('#resultado')[0].style.display = 'block';
    $('#postagensDoUsuario')[0].style.display = 'block';
    $('#formDados')[0].style.display = 'none';
    $('#formImagem')[0].style.display = 'none';
    $('#formSenha')[0].style.display = 'none';
}

function mostrarFormEditarPost() {
    $('#editPostButton')[0].style.display = 'none';
    $('#post-content')[0].style.display = 'none';
    $('#editPostForm')[0].style.display = 'block';
}

function esconderFormEditarPost() {
    $('#editPostButton')[0].style.display = 'inline-block';
    $('#post-content')[0].style.display = 'block';
    $('#editPostForm')[0].style.display = 'none';
}

console.log("teste")

function ValidadoresDeSenhas() {
    console.log("teste")

    var senha = $('input[name="Senha"]').val();
    var confirmar = $('input[name="Confirmar"]').val();
    var errosSenha = [];

    // Limpa mensagens anteriores
    $('#erro-senha').html('');

    // Regras de senha
    if (senha.length < 8) errosSenha.push("A senha deve ter pelo menos 8 caracteres.");
    if (!/[A-Z]/.test(senha)) errosSenha.push("A senha deve conter pelo menos uma letra maiúscula.");
    if (!/[a-z]/.test(senha)) errosSenha.push("A senha deve conter pelo menos uma letra minúscula.");
    if (!/\d/.test(senha)) errosSenha.push("A senha deve conter pelo menos um número.");
    if (!/[\W_]/.test(senha)) errosSenha.push("A senha deve conter pelo menos um caractere especial.");

    // Verifica se as senhas coincidem
    if (senha !== confirmar) errosSenha.push("As senhas devem ser iguais!");

    // Mostra erros no formulário
    if (errosSenha.length > 0) $('#erro-senha').html(errosSenha.join('<br>'));
    
    // Se houver algum erro, impede envio
    if (errosSenha.length > 0) return false;
    
    return true;
}
