from flask import Blueprint, request, jsonify, g

from models.auditoria_model import AuditoriaModel
from security.auth_middleware import requer_auth

bp = Blueprint("auditoria", __name__, url_prefix="/logs")


@bp.get("")
@requer_auth("ADMIN")
def listar():
    """Consulta geral dos logs — restrita ao administrador."""
    return jsonify(AuditoriaModel.listar(
        usuario_id=request.args.get("usuario_id", type=int),
        acao=request.args.get("acao"),
        entidade=request.args.get("entidade"),
    ))


@bp.get("/meus")
@requer_auth()
def meus_logs():
    """Direito de acesso do titular (LGPD, art. 18): o próprio usuário
    pode consultar as ações registradas em seu nome."""
    return jsonify(AuditoriaModel.listar(usuario_id=int(g.usuario["sub"])))