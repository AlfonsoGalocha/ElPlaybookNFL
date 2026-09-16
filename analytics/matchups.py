"""analytics/matchups.py — comparativa ataque/defensa entre dos equipos y "Duelo Clave".

El Duelo Clave no es una puntuacion arbitraria: es el emparejamiento (ataque
de un equipo vs defensa del otro) con mayor diferencia de percentil real de
la temporada en EPA/jugada, sobre los datos de pbp ya calculados en
analytics.efficiency. Siempre se puede mostrar el numero detras del percentil.
"""

import pandas as pd


def with_percentiles(team_eff):
    """Añade percentil 0-100 de cada equipo en off/def EPA y success rate.

    Para defensa, menor EPA permitida = mejor, así que el percentil se invierte
    para que "percentil alto" signifique siempre "mejor" en las dos direcciones.
    """
    df = team_eff.copy()
    df["off_epa_pct"] = df["off_epa_play"].rank(pct=True) * 100
    df["off_success_pct"] = df["off_success"].rank(pct=True) * 100
    df["def_epa_pct"] = df["def_epa_play"].rank(pct=True, ascending=False) * 100
    df["def_success_pct"] = df["def_success"].rank(pct=True, ascending=False) * 100
    return df


def team_row(team_pct, abbr):
    rows = team_pct[team_pct.team == abbr]
    return rows.iloc[0] if len(rows) else None


def duelo_clave(team_pct, team_a, team_b):
    """Identifica el emparejamiento ataque-vs-defensa con mayor brecha de percentil.

    Devuelve un dict con el lado ganador, el hueco (0-100) y los numeros reales
    (EPA/jugada) que lo sostienen, o None si falta algun equipo en los datos.
    """
    a, b = team_row(team_pct, team_a), team_row(team_pct, team_b)
    if a is None or b is None:
        return None
    candidates = [
        {"label": f"Ataque de {team_a} vs Defensa de {team_b}",
         "off_team": team_a, "def_team": team_b,
         "off_pct": a["off_epa_pct"], "def_pct": b["def_epa_pct"],
         "off_epa": a["off_epa_play"], "def_epa": b["def_epa_play"]},
        {"label": f"Ataque de {team_b} vs Defensa de {team_a}",
         "off_team": team_b, "def_team": team_a,
         "off_pct": b["off_epa_pct"], "def_pct": a["def_epa_pct"],
         "off_epa": b["off_epa_play"], "def_epa": a["def_epa_play"]},
    ]
    for c in candidates:
        # brecha: cuanto mejor es el ataque que la defensa que le toca enfrentar
        c["gap"] = c["off_pct"] - (100 - c["def_pct"])
    best = max(candidates, key=lambda c: abs(c["gap"]))
    best["favours_offense"] = best["gap"] > 0
    return best


def matchup_sections(team_a_stats, team_b_stats):
    """Empareja las tiles de dos equipos para las secciones ataque/defensa/situacional."""
    keys = [k for k in team_a_stats if k in team_b_stats]
    return [(k, team_a_stats[k], team_b_stats[k]) for k in keys]
