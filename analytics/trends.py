"""analytics/trends.py — comparativas jornada a jornada (Tendencias).

Todo se calcula sobre datos reales por semana; nunca se "inventa" una
tendencia si no hay suficientes jornadas para sostenerla (ver MIN_WEEKS_*).
"""

import pandas as pd

MIN_WEEKS_FOR_TREND = 3  # con menos de 3 jornadas no afirmamos tendencias, solo mostramos la evolucion


def weekly_team_epa(pbp):
    """EPA/jugada de ataque y % de exito, por equipo y semana."""
    off = pbp[pbp.posteam.notna() & pbp.epa.notna()]
    return (off.groupby(["posteam", "week"])
            .agg(epa_play=("epa", "mean"), success_rate=("success", "mean"),
                 plays=("epa", "size"))
            .reset_index().rename(columns={"posteam": "team"}))


def weekly_team_situational(pbp):
    """Pass rate por equipo y semana (para ver si un equipo esta pasando mas o menos)."""
    off = pbp[pbp.posteam.notna()]
    return (off.groupby(["posteam", "week"])
            .agg(pass_rate=("pass_attempt", "mean"), plays=("play_id", "count"))
            .reset_index().rename(columns={"posteam": "team"}))


def trend_table(weekly_df, value_col, group_col="team", weight_col="plays"):
    """Compara la primera mitad de jornadas jugadas con la segunda, por grupo (equipo/jugador).

    Devuelve None si no hay jornadas suficientes para que la comparacion tenga sentido.
    """
    weeks = sorted(weekly_df.week.unique().tolist())
    if len(weeks) < MIN_WEEKS_FOR_TREND:
        return None
    mid = len(weeks) // 2
    early_weeks, recent_weeks = weeks[:mid] or weeks[:1], weeks[mid:]

    def _weighted(d):
        if weight_col and weight_col in d:
            w = d[weight_col]
            return (d[value_col] * w).sum() / w.sum() if w.sum() else d[value_col].mean()
        return d[value_col].mean()

    early = weekly_df[weekly_df.week.isin(early_weeks)].groupby(group_col).apply(_weighted, include_groups=False)
    recent = weekly_df[weekly_df.week.isin(recent_weeks)].groupby(group_col).apply(_weighted, include_groups=False)
    out = pd.DataFrame({"early": early, "recent": recent}).dropna()
    out["delta"] = out["recent"] - out["early"]
    out = out.reset_index().sort_values("delta", ascending=False)
    return {"table": out, "early_weeks": early_weeks, "recent_weeks": recent_weeks}
