"""analytics/totals.py — totales de temporada por jugador y metricas por posicion."""

import nfl_graficos as G

from .utils import mode


def totals_table(pdf, week_range=None):
    """Totales ofensivos (pase/carrera/recepcion) por jugador. Usado en Comparador clasico y Equipos."""
    d = pdf
    if week_range is not None:
        d = d[(d["week"] >= week_range[0]) & (d["week"] <= week_range[1])]
    g = d.groupby("player_display_name").agg(
        position=("position", mode), team=("team", mode),
        passing_yards=("passing_yards", "sum"), passing_tds=("passing_tds", "sum"),
        passing_interceptions=("passing_interceptions", "sum"),
        rushing_yards=("rushing_yards", "sum"), rushing_tds=("rushing_tds", "sum"),
        receptions=("receptions", "sum"), receiving_yards=("receiving_yards", "sum"),
        receiving_tds=("receiving_tds", "sum"),
        pfd=("passing_first_downs", "sum"), rfd=("rushing_first_downs", "sum"),
        recfd=("receiving_first_downs", "sum"),
    ).reset_index()
    g["total_tds"] = g.passing_tds + g.rushing_tds + g.receiving_tds
    g["first_downs_total"] = g.pfd + g.rfd + g.recfd
    return g


def full_totals_table(pdf, week_range=None):
    """Totales de temporada por jugador, incluyendo stats de ataque, defensa y equipos especiales."""
    d = pdf
    if week_range is not None:
        d = d[(d["week"] >= week_range[0]) & (d["week"] <= week_range[1])]
    agg = {c: (c, "max" if c in G.MAX_COLS else "sum") for c in G.STAT_COLS if c in d.columns}
    g = d.groupby("player_display_name").agg(
        position=("position", mode), team=("team", mode), **agg
    ).reset_index()
    g["total_tds"] = g.passing_tds + g.rushing_tds + g.receiving_tds
    g["tackles"] = g.def_tackles_solo + g.def_tackles_with_assist
    return g


def metrics_for_position(pos):
    """Metricas relevantes (etiqueta -> columna) para comparar jugadores de una posicion."""
    pos = (pos or "").upper()
    if pos == "QB":
        return {"Yardas de pase": "passing_yards", "TD de pase": "passing_tds",
                "Intercepciones": "passing_interceptions", "Yardas de carrera": "rushing_yards",
                "TD de carrera": "rushing_tds"}
    if pos in ("RB", "FB"):
        return {"Yardas de carrera": "rushing_yards", "TD de carrera": "rushing_tds",
                "Carreras": "carries", "Recepciones": "receptions",
                "Yardas de recepcion": "receiving_yards"}
    if pos in ("WR", "TE"):
        return {"Recepciones": "receptions", "Objetivos": "targets",
                "Yardas de recepcion": "receiving_yards", "TD de recepcion": "receiving_tds"}
    if pos in G.DEF_POSITIONS:
        return {"Tacleos": "tackles", "Sacks": "def_sacks",
                "Tackles para perdida": "def_tackles_for_loss", "Presiones QB": "def_qb_hits",
                "Intercepciones": "def_interceptions", "Pases defendidos": "def_pass_defended"}
    if pos == "K":
        return {"FG anotados": "fg_made", "FG intentados": "fg_att", "PAT anotados": "pat_made"}
    if pos == "P":
        return {"Despejes": "pt_att", "Yardas": "pt_yards"}
    return {"TD totales": "total_tds"}


def headline_stat(pos):
    """La primera metrica (mas representativa) de metrics_for_position, para usar como
    "numero de cabecera" en contexto/evolucion. Devuelve (etiqueta, columna) o None."""
    m = metrics_for_position(pos)
    if not m:
        return None
    return next(iter(m.items()))


def team_stat_tiles(std_row, s):
    yards_total = s["passing_yards"] + s["rushing_yards"]
    return [
        ("RECORD", f"{int(std_row['W'])}-{int(std_row['L'])}-{int(std_row['T'])}"),
        ("PTS A FAVOR", f"{std_row['PF']:,.0f}".replace(",", ".")),
        ("PTS EN CONTRA", f"{std_row['PA']:,.0f}".replace(",", ".")),
        ("YARDAS TOTALES", f"{yards_total:,.0f}".replace(",", ".")),
        ("SACKS", f"{s['def_sacks']:.1f}"),
        ("INTERCEP.", f"{s['def_interceptions']:,.0f}"),
    ]


def player_season(pdf, name):
    p = pdf[pdf.player_display_name == name]
    pos = mode(p["position"])
    return {
        "pos": pos, "team": mode(p["team"]),
        "tiles": G._tiles(pos, G.player_totals(p)),
    }
