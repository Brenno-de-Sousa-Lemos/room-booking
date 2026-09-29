from database.connection import get_conn
import config


class TermoModel:

    @staticmethod
    def usuario_aceitou_versao_atual(usuario_id: int) -> bool:
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id FROM termos_aceite WHERE usuario_id = %s "
                "AND termo_versao = %s AND politica_versao = %s",
                (usuario_id, config.TERMO_VERSAO, config.POLITICA_VERSAO),
            )
            return cur.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def registrar_aceite(usuario_id: int, ip_origem: str):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO termos_aceite (usuario_id, termo_versao, politica_versao, ip_origem) "
                "VALUES (%s, %s, %s, %s)",
                (usuario_id, config.TERMO_VERSAO, config.POLITICA_VERSAO, ip_origem),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def historico_aceites(usuario_id: int):
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM termos_aceite WHERE usuario_id = %s ORDER BY aceito_em DESC",
                (usuario_id,),
            )
            return cur.fetchall()
        finally:
            conn.close()