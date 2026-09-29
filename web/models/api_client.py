import requests
from flask import session
import config


def _headers():
    return {"Authorization": f"Bearer {session.get('token')}"}


def login(email, senha):
    return requests.post(
        f"{config.API_URL}/auth/login",
        json={"email": email, "senha": senha},
        timeout=5,
    )


def listar_usuarios():
    return requests.get(f"{config.API_URL}/usuarios", headers=_headers(), timeout=5)

def criar_usuario(dados: dict):
    return requests.post(f"{config.API_URL}/usuarios", headers=_headers(), json=dados, timeout=5)

def listar_logs():
    return requests.get(f"{config.API_URL}/logs", headers=_headers(), timeout=5)

def status_termos():
    return requests.get(f"{config.API_URL}/termos/status", headers=_headers(), timeout=5)

def aceitar_termos():
    return requests.post(f"{config.API_URL}/termos/aceitar", headers=_headers(), timeout=5)