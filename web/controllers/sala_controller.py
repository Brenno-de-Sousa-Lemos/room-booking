from flask import Blueprint, render_template, request, redirect, url_for

from models import api_client
from security.decorators import login_required
from utils import sessao_expirou, tratar_resposta

bp = Blueprint("salas", __name__)


@bp.route("/salas", methods=["GET", "POST"])
@login_required("ADMIN")
def salas():
    if request.method == "POST":
        dados = {k: request.form.get(k) for k in ("nome", "tipo", "capacidade", "localizacao")}
        tratar_resposta(api_client.criar_sala(dados), "Sala cadastrada!")
        return redirect(url_for("salas.salas"))

    r = api_client.listar_salas()
    if sessao_expirou(r):
        return redirect(url_for("auth.login"))
    return render_template("salas.html", salas=r.json())


@bp.post("/salas/<int:sala_id>/excluir")
@login_required("ADMIN")
def excluir(sala_id):
    tratar_resposta(api_client.excluir_sala(sala_id), "Sala excluída.")
    return redirect(url_for("salas.salas"))