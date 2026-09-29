from flask import Blueprint, render_template, redirect, url_for, session, request

from models import api_client

bp = Blueprint("termos", __name__)


@bp.route("/termo-de-uso")
def termo_uso():
    """Página pública, acessível sem login."""
    return render_template("termo_uso.html")


@bp.route("/politica-de-privacidade")
def politica_privacidade():
    """Página pública, acessível sem login."""
    return render_template("politica_privacidade.html")


@bp.route("/aceitar-termos", methods=["GET", "POST"])
def aceitar_termos():
    if "token" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        if request.form.get("aceite") == "on":
            api_client.aceitar_termos()
            session["termos_aceitos"] = True
            destino = session.pop("proxima_url", None) or url_for("dashboard.dashboard")
            return redirect(destino)
        return render_template("aceitar_termos.html", erro="É necessário marcar a caixa para continuar.")

    return render_template("aceitar_termos.html")