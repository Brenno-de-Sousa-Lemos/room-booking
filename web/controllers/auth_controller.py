from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests

from models import api_client

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            r = api_client.login(request.form["email"], request.form["senha"])
        except requests.RequestException:
            flash("Serviço indisponível. Tente novamente.", "erro")
            return render_template("login.html")

        if r.status_code == 200:
            d = r.json()
            session.clear()
            session.permanent = True
            session.update(token=d["token"], perfil=d["perfil"], nome=d["nome"])

            try:
                status_r = api_client.status_termos()
                session["termos_aceitos"] = (
                    status_r.json().get("aceito", False) if status_r.status_code == 200 else False
                )
            except requests.RequestException:
                session["termos_aceitos"] = False

            return redirect(url_for("dashboard.dashboard"))
        flash("E-mail ou senha inválidos.", "erro")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))