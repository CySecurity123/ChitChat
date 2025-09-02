<?php
require_once("dbconfig.php");
require_once("../model/Usuario.php");

/**
 * Entidade responsável por manipular os usuários no banco de dadoss
 */
class UsuarioDAO {
    /**
     * Método responsável por inserir um usuário no banco
     * @param Usuario $usuario O usuário a ser inserido
     * @throws Exception Se já existir no banco algum usuário com o mesmo login
     */
    public function inserir(Usuario $usuario) {
        $con = openCon();

        // Verifica se o login já existe
        $stmt = mysqli_prepare($con, "SELECT * FROM Forum.Usuario WHERE Login = ?");
        $login = $usuario->getLogin();
        mysqli_stmt_bind_param($stmt, "s", $login);
        mysqli_stmt_execute($stmt);
        $res = mysqli_stmt_get_result($stmt);

        if (mysqli_num_rows($res) == 1) {
            mysqli_stmt_close($stmt);
            closeCon($con);
            throw new Exception("Já existe um usuário com este login!");
        }
        mysqli_stmt_close($stmt);

        // Cria hash da senha
        $senhaHash = password_hash($usuario->getSenha(), PASSWORD_DEFAULT);

        // Inserção segura
        $stmt = mysqli_prepare(
            $con,
            "INSERT INTO Forum.Usuario (Login, Nome, Senha, Foto) VALUES (?, ?, ?, ?)"
        );

        $login = $usuario->getLogin();
        $nome  = $usuario->getNome();
        $foto  = $usuario->getFoto();

        mysqli_stmt_bind_param(
            $stmt,
            "ssss",
            $login,
            $nome,
            $senhaHash,
            $foto
        );

        mysqli_stmt_execute($stmt);

        mysqli_stmt_close($stmt);
        closeCon($con);
    }

    /**
     * Método responsável por autenticar um usuário
     * @param Usuario $usuario O usuário a ser autenticaado
     * @throws Exception Se o login ou a senha forem inválidos
     */
    public function login(Usuario $usuario) {
        $con = openCon();

        // Busca apenas pelo login
        $stmt = $con->prepare("SELECT * FROM Forum.Usuario WHERE Login = ?");
        if (!$stmt) {
            throw new Exception("Erro na preparação da query: " . $con->error);
        }

        $login = $usuario->getLogin();
        $stmt->bind_param("s", $login);
        $stmt->execute();
        $res = $stmt->get_result();

        if ($res->num_rows == 0) {
            throw new Exception("Usuário ou senha inválidos.");
        }

        $row = $res->fetch_assoc();

        // Verifica a senha informada contra o hash salvo no banco
        if (!password_verify($usuario->getSenha(), $row['Senha'])) {
            throw new Exception("Usuário ou senha inválidos.");
        }

        // Se passou, popula o objeto
        $row['Senha'] = "";
        $usuario->Construtor(array_values($row));

        $stmt->close();
        closeCon($con);
    }

    
    /**
     * Método responsável por atualizar um usuário
     * @param Usuario $usuario O usuário a ser atualizado
     * @throws Exception Se o nome de usuário inserido já estiver sendo em uso por outro
     */
    public function atualizar(Usuario $usuario) {
        $con = openCon();

        // Verifica se existe um usuário com o mesmo Id e Login
        $stmt = $con->prepare("SELECT * FROM Forum.Usuario WHERE IdUsuario = ? AND Login = ?");
        $id = $usuario->getId();
        $login = $usuario->getLogin();
        $stmt->bind_param("is", $id, $login);
        $stmt->execute();
        $res = $stmt->get_result();

        if ($res->num_rows == 0) {
            // Verifica se já existe outro usuário com o mesmo login
            $stmt->close();
            $stmt = $con->prepare("SELECT * FROM Forum.Usuario WHERE Login = ?");
            $stmt->bind_param("s", $login);
            $stmt->execute();
            $res = $stmt->get_result();

            if ($res->num_rows == 1) {
                $stmt->close();
                closeCon($con);
                throw new Exception("Este nome de usuário já está em uso.");
            }
        }

        $stmt->close();

        // Gera hash da senha antes de atualizar
        $senhaHash = password_hash($usuario->getSenha(), PASSWORD_DEFAULT);

        // Atualiza os dados do usuário
        $stmt = $con->prepare("UPDATE Forum.Usuario SET Login = ?, Nome = ?, Senha = ?, Foto = ? WHERE IdUsuario = ?");
        $nome = $usuario->getNome();
        $foto = $usuario->getFoto();
        $stmt->bind_param("ssssi", $login, $nome, $senhaHash, $foto, $id);
        $stmt->execute();

        $stmt->close();
        closeCon($con);
    }


    /**
     * Método responsável por excluir um usuário do banco
     * @param Usuario $usuario O usuário a ser excluído
     */
    public function excluir(Usuario $usuario) {
        $con = openCon();
        $query = "DELETE FROM Forum.Usuario WHERE "
                 ."IdUsuario = ".$usuario->getId().";";
        mysqli_query($con, $query);
        closeCon($con);
    }

    /**
     * Método responsável por recuperar um usuário através do seu id no banco
     * @param int $id O id do usuário
     * @return Usuario O usuário a ser recuperado
     */
    public function recuperarPorId(int $id) {
        $con = openCon();
        $query = "SELECT * FROM Forum.Usuario WHERE "
                 ."IdUsuario = ".$id.";";
        $res = mysqli_query($con, $query);
        $usuario = new Usuario();
        $usuario->Construtor(mysqli_fetch_array($res));
        closeCon($con);
        return $usuario;
    }

    /**
     * Método responsável por recuperar um usuário através do id de sua postagem
     * @param int $idPost O id da postagem
     * @return Usuario O autor da postagem
     * @throws Exception Caso tenha ocorrido algum erro na query
     */
    public function recuperarPorIdPost($idPost) {
        $con = openCon();
        $query = "SELECT U.* FROM Forum.Postagem AS P INNER JOIN Forum.Usuario AS U ON "
                 ."P.IdUsuario = U.IdUsuario WHERE "
                 ."P.IdPostagem = ".$idPost.";";
        $res = mysqli_query($con, $query);
        if (!$res)
            throw new Exception("Erro: ".mysqli_error($con)."<br/>Na query: ".$query);
        $usuario = new Usuario();
        $usuario->Construtor(mysqli_fetch_array($res));
        closeCon($con);
        return $usuario;
    }
}
?>