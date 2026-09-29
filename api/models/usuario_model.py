from mysql.connector import IntegrityError
from database.connection import get_conn

PERFIS = {"ADMIN", "PROFESSOR", "ALUNO"}
CAMPOS_PUBLICOS = "id, nome, email, perfil, registro, ativo, criado_em"


class UsuarioModel:

    @staticmethod
    def buscar_por_email(email: str):
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, nome, senha_hash, perfil FROM usuarios "
                "WHERE email = %s AND ativo = 1 AND excluido_em IS NULL",
                (email,),
            )
            return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def criar(nome, email, senha_hash, perfil, registro):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, perfil, registro) "
                "VALUES (%s, %s, %s, %s, %s)",
                (nome, email, senha_hash, perfil, registro),
            )
            conn.commit()
            return cur.lastrowid
        except IntegrityError:
            raise ValueError("E-mail já cadastrado")
        finally:
            conn.close()

    @staticmethod
    def listar(perfil=None):
        sql = f"SELECT {CAMPOS_PUBLICOS} FROM usuarios WHERE excluido_em IS NULL"
        params = []
        if perfil in PERFIS:
            sql += " AND perfil = %s"
            params.append(perfil)
        sql += " ORDER BY nome"

        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def obter_por_id(uid: int):
        conn = get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                f"SELECT {CAMPOS_PUBLICOS} FROM usuarios WHERE id = %s AND excluido_em IS NULL",
                (uid,),
            )
            return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def atualizar(uid: int, campos: dict) -> bool:
        if not campos:
            return False
        sets = [f"{c} = %s" for c in campos]
        params = list(campos.values()) + [uid]

        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE usuarios SET {', '.join(sets)} WHERE id = %s AND excluido_em IS NULL",
                params,
            )
            conn.commit()
            return cur.rowcount > 0
        except IntegrityError:
            raise ValueError("E-mail já cadastrado")
        finally:
            conn.close()

    @staticmethod
    def excluir_logico(uid: int) -> bool:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE usuarios SET excluido_em = NOW(), ativo = 0 "
                "WHERE id = %s AND excluido_em IS NULL",
                (uid,),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()