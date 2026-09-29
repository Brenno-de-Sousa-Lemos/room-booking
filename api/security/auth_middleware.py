import datetime
from functools import wraps

import jwt
from flask import request, jsonify, g

import config


def gerar_token(usuario: dict) -> str:
    agora = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(usuario["id"]),
        "nome": usuario["nome"],
        "perfil": usuario["perfil"],
        "iat": agora,
        "exp": agora + datetime.timedelta(minutes=config.JWT_EXPIRA_MIN),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def requer_auth(*perfis_permitidos):
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify(erro="Token ausente"), 401
            try:
                dados = jwt.decode(header[7:], config.JWT_SECRET, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify(erro="Sessão expirada"), 401
            except jwt.InvalidTokenError:
                return jsonify(erro="Token inválido"), 401

            if perfis_permitidos and dados["perfil"] not in perfis_permitidos:
                return jsonify(erro="Acesso negado"), 403

            g.usuario = dados
            return f(*args, **kwargs)
        return wrapper
    return decorador