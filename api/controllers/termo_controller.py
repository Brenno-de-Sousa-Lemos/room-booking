from flask import Blueprint, jsonify, g, request

import config
from models.termo_model import TermoModel
from models.auditoria_model import AuditoriaModel
from security.auth_middleware import requer_auth

bp = Blueprint("termos", __name__, url_prefix="/termos")


@bp.get("/status")
@requer_auth()
def status():
    usuario_id = int(g.usuario["sub"])
    return jsonify(
        aceito=TermoModel.usuario_aceitou_versao_atual(usuario_id),
        termo_versao=config.TERMO_VERSAO,
        politica_versao=config.POLITICA_VERSAO,
    )


@bp.post("/aceitar")
@requer_auth()
def aceitar():
    usuario_id = int(g.usuario["sub"])
    TermoModel.registrar_aceite(usuario_id, request.remote_addr)
    AuditoriaModel.registrar(
        usuario_id=usuario_id,
        usuario_nome=g.usuario.get("nome"),
        acao="ACEITE_TERMOS",
        entidade="termos_aceite",
        entidade_id=usuario_id,
        sucesso=True,
        ip_origem=request.remote_addr,
    )
    return jsonify(ok=True), 201