"""analytics/weekly.py — automatización de "El Playbook Weekly": detección de tendencias y
cambios de rendimiento significativos entre jornadas. Nada de esto es "ordenar una columna y
listo": cada función exige datos de al menos dos jornadas jugadas, aplica un mínimo de jugadas
por equipo/semana para evitar ruido de muestras pequeñas, y expone el criterio en los datos que
devuelve para que la página pueda explicarlo.
"""

MIN_WEEKS_FOR_TREND = 2
SIGNIFICANT_EPA_DELTA = 0.08  # cambio de EPA/jugada semana a semana considerado una historia real
MIN_PLAYS_TEAM_WEEK = 15


def has_enough_history(current_week):
    return current_week is not None and current_week >= MIN_WEEKS_FOR_TREND


def team_week_epa(pbp, week):
    """EPA/jugada ofensivo de cada equipo en una jornada concreta (con jugadas suficientes)."""
    d = pbp[(pbp.week == week) & pbp.epa.notna() & pbp.posteam.notna()]
    if d.empty:
        return None
    g = (d.groupby("posteam").agg(epa_play=("epa", "mean"), plays=("epa", "size"))
         .reset_index().rename(columns={"posteam": "team"}))
    g = g[g.plays >= MIN_PLAYS_TEAM_WEEK]
    return g if not g.empty else None


def week_over_week_deltas(pbp, current_week):
    """EPA/jugada ofensivo de cada equipo en la jornada actual frente a la anterior.

    Devuelve None si no hay al menos dos jornadas jugadas con datos suficientes — nunca se
    compara una jornada consigo misma ni se inventa una "anterior" que no existe.
    """
    if not has_enough_history(current_week):
        return None
    cur = team_week_epa(pbp, current_week)
    prev = team_week_epa(pbp, current_week - 1)
    if cur is None or prev is None:
        return None
    m = cur.merge(prev, on="team", suffixes=("_cur", "_prev"))
    if m.empty:
        return None
    m["delta"] = m.epa_play_cur - m.epa_play_prev
    return m


def story_of_the_week(pbp, current_week, team_meta=None):
    """El mayor cambio de EPA/jugada ofensivo semana a semana (mejora o caída), solo si
    supera un umbral mínimo para considerarse una historia real y no ruido de muestra."""
    m = week_over_week_deltas(pbp, current_week)
    if m is None:
        return None
    top = m.reindex(m.delta.abs().sort_values(ascending=False).index).iloc[0]
    if abs(top.delta) < SIGNIFICANT_EPA_DELTA:
        return None
    name = team_meta.get(top.team, {}).get("name", top.team) if team_meta else top.team
    return {"team": top.team, "team_name": name, "prev_epa": float(top.epa_play_prev),
            "cur_epa": float(top.epa_play_cur), "delta": float(top.delta),
            "prev_week": current_week - 1, "cur_week": current_week}


def biggest_movers(pbp, current_week, n=3):
    """Los equipos que más mejoraron y más cayeron en EPA/jugada ofensivo respecto a la
    jornada anterior. Exige datos reales de dos jornadas — no es un ranking de temporada."""
    m = week_over_week_deltas(pbp, current_week)
    if m is None:
        return None
    improving = m.sort_values("delta", ascending=False).head(n).to_dict("records")
    declining = m.sort_values("delta").head(n).to_dict("records")
    return {"improving": improving, "declining": declining}
