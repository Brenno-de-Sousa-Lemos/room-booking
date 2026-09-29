from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from models.usuario_model import UsuarioModel, PERFIS
from security.auth_middleware import requer_auth

from security.auditoria_middleware import registrar_log

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def validar(dados, criando=True):
    erros = []
    if criando or "nome" in dados:
        if not (dados.get("nome") or "").strip():
            erros.append("Nome é obrigatório")
    if criando or "email" in dados:
        if "@" not in (dados.get("email") or "") or len(dados.get("email", "")) > 150:
            erros.append("E-mail inválido")
    if criando or "perfil" in dados:
        if dados.get("perfil") not in PERFIS:
            erros.append("Perfil inválido")
    if criando or "senha" in dados:
        if len(dados.get("senha") or "") < 8:
            erros.append("Senha deve ter no mínimo 8 caracteres")
    return erros


@bp.post("")
@requer_auth("ADMIN")
@registrar_log("CRIACAO", "usuarios")
def criar():
    dados = request.get_json(silent=True) or {}
    erros = validar(dados)
    if erros:
        return jsonify(erros=erros), 400
    try:
        uid = UsuarioModel.criar(
            dados["nome"].strip(),
            dados["email"].strip().lower(),
            generate_password_hash(dados["senha"]),
            dados["perfil"],
            dados.get("registro") or None,
        )
        return jsonify(id=uid), 201
    except ValueError as e:
        return jsonify(erro=str(e)), 409


@bp.get("")
@requer_auth("ADMIN")
@registrar_log("CONSULTA", "usuarios")
def listar():
    return jsonify(UsuarioModel.listar(request.args.get("perfil")))


@bp.get("/<int:uid>")
@requer_auth("ADMIN")
@registrar_log("CONSULTA", "usuarios")
def obter(uid):
    u = UsuarioModel.obter_por_id(uid)
    return (jsonify(u), 200) if u else (jsonify(erro="Não encontrado"), 404)


@bp.put("/<int:uid>")
@requer_auth("ADMIN")
@registrar_log("EDICAO", "usuarios")
def editar(uid):
    dados = request.get_json(silent=True) or {}
    erros = validar(dados, criando=False)
    if erros:
        return jsonify(erros=erros), 400

    campos = {c: dados[c] for c in ("nome", "email", "perfil", "registro", "ativo") if c in dados}
    if "email" in campos:
        campos["email"] = campos["email"].strip().lower()
    if "senha" in dados:
        campos["senha_hash"] = generate_password_hash(dados["senha"])
    if not campos:
        return jsonify(erro="Nada para atualizar"), 400

    try:
        atualizado = UsuarioModel.atualizar(uid, campos)
        return ("", 204) if atualizado else (jsonify(erro="Não encontrado"), 404)
    except ValueError as e:
        return jsonify(erro=str(e)), 409


@bp.delete("/<int:uid>")
@requer_auth("ADMIN")
@registrar_log("EXCLUSAO", "usuarios")
def excluir(uid):
    excluido = UsuarioModel.excluir_logico(uid)
    return ("", 204) if excluido else (jsonify(erro="Não encontrado"), 404)