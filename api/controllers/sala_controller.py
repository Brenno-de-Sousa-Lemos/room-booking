from flask import Blueprint, request, jsonify

from models.sala_model import SalaModel
from security.auth_middleware import requer_auth
from security.auditoria_middleware import registrar_log

bp = Blueprint("salas", __name__, url_prefix="/salas")
TIPOS = {"SALA", "AUDITORIO"}


def _validar(dados, criando=True):
    erros = []
    if criando or "nome" in dados:
        if not (dados.get("nome") or "").strip():
            erros.append("Nome é obrigatório")
    if criando or "tipo" in dados:
        if dados.get("tipo") not in TIPOS:
            erros.append("Tipo inválido")
    if criando or "capacidade" in dados:
        try:
            if int(dados.get("capacidade")) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            erros.append("Capacidade deve ser um número maior que zero")
    return erros


@bp.post("")
@requer_auth("ADMIN")
@registrar_log("CRIACAO", "salas")
def criar():
    dados = request.get_json(silent=True) or {}
    erros = _validar(dados)
    if erros:
        return jsonify(erros=erros), 400
    sid = SalaModel.criar(
        dados["nome"].strip(), dados["tipo"], int(dados["capacidade"]),
        (dados.get("localizacao") or "").strip() or None,
    )
    return jsonify(id=sid), 201


@bp.get("")
@requer_auth()
def listar():
    return jsonify(SalaModel.listar())


@bp.get("/<int:uid>")
@requer_auth()
def obter(uid):
    s = SalaModel.obter_por_id(uid)
    return (jsonify(s), 200) if s else (jsonify(erro="Não encontrada"), 404)


@bp.put("/<int:uid>")
@requer_auth("ADMIN")
@registrar_log("EDICAO", "salas")
def editar(uid):
    dados = request.get_json(silent=True) or {}
    erros = _validar(dados, criando=False)
    if erros:
        return jsonify(erros=erros), 400
    if not SalaModel.obter_por_id(uid):
        return jsonify(erro="Não encontrada"), 404

    campos = {c: dados[c] for c in ("nome", "tipo", "capacidade", "localizacao", "ativo") if c in dados}
    if "capacidade" in campos:
        campos["capacidade"] = int(campos["capacidade"])
    if not campos:
        return jsonify(erro="Nada para atualizar"), 400
    SalaModel.atualizar(uid, campos)
    return "", 204


@bp.delete("/<int:uid>")
@requer_auth("ADMIN")
@registrar_log("EXCLUSAO", "salas")
def excluir(uid):
    try:
        ok = SalaModel.excluir_logico(uid)
    except ValueError as e:
        return jsonify(erro=str(e)), 409
    return ("", 204) if ok else (jsonify(erro="Não encontrada"), 404)