from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(*perfis):
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "token" not in session:
                return redirect(url_for("auth.login"))

            if not session.get("termos_aceitos") and request.endpoint != "termos.aceitar_termos":
                session["proxima_url"] = request.url
                return redirect(url_for("termos.aceitar_termos"))

            if perfis and session.get("perfil") not in perfis:
                flash("Você não tem permissão para acessar esta página.", "erro")
                return redirect(url_for("dashboard.dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorador