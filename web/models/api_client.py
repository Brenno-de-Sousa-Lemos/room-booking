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


def listar_usuarios(perfil=None):
    params = {"perfil": perfil} if perfil else None
    return requests.get(f"{config.API_URL}/usuarios", headers=_headers(), params=params, timeout=5)

def criar_usuario(dados: dict):
    return requests.post(f"{config.API_URL}/usuarios", headers=_headers(), json=dados, timeout=5)

def listar_logs():
    return requests.get(f"{config.API_URL}/logs", headers=_headers(), timeout=5)

def status_termos():
    return requests.get(f"{config.API_URL}/termos/status", headers=_headers(), timeout=5)

def aceitar_termos():
    return requests.post(f"{config.API_URL}/termos/aceitar", headers=_headers(), timeout=5)

def listar_salas():
    return requests.get(f"{config.API_URL}/salas", headers=_headers(), timeout=5)

def criar_sala(dados):
    return requests.post(f"{config.API_URL}/salas", headers=_headers(), json=dados, timeout=5)

def excluir_sala(sala_id):
    return requests.delete(f"{config.API_URL}/salas/{sala_id}", headers=_headers(), timeout=5)

def listar_reservas(params=None):
    return requests.get(f"{config.API_URL}/reservas", headers=_headers(), params=params, timeout=10)

def obter_reserva(rid):
    return requests.get(f"{config.API_URL}/reservas/{rid}", headers=_headers(), timeout=10)

def criar_reserva(dados):
    return requests.post(f"{config.API_URL}/reservas", headers=_headers(), json=dados, timeout=20)

def editar_reserva(rid, dados):
    return requests.put(f"{config.API_URL}/reservas/{rid}", headers=_headers(), json=dados, timeout=20)

def excluir_reserva(rid):
    return requests.delete(f"{config.API_URL}/reservas/{rid}", headers=_headers(), timeout=20)