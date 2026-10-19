from flask import current_app

from models.reserva_model import ReservaModel
from services import google_calendar_service as gcal


def sincronizar(reserva_id: int) -> bool:
    """Cria ou atualiza o evento no Google. Nunca lança exceção: devolve True/False."""
    reserva = ReservaModel.obter_por_id(reserva_id)
    if not reserva:
        return False
    try:
        event_id = reserva["google_event_id"]
        if event_id:
            gcal.atualizar_evento(event_id, reserva)
        else:
            event_id = gcal.criar_evento(reserva)
        ReservaModel.marcar_sincronizacao(reserva_id, event_id, True)
        return True
    except Exception:
        current_app.logger.exception("Falha ao sincronizar reserva %s com o Google", reserva_id)
        ReservaModel.marcar_sincronizacao(reserva_id, None, False)
        return False


def remover_do_google(reserva: dict) -> bool:
    if not reserva.get("google_event_id"):
        return True
    try:
        gcal.excluir_evento(reserva["google_event_id"])
        return True
    except Exception:
        current_app.logger.exception("Falha ao remover evento da reserva %s", reserva["id"])
        return False