from flask import Flask, redirect, url_for
from datetime import datetime

import config
from controllers import auth_controller, dashboard_controller, usuario_controller, auditoria_controller, termo_controller, sala_controller, reserva_controller

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=3600,
)

app.register_blueprint(auth_controller.bp)
app.register_blueprint(dashboard_controller.bp)
app.register_blueprint(usuario_controller.bp)
app.register_blueprint(auditoria_controller.bp)
app.register_blueprint(termo_controller.bp)
app.register_blueprint(sala_controller.bp)
app.register_blueprint(reserva_controller.bp)

@app.template_filter("datahora")
def datahora(valor):
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return valor or "-"

@app.route("/")
def index():
    return redirect(url_for("dashboard.dashboard"))


if __name__ == "__main__":
    app.run(port=5001, debug=True)