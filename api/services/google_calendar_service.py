from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _servico():
    creds = service_account.Credentials.from_service_account_file(
        config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _corpo_evento(r: dict) -> dict:
    local = r["sala_nome"]
    if r.get("sala_localizacao"):
        local += f" - {r['sala_localizacao']}"

    linhas = []
    if r.get("descricao"):
        linhas.append(r["descricao"])
    linhas.append(f"Responsável: {r['professor_nome']}")
    linhas.append("Reserva gerenciada pelo sistema Room-Booking.")

    return {
        "summary": f"{r['titulo']} ({r['sala_nome']})",
        "location": local,
        "description": "\n".join(linhas),
        "start": {"dateTime": r["inicio"].isoformat(), "timeZone": config.TIMEZONE},
        "end": {"dateTime": r["fim"].isoformat(), "timeZone": config.TIMEZONE},
    }


def criar_evento(reserva: dict) -> str:
    evento = _servico().events().insert(
        calendarId=config.GOOGLE_CALENDAR_ID, body=_corpo_evento(reserva)
    ).execute()
    return evento["id"]


def atualizar_evento(event_id: str, reserva: dict) -> None:
    _servico().events().update(
        calendarId=config.GOOGLE_CALENDAR_ID, eventId=event_id, body=_corpo_evento(reserva)
    ).execute()


def excluir_evento(event_id: str) -> None:
    try:
        _servico().events().delete(
            calendarId=config.GOOGLE_CALENDAR_ID, eventId=event_id
        ).execute()
    except HttpError as e:
        if e.resp.status in (404, 410):
            return
        raise