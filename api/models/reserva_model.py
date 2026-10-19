from database.connection import get_conn

BASE_SELECT = (
    "SELECT r.id, r.sala_id, s.nome AS sala_nome, s.localizacao AS sala_localizacao, "
    "r.professor_id, u.nome AS professor_nome, r.titulo, r.descricao, "
    "r.inicio, r.fim, r.google_event_id, r.sincronizado "
    "FROM reservas r "
    "JOIN salas s ON s.id = r.sala_id "
    "JOIN usuarios u ON u.id = r.professor_id "
    "WHERE r.excluido_em IS NULL"
)


def _travar_sala_e_checar_conflito(cur, sala_id, inicio, fim, ignorar_id=None):
    """Trava a linha da sala (serializa reservas concorrentes) e verifica sobreposição."""
    cur.execute(
        "SELECT id FROM salas WHERE id = %s AND ativo = 1 AND excluido_em IS NULL FOR UPDATE",
        (sala_id,),
    )
    if not cur.fetchone():
        raise LookupError("Sala não encontrada ou inativa")

    sql = (
        "SELECT id FROM reservas WHERE sala_id = %s AND excluido_em IS NULL "
        "AND inicio < %s AND fim > %s"
    )
    params = [sala_id, fim, inicio]
    if ignorar_id:
        sql += " AND id <> %s"
        params.append(ignorar_id)
    cur.execute(sql + " LIMIT 1", params)
    if cur.fetchone():
        raise ValueError("Já existe uma reserva para esta sala neste horário")


class ReservaModel:

    @staticmethod
    def criar(sala_id, professor_id, titulo, descricao, inicio, fim):
        conn = get_conn()
        try:
            conn.start_transaction()
            cur = conn.cursor(dictionary=True)
            _travar_sala_e_checar_conflito(cur, sala_id, inicio, fim)
            cur.execute(
                "INSERT INTO reservas (sala_id, professor_id, titulo, descricao, inicio, fim) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (sala_id, professor_id, titulo, descricao, inicio, fim),
            )
            rid = cur.lastrowid
            conn.commit()
            return rid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def atualizar(rid, sala_id, titulo, descricao, inicio, fim):
        conn = get_conn()
        try:
            conn.start_transaction()
            cur = conn.cursor(dictionary=True)
            _travar_sala_e_checar_conflito(cur, sala_id, inicio, fim, ignorar_id=rid)
            cur.execute(
                "UPDATE reservas SET sala_id = %s, titulo = %s, descricao = %s, "
                "inicio = %s, fim = %s WHERE id = %s AND excluido_em IS NULL",
                (sala_id, titulo, descricao, inicio, fim, rid),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def listar(sala_id=None, professor_id=None, incluir_passadas=False):
        sql = BASE_SELECT
        params = []
        if not incluir_passadas:
            sql += " AND r.fim >= NOW()"
        if sala_id:
            sql += " AND r.sala_id = %s"
            params.append(sala_id)
        if professor_id:
            sql += " AND r.professor_id = %s"
            params.append(professor_id)
        sql += " ORDER BY r.inicio"

        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def obter_por_id(rid: int):
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(BASE_SELECT + " AND r.id = %s", (rid,))
            return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def excluir_logico(rid: int):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE reservas SET excluido_em = NOW() WHERE id = %s AND excluido_em IS NULL",
                (rid,),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def marcar_sincronizacao(rid: int, event_id, sincronizado: bool):
        """COALESCE: se event_id vier None, preserva o id do evento que já existia."""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE reservas SET google_event_id = COALESCE(%s, google_event_id), "
                "sincronizado = %s WHERE id = %s",
                (event_id, 1 if sincronizado else 0, rid),
            )
            conn.commit()
        finally:
            conn.close()