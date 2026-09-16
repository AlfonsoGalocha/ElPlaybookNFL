"""analytics/explanations.py — desglose deterministico "¿Por qué?" de un EPA/jugada total en
sus componentes reales (pase, carrera, pérdidas de balón). Todo sale de sumar columnas de pbp
que ya existen (epa, pass_attempt, rush_attempt, interception, fumble_lost): los componentes
siempre suman exactamente el total, nada se pondera ni se inventa.
"""

MIN_PLAYS = 10

_DRIVER_LABEL = {
    "Passing EPA": "el juego aéreo",
    "Rushing EPA": "el juego terrestre",
    "Turnovers EPA": "las pérdidas de balón",
    "Otras jugadas": "otras jugadas",
}


def epa_breakdown(off_pbp):
    """Descompone el EPA/jugada de un conjunto de jugadas ofensivas (de un equipo o de un
    jugador concreto) en pase, carrera y pérdidas de balón (INT o fumble perdido, en pase o
    carrera). Los componentes suman exactamente el EPA/jugada total.

    Devuelve None si no hay jugadas suficientes con EPA válido — nunca se muestra un
    desglose con muestra insuficiente.
    """
    d = off_pbp[off_pbp.epa.notna()]
    if len(d) < MIN_PLAYS:
        return None
    total_plays = len(d)
    total_epa_play = float(d.epa.sum() / total_plays)

    turnover = (d.interception.fillna(0) == 1) | (d.fumble_lost.fillna(0) == 1)
    to_epa = float(d[turnover].epa.sum() / total_plays)

    clean = d[~turnover]
    pass_epa = float(clean[clean.pass_attempt == 1].epa.sum() / total_plays)
    rush_epa = float(clean[clean.rush_attempt == 1].epa.sum() / total_plays)
    other_epa = total_epa_play - to_epa - pass_epa - rush_epa  # penaltis, spikes, kneels...

    components = [("Passing EPA", pass_epa), ("Rushing EPA", rush_epa), ("Turnovers EPA", to_epa)]
    if abs(other_epa) >= 0.005:
        components.append(("Otras jugadas", other_epa))

    return {"total": total_epa_play, "components": components, "n_plays": total_plays}


def breakdown_insight(breakdown, subject="El rendimiento ofensivo"):
    """Frase deterministica: identifica el componente de mayor magnitud y explica si
    impulsa o lastra el total. No hay generación libre, solo plantilla sobre datos reales."""
    if breakdown is None:
        return None
    lead_label, lead_val = max(breakdown["components"], key=lambda kv: abs(kv[1]))
    driver = _DRIVER_LABEL.get(lead_label, lead_label.lower())
    verbo = "impulsado" if lead_val >= 0 else "lastrado"
    return f"{subject} está siendo {verbo} principalmente por {driver}."
