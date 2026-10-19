from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models import api_client
from security.decorators import login_required
from utils import sessao_expirou, tratar_resposta

bp = Blueprint("reservas", __name__)
CAMPOS = ("sala_id", "titulo", "descricao", "inicio", "fim")


@bp.route("/reservas")
@login_required()
def listar():
    perfil = session.get("perfil")
    pode_reservar = perfil in ("ADMIN", "PROFESSOR")

    params = {}
    if request.args.get("minhas"):
        params["minhas"] = 1
    if request.args.get("passadas"):
        params["passadas"] = 1

    r = api_client.listar_reservas(params)
    if sessao_expirou(r):
        return redirect(url_for("auth.login"))

    salas = api_client.listar_salas().json() if pode_reservar else []
    professores = api_client.listar_usuarios("PROFESSOR").json() if perfil == "ADMIN" else []

    return render_template(
        "reservas.html",
        reservas=r.json(), salas=salas, professores=professores, pode_reservar=pode_reservar,
    )


@bp.post("/reservas/nova")
@login_required("ADMIN", "PROFESSOR")
def criar():
    dados = {c: request.form.get(c) for c in CAMPOS}
    if session.get("perfil") == "ADMIN" and request.form.get("professor_id"):
        dados["professor_id"] = request.form["professor_id"]
    tratar_resposta(api_client.criar_reserva(dados), "Reserva criada!")
    return redirect(url_for("reservas.listar"))


@bp.route("/reservas/<int:rid>/editar", methods=["GET", "POST"])
@login_required("ADMIN", "PROFESSOR")
def editar(rid):
    if request.method == "POST":
        dados = {c: request.form.get(c) for c in CAMPOS}
        if tratar_resposta(api_client.editar_reserva(rid, dados), "Reserva atualizada!"):
            return redirect(url_for("reservas.listar"))
        return redirect(url_for("reservas.editar", rid=rid))

    r = api_client.obter_reserva(rid)
    if sessao_expirou(r):
        return redirect(url_for("auth.login"))
    if r.status_code != 200:
        flash("Reserva não encontrada.", "erro")
        return redirect(url_for("reservas.listar"))

    reserva = r.json()
    if not reserva["pode_editar"]:
        flash("Você só pode alterar as suas próprias reservas.", "erro")
        return redirect(url_for("reservas.listar"))

    salas = api_client.listar_salas().json()
    return render_template("reserva_editar.html", reserva=reserva, salas=salas)


@bp.post("/reservas/<int:rid>/excluir")
@login_required("ADMIN", "PROFESSOR")
def excluir(rid):
    tratar_resposta(api_client.excluir_reserva(rid), "Reserva cancelada.")
    return redirect(url_for("reservas.listar"))