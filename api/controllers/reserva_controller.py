from datetime import datetime

from flask import Blueprint, request, jsonify, g

from models.reserva_model import ReservaModel
from models.usuario_model import UsuarioModel
from security.auth_middleware import requer_auth
from security.auditoria_middleware import registrar_log
from services import reserva_service

bp = Blueprint("reservas", __name__, url_prefix="/reservas")
FORMATO = "%Y-%m-%dT%H:%M"
AVISO_SYNC = "Reserva salva, mas não foi possível sincronizar com o Google Calendar."


def _eh_admin():
    return g.usuario["perfil"] == "ADMIN"

def _pode_alterar(reserva):
    return _eh_admin() or reserva["professor_id"] == int(g.usuario["sub"])

def _serializar(r):
    r.pop("google_event_id", None)
    r["inicio"] = r["inicio"].strftime(FORMATO)
    r["fim"] = r["fim"].strftime(FORMATO)
    r["pode_editar"] = _pode_alterar(r)
    return r

def _ler_dados(dados, criando=True):
    erros = []
    titulo = (dados.get("titulo") or "").strip()
    if not titulo or len(titulo) > 150:
        erros.append("Título é obrigatório (máx. 150 caracteres)")

    try:
        sala_id = int(dados.get("sala_id"))
    except (TypeError, ValueError):
        sala_id = None
        erros.append("Sala inválida")

    inicio = fim = None
    try:
        inicio = datetime.fromisoformat(dados["inicio"])
        fim = datetime.fromisoformat(dados["fim"])
        if inicio.tzinfo or fim.tzinfo:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        erros.append("Datas inválidas")
    else:
        if fim <= inicio:
            erros.append("O fim deve ser posterior ao início")
        elif criando and inicio < datetime.now():
            erros.append("Não é possível reservar no passado")

    descricao = (dados.get("descricao") or "").strip() or None
    return erros, dict(sala_id=sala_id, titulo=titulo, descricao=descricao, inicio=inicio, fim=fim)


@bp.post("")
@requer_auth("ADMIN", "PROFESSOR")
@registrar_log("CRIACAO", "reservas")
def criar():
    dados = request.get_json(silent=True) or {}
    erros, v = _ler_dados(dados)
    if erros:
        return jsonify(erros=erros), 400

    professor_id = int(g.usuario["sub"])
    if _eh_admin() and dados.get("professor_id"):
        try:
            prof = UsuarioModel.obter_por_id(int(dados["professor_id"]))
        except (TypeError, ValueError):
            prof = None
        if not prof or prof["perfil"] not in ("PROFESSOR", "ADMIN"):
            return jsonify(erro="Professor inválido"), 400
        professor_id = prof["id"]

    try:
        rid = ReservaModel.criar(
            v["sala_id"], professor_id, v["titulo"], v["descricao"], v["inicio"], v["fim"]
        )
    except LookupError as e:
        return jsonify(erro=str(e)), 404
    except ValueError as e:
        return jsonify(erro=str(e)), 409

    sincronizado = reserva_service.sincronizar(rid)
    resposta = {"id": rid, "sincronizado": sincronizado}
    if not sincronizado:
        resposta["aviso"] = AVISO_SYNC
    return jsonify(resposta), 201


@bp.get("")
@requer_auth()
def listar():
    professor_id = int(g.usuario["sub"]) if request.args.get("minhas") else None
    reservas = ReservaModel.listar(
        sala_id=request.args.get("sala_id", type=int),
        professor_id=professor_id,
        incluir_passadas=bool(request.args.get("passadas")),
    )
    return jsonify([_serializar(r) for r in reservas])

@bp.get("/<int:uid>")
@requer_auth()
def obter(uid):
    r = ReservaModel.obter_por_id(uid)
    return (jsonify(_serializar(r)), 200) if r else (jsonify(erro="Não encontrada"), 404)

@bp.put("/<int:uid>")
@requer_auth("ADMIN", "PROFESSOR")
@registrar_log("EDICAO", "reservas")
def editar(uid):
    reserva = ReservaModel.obter_por_id(uid)
    if not reserva:
        return jsonify(erro="Não encontrada"), 404
    if not _pode_alterar(reserva):
        return jsonify(erro="Você só pode alterar as suas próprias reservas"), 403

    erros, v = _ler_dados(request.get_json(silent=True) or {}, criando=False)
    if erros:
        return jsonify(erros=erros), 400

    try:
        ReservaModel.atualizar(uid, v["sala_id"], v["titulo"], v["descricao"], v["inicio"], v["fim"])
    except LookupError as e:
        return jsonify(erro=str(e)), 404
    except ValueError as e:
        return jsonify(erro=str(e)), 409

    if not reserva_service.sincronizar(uid):
        return jsonify(aviso=AVISO_SYNC), 200
    return "", 204

@bp.delete("/<int:uid>")
@requer_auth("ADMIN", "PROFESSOR")
@registrar_log("EXCLUSAO", "reservas")
def excluir(uid):
    reserva = ReservaModel.obter_por_id(uid)
    if not reserva:
        return jsonify(erro="Não encontrada"), 404
    if not _pode_alterar(reserva):
        return jsonify(erro="Você só pode cancelar as suas próprias reservas"), 403

    ReservaModel.excluir_logico(uid)
    if not reserva_service.remover_do_google(reserva):
        return jsonify(aviso="Reserva cancelada, mas o evento no Google Calendar não pôde ser removido."), 200
    return "", 204