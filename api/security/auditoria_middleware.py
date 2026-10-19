from functools import wraps
from flask import request, g

from models.auditoria_model import AuditoriaModel


def _status_e_id(resposta, uid_kwarg):
    """Extrai o status HTTP e o id da entidade afetada, para registrar no log."""
    if isinstance(resposta, tuple):
        corpo, status = resposta[0], resposta[1]
    else:
        corpo, status = resposta, 200

    entidade_id = uid_kwarg
    if entidade_id is None:
        try:
            dados = corpo.get_json(silent=True)
            if dados:
                entidade_id = dados.get("id")
        except Exception:
            pass
    return status, entidade_id


def registrar_log(acao, entidade):
    """Registra a ação no log de auditoria. Nunca interrompe a rota caso o log falhe."""
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resposta = f(*args, **kwargs)
            try:
                status, entidade_id = _status_e_id(resposta, kwargs.get("uid"))
                usuario_id = int(g.usuario["sub"]) if hasattr(g, "usuario") else None
                usuario_nome = g.usuario.get("nome") if hasattr(g, "usuario") else None

                AuditoriaModel.registrar(
                    usuario_id=usuario_id,
                    usuario_nome=usuario_nome,
                    acao=acao,
                    entidade=entidade,
                    entidade_id=entidade_id,
                    sucesso=status < 400,
                    ip_origem=request.remote_addr,
                )
            except Exception:
                pass
            return resposta
        return wrapper
    return decorador