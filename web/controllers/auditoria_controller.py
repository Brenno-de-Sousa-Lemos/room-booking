from flask import Blueprint, render_template, session, redirect, url_for

from models import api_client
from security.decorators import login_required

bp = Blueprint("auditoria", __name__)


@bp.route("/logs")
@login_required("ADMIN")
def logs():
    r = api_client.listar_logs()
    if r.status_code == 401:
        session.clear()
        return redirect(url_for("auth.login"))
    return render_template("logs.html", logs=r.json())