"""analytics/utils.py — helpers puros compartidos entre modulos de analytics.

Nada de aqui importa streamlit: son funciones de dataframe a dataframe/dict,
para poder testearlas sin levantar la app.
"""

import datetime as dt
from zoneinfo import ZoneInfo

WEEKDAY_ES = {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
              "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"}


def mode(s):
    m = s.mode()
    return m.iloc[0] if len(m) else ""


def headshot_of(pdf, name):
    s = pdf[pdf.player_display_name == name]["headshot_url"].dropna()
    return s.iloc[0] if s.size else ""


def madrid_time(gameday, gametime):
    """Convierte fecha+hora de un partido (America/New_York, como vienen del calendario de
    nflreadpy) a un datetime en Europe/Madrid, o None si no se puede parsear."""
    try:
        naive = dt.datetime.strptime(f"{gameday} {gametime}", "%Y-%m-%d %H:%M")
        eastern = naive.replace(tzinfo=ZoneInfo("America/New_York"))
        return eastern.astimezone(ZoneInfo("Europe/Madrid"))
    except Exception:
        return None


def game_when_label(gameday, gametime):
    """"Domingo 14/09 · 19:00h" en hora de Madrid, o el gameday tal cual si no se puede convertir."""
    madrid = madrid_time(gameday, gametime)
    if not madrid:
        return gameday
    weekday = WEEKDAY_ES.get(madrid.strftime("%A"), madrid.strftime("%A")).capitalize()
    return f"{weekday} {madrid.strftime('%d/%m')} · {madrid.strftime('%H:%M')}h"
