console.log('functions.js foi carregado.');

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

function ValidadoresDeSenhas() {
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

// Verifica se jQuery foi carregado
if (typeof jQuery == 'undefined') {
    console.error('jQuery não foi carregado! O script vai parar.');
}

$(document).ready(function() {
    console.log('Documento pronto e jQuery está funcionando.');

    // Manipulação do Modal
    var modal = $('#errorModal');
    var span = $('.close-button');

    // Fecha o modal ao clicar no 'X'
    span.click(function() {
        modal.hide();
    });

    // Fecha o modal ao clicar fora dele
    $(window).click(function(event) {
        if (event.target == modal[0]) {
            modal.hide();
        }
    });

    // Manipulação do formulário de foto com AJAX (usando delegação de evento para robustez)
    $(document).on('submit', '#form-foto', function(e) {
        console.log('Manipulador de envio AJAX acionado!'); // Ponto de depuração
        e.preventDefault(); // Impede o envio padrão

        var formData = new FormData(this);

        $.ajax({
            url: '../controller/usuario.php',
            type: 'POST',
            data: formData,
            processData: false, // Necessário para enviar arquivos
            contentType: false, // Necessário para enviar arquivos
            success: function(response) {
                // Recarrega a página para mostrar a nova foto
                location.reload();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // Extrai e exibe a mensagem de erro no modal
                var errorMessage = 'Ocorreu um erro inesperado.';
                if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
                    errorMessage = jqXHR.responseJSON.message;
                }
                $('#modalErrorMessage').text(errorMessage);
                modal.show();
            }
        });
    });
});
