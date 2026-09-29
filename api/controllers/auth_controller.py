from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash

from models.usuario_model import UsuarioModel
from security.auth_middleware import gerar_token, requer_auth
from models.auditoria_model import AuditoriaModel

bp = Blueprint("auth", __name__, url_prefix="/auth")

HASH_FALSO = "scrypt:32768:8:1$x$" + "0" * 128


@bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha") or ""

    if not email or not senha:
        return jsonify(erro="Informe e-mail e senha"), 400

    usuario = UsuarioModel.buscar_por_email(email)

    hash_ = usuario["senha_hash"] if usuario else HASH_FALSO
    try:
        senha_ok = check_password_hash(hash_, senha)
    except ValueError:
        senha_ok = False

    sucesso = bool(usuario and senha_ok)
    try:
        AuditoriaModel.registrar(
            usuario_id=usuario["id"] if usuario else None,
            usuario_nome=usuario["nome"] if usuario else email,
            acao="LOGIN" if sucesso else "LOGIN_FALHA",
            entidade="usuarios",
            entidade_id=usuario["id"] if usuario else None,
            sucesso=sucesso,
            ip_origem=request.remote_addr,
        )
    except Exception:
        pass

    if not sucesso:
        return jsonify(erro="Credenciais inválidas"), 401

    return jsonify(
        token=gerar_token(usuario),
        perfil=usuario["perfil"],
        nome=usuario["nome"],
    )


@bp.get("/me")
@requer_auth()
def me():
    return jsonify(id=g.usuario["sub"], nome=g.usuario["nome"], perfil=g.usuario["perfil"])