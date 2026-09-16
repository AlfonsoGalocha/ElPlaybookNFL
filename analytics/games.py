"""analytics/games.py — semana destacada y partido clave de una jornada (Duelo Clave)."""

from .matchups import duelo_clave


def highlight_week(sched):
    """Primera jornada sin jugar, o la ultima jugada si la temporada ya termino."""
    unplayed = sched[sched.home_score.isna()]
    if len(unplayed):
        return int(unplayed.week.min())
    return int(sched.week.max())


def completed_week(sched):
    """Ultima jornada con partidos ya disputados, o None si todavia no se ha jugado ninguna."""
    played = sched[sched.home_score.notna()]
    if played.empty:
        return None
    return int(played.week.max())


def featured_game(games, team_pct):
    """De los partidos de una jornada, el que tiene mayor brecha de percentil EPA (Duelo Clave).

    Devuelve (fila_del_partido, duelo) o None si no hay datos suficientes.
    """
    best_gap, best = 0, None
    for g in games.itertuples():
        if g.home_team not in team_pct.team.values or g.away_team not in team_pct.team.values:
            continue
        d = duelo_clave(team_pct, g.home_team, g.away_team)
        if d and abs(d["gap"]) >= abs(best_gap):
            best_gap, best = d["gap"], (g, d)
    return best
