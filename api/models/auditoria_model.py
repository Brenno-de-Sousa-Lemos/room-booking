from database.connection import get_conn


class AuditoriaModel:

    @staticmethod
    def registrar(usuario_id, usuario_nome, acao, entidade, entidade_id, sucesso, ip_origem):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO logs_auditoria "
                "(usuario_id, usuario_nome, acao, entidade, entidade_id, sucesso, ip_origem) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (usuario_id, usuario_nome, acao, entidade, entidade_id, sucesso, ip_origem),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def listar(usuario_id=None, acao=None, entidade=None, limite=200):
        sql = "SELECT * FROM logs_auditoria WHERE 1=1"
        params = []
        if usuario_id:
            sql += " AND usuario_id = %s"
            params.append(usuario_id)
        if acao:
            sql += " AND acao = %s"
            params.append(acao)
        if entidade:
            sql += " AND entidade = %s"
            params.append(entidade)
        sql += " ORDER BY criado_em DESC LIMIT %s"
        params.append(limite)

        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            conn.close()