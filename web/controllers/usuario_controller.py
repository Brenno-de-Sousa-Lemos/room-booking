from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import api_client
from security.decorators import login_required

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios", methods=["GET", "POST"])
@login_required("ADMIN")
def usuarios():
    if request.method == "POST":
        dados = {k: request.form.get(k) for k in ("nome", "email", "senha", "perfil", "registro")}
        r = api_client.criar_usuario(dados)
        if r.status_code == 201:
            flash("Usuário cadastrado!", "ok")
        else:
            corpo = r.json()
            flash("; ".join(corpo.get("erros", [corpo.get("erro", "Erro")])), "erro")
        return redirect(url_for("usuarios.usuarios"))

    r = api_client.listar_usuarios()
    if r.status_code == 401:
        from flask import session
        session.clear()
        return redirect(url_for("auth.login"))
    return render_template("usuarios.html", usuarios=r.json())