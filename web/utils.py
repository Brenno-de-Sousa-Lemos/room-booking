from flask import flash, session


def sessao_expirou(r):
    if r.status_code == 401:
        session.clear()
        return True
    return False


def tratar_resposta(r, mensagem_ok):
    """Mostra a mensagem certa para a resposta da API. Devolve True se deu certo."""
    if r.status_code in (200, 201, 204):
        flash(mensagem_ok, "ok")
        if r.status_code != 204:
            try:
                aviso = r.json().get("aviso")
            except ValueError:
                aviso = None
            if aviso:
                flash(aviso, "aviso")
        return True
    try:
        corpo = r.json()
    except ValueError:
        corpo = {}
    flash("; ".join(corpo.get("erros", [corpo.get("erro", "Erro inesperado")])), "erro")
    return False