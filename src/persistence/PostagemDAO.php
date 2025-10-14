<?php
require_once("dbconfig.php");
require_once("../model/Usuario.php");

/**
 * Entidade responsável por manipular as postagens no banco de dados
 */
class PostagemDAO {
    /**
     * Método responsável por inserir uma postagem do usuário no banco
     * @param Usuario $usuario O autor da postagem
     */
        public function inserir(Usuario $usuario) {
            $con = openCon();
            $postagem = $usuario->getPostagemAtual();
    
            $stmt = $con->prepare("INSERT INTO Forum.Postagem(IdUsuario, Mensagem, DataPostagem, UltimaEdicao) VALUES (?, ?, ?, ?)");
            if (!$stmt) {
                closeCon($con);
                throw new Exception("Erro na preparação da query: " . $con->error);
            }
    
            $idUsuario = $usuario->getId();
            $mensagem = $postagem->getMensagem();
            $dataPostagem = $postagem->getDataPostagem();
            $ultimaEdicao = $postagem->getDataUltimaEdicao();
    
            $stmt->bind_param("isss", $idUsuario, $mensagem, $dataPostagem, $ultimaEdicao);
            
            if (!$stmt->execute()) {
                $stmt->close();
                closeCon($con);
                throw new Exception("Erro ao executar a query: " . $stmt->error);
            }
    
            $stmt->close();
            closeCon($con);
        }
    /**
     * Método responsável por atualizar uma postagem do banco
     * @param Postagem $postagem A postagem a ser atualizada
     */
    public function atualizar(Postagem $postagem) {
        $con = openCon();

        $stmt = $con->prepare("UPDATE Forum.Postagem SET Mensagem = ?, UltimaEdicao = ? WHERE IdPostagem = ?");
        if (!$stmt) {
            closeCon($con);
            throw new Exception("Erro na preparação da query: " . $con->error);
        }

        $mensagem = $postagem->getMensagem();
        $ultimaEdicao = $postagem->getDataUltimaEdicao();
        $idPostagem = $postagem->getId();

        $stmt->bind_param("ssi", $mensagem, $ultimaEdicao, $idPostagem);

        if (!$stmt->execute()) {
            $stmt->close();
            closeCon($con);
            throw new Exception("Erro ao executar a query: " . $stmt->error);
        }

        $stmt->close();
        closeCon($con);
    }

    /**
     * Método responsável por excluir uma postagem do banco
     * @param Postagem $postagem A postagem a ser excluída
     */
    public function excluir(Postagem $postagem) {
        $con = openCon();

        $stmt = $con->prepare("DELETE FROM Forum.Postagem WHERE IdPostagem = ?");
        if (!$stmt) {
            closeCon($con);
            throw new Exception("Erro na preparação da query: " . $con->error);
        }

        $idPostagem = $postagem->getId();

        $stmt->bind_param("i", $idPostagem);

        if (!$stmt->execute()) {
            $stmt->close();
            closeCon($con);
            throw new Exception("Erro ao executar a query: " . $stmt->error);
        }

        $stmt->close();
        closeCon($con);
    }

    /**
     * Método responsável por recuperar todas as postagens do banco
     * @return mixed[] O array contendo as postagens e seus respectivos escritores
     */
    public function recuperarTodas() {
        $con = openCon();

        // Query com JOIN para trazer dados do usuário
        $query = "
            SELECT P.IdPostagem, P.Mensagem, P.DataPostagem, P.UltimaEdicao, U.Nome
            FROM Forum.Postagem AS P
            INNER JOIN Forum.Usuario AS U ON P.IdUsuario = U.IdUsuario
            ORDER BY P.IdPostagem ASC
        ";

        $res = mysqli_query($con, $query);
        if (!$res) {
            closeCon($con);
            throw new Exception("Erro ao executar a query: " . mysqli_error($con));
        }

        // Retorna array associativo
        $rows = [];
        if (mysqli_num_rows($res) > 0) {
            $rows = mysqli_fetch_all($res, MYSQLI_ASSOC);
        }

        closeCon($con);
        return $rows;
    }


    /**
     * Método responsável por recuperar as postagens de um dado usuário
     * @param Usuario $usuario O autor das postagens
     */
    public function recuperarPorUsuario(Usuario $usuario) {
        $con = openCon();

        // Prepara a query para evitar SQL Injection
        $stmt = $con->prepare("
            SELECT IdPostagem, Mensagem, DataPostagem, UltimaEdicao
            FROM Forum.Postagem
            WHERE IdUsuario = ?
            ORDER BY IdPostagem DESC
        ");
        if (!$stmt) {
            closeCon($con);
            throw new Exception("Erro na preparação da query: " . $con->error);
        }

        // Passa o Id do usuário como inteiro
        $idUsuario = $usuario->getId();
        $stmt->bind_param("i", $idUsuario);
        $stmt->execute();

        $res = $stmt->get_result();
        if (!$res) {
            $stmt->close();
            closeCon($con);
            throw new Exception("Erro ao executar a query: " . $con->error);
        }

        $postagens = [];
        while ($row = $res->fetch_assoc()) {
            $postagem = new Postagem();
            $postagem->Construtor($row);
            $postagens[] = $postagem;
        }

        $stmt->close();
        closeCon($con);

        $usuario->setPostagens($postagens);
    }

    /**
     * Método responsável por recuperar uma postagem pelo seu id
     * @param int $id O id da postagem
     * @return Postagem A postagem
     * @throws Exception Caso tenha ocorrido algum erro
     */
    public function recuperarPorId($id) {
        $con = openCon();

        // Preparando a query para evitar SQL Injection
        $stmt = $con->prepare("SELECT IdPostagem, Mensagem, DataPostagem, UltimaEdicao 
                            FROM Forum.Postagem 
                            WHERE IdPostagem = ?");
        if (!$stmt) {
            closeCon($con);
            throw new Exception("Erro na preparação da query: " . $con->error);
        }

        // Passa o id como inteiro
        $stmt->bind_param("i", $id);
        $stmt->execute();

        $res = $stmt->get_result();
        if (!$res) {
            $stmt->close();
            closeCon($con);
            throw new Exception("Erro ao executar a query: " . $con->error);
        }

        if ($res->num_rows == 0) {
            $stmt->close();
            closeCon($con);
            throw new Exception("Postagem não encontrada.");
        }

        $postagem = new Postagem();
        $postagem->Construtor($res->fetch_array());

        $stmt->close();
        closeCon($con);

        return $postagem;
    }


    /**
     * Método responsável por recuperar todas as postagens do banco
     * @param string $mensagem A mensagem a ser buscada
     * @return mixed[] O array contendo as postagens e seus respectivos escritores
     */
    public function recuperarPorMensagem(string $mensagem) {
        $con = openCon();

        // Prepara a query com JOIN e LIKE
        $stmt = $con->prepare("
            SELECT * 
            FROM Forum.Postagem AS P 
            INNER JOIN Forum.Usuario AS U 
            ON P.IdUsuario = U.IdUsuario 
            WHERE P.Mensagem LIKE ? 
            ORDER BY P.IdPostagem DESC
        ");
        if (!$stmt) {
            closeCon($con);
            throw new Exception("Erro na preparação da query: " . $con->error);
        }

        // Adiciona os '%' para o LIKE
        $param = "%$mensagem%";
        $stmt->bind_param("s", $param);

        $stmt->execute();
        $res = $stmt->get_result();

        $rows = [];
        if ($res->num_rows > 0) {
            $rows = $res->fetch_all(MYSQLI_ASSOC);
        }

        $stmt->close();
        closeCon($con);

        return $rows;
    }

}
?>