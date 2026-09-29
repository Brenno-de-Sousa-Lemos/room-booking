from flask import Blueprint, render_template
from security.decorators import login_required

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required()
def dashboard():
    return render_template("dashboard.html")