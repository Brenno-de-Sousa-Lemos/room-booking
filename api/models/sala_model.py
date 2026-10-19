from database.connection import get_conn

CAMPOS = "id, nome, tipo, capacidade, localizacao, ativo"


class SalaModel:

    @staticmethod
    def criar(nome, tipo, capacidade, localizacao):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO salas (nome, tipo, capacidade, localizacao) VALUES (%s, %s, %s, %s)",
                (nome, tipo, capacidade, localizacao),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def listar():
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(f"SELECT {CAMPOS} FROM salas WHERE excluido_em IS NULL ORDER BY nome")
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def obter_por_id(sid: int):
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(f"SELECT {CAMPOS} FROM salas WHERE id = %s AND excluido_em IS NULL", (sid,))
            return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def atualizar(sid: int, campos: dict):
        sets = [f"{c} = %s" for c in campos]
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE salas SET {', '.join(sets)} WHERE id = %s AND excluido_em IS NULL",
                list(campos.values()) + [sid],
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def excluir_logico(sid: int) -> bool:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM reservas "
                "WHERE sala_id = %s AND excluido_em IS NULL AND fim > NOW()",
                (sid,),
            )
            if cur.fetchone()[0] > 0:
                raise ValueError("A sala possui reservas futuras. Cancele-as antes de excluir.")
            cur.execute(
                "UPDATE salas SET excluido_em = NOW(), ativo = 0 "
                "WHERE id = %s AND excluido_em IS NULL",
                (sid,),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()