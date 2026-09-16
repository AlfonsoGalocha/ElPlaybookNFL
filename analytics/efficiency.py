"""analytics/efficiency.py — eficiencia de QBs y equipos a partir de pbp real (EPA, success rate).

Todo lo de aqui son medias/sumas directas de columnas que ya trae nflverse
(epa, success, cpoe...). No se inventa ninguna metrica ni ponderacion propia.
"""

import numpy as np
import pandas as pd


def qb_efficiency_table(pbp, min_dropbacks=10):
    """EPA/jugada, success rate y CPOE medio por QB, en jugadas de pase con EPA valido."""
    p = pbp[(pbp.pass_attempt == 1) & pbp.epa.notna() & pbp.passer_player_name.notna()]
    if p.empty:
        return pd.DataFrame(columns=["passer_player_name", "team", "dropbacks",
                                      "epa_play", "success_rate", "cpoe", "air_yards"])
    g = p.groupby(["passer_player_name", "posteam"]).agg(
        dropbacks=("epa", "size"),
        epa_play=("epa", "mean"),
        success_rate=("success", "mean"),
        cpoe=("cpoe", "mean"),
        air_yards=("air_yards", "mean"),
    ).reset_index().rename(columns={"posteam": "team"})
    g = g[g.dropbacks >= min_dropbacks].sort_values("epa_play", ascending=False)
    return g.reset_index(drop=True)


def team_efficiency_table(pbp):
    """EPA/jugada y success rate de ataque y defensa por equipo (todas las jugadas con EPA)."""
    base = pbp[pbp.epa.notna()]
    off = (base[base.posteam.notna()].groupby("posteam")
           .agg(off_plays=("epa", "size"), off_epa_play=("epa", "mean"),
                off_success=("success", "mean"))
           .reset_index().rename(columns={"posteam": "team"}))
    deff = (base[base.defteam.notna()].groupby("defteam")
            .agg(def_plays=("epa", "size"), def_epa_play=("epa", "mean"),
                 def_success=("success", "mean"))
            .reset_index().rename(columns={"defteam": "team"}))
    return off.merge(deff, on="team", how="outer")


def team_situational_table(pbp):
    """Pass rate, rush rate, % de acierto en 3ª y TD en zona roja, por equipo."""
    off = pbp[pbp.posteam.notna()]
    g = (off.groupby("posteam")
         .agg(plays=("play_id", "count"),
              pass_rate=("pass_attempt", "mean"),
              rush_rate=("rush_attempt", "mean"))
         .reset_index().rename(columns={"posteam": "team"}))

    third = off[off.down == 3]
    if not third.empty:
        conv = (third.groupby("posteam")
                .agg(third_att=("third_down_converted", "size"),
                     third_conv=("third_down_converted", "sum"))
                .reset_index().rename(columns={"posteam": "team"}))
        conv["third_down_pct"] = conv.third_conv / conv.third_att
        g = g.merge(conv[["team", "third_down_pct"]], on="team", how="left")
    else:
        g["third_down_pct"] = np.nan

    rz = off[off.yardline_100 <= 20]
    if not rz.empty:
        rz_g = (rz.groupby("posteam")
                .agg(rz_plays=("play_id", "count"), rz_td=("touchdown", "sum"))
                .reset_index().rename(columns={"posteam": "team"}))
        rz_g["rz_td_pct"] = rz_g.rz_td / rz_g.rz_plays
        g = g.merge(rz_g[["team", "rz_td_pct"]], on="team", how="left")
    else:
        g["rz_td_pct"] = np.nan
    return g


def ngs_passing_summary(ngs_pass, week_range=None):
    """Resumen NGS de pase por QB (CPOE, tiempo de tiro, agresividad) ya agregado por nflverse.

    Espera un ngs_pass ya filtrado a semanas reales (ver data.loaders.load_ngs).
    """
    d = ngs_pass
    if week_range is not None:
        d = d[(d.week >= week_range[0]) & (d.week <= week_range[1])]
    g = d.groupby(["player_display_name", "team_abbr"]).agg(
        attempts=("attempts", "sum"),
        avg_time_to_throw=("avg_time_to_throw", "mean"),
        aggressiveness=("aggressiveness", "mean"),
        completion_pct_above_expectation=("completion_percentage_above_expectation", "mean"),
    ).reset_index().rename(columns={"team_abbr": "team"})
    return g.sort_values("completion_pct_above_expectation", ascending=False)


def pressure_table(pfr_pass):
    """Presion sufrida por QB (Pro Football Reference), agregada de temporada."""
    if pfr_pass is None or pfr_pass.empty:
        return pd.DataFrame(columns=["pfr_player_name", "team", "dropbacks_chart",
                                      "times_pressured", "times_pressured_pct"])
    g = pfr_pass.groupby(["pfr_player_name", "team"]).agg(
        times_sacked=("times_sacked", "sum"),
        times_hurried=("times_hurried", "sum"),
        times_hit=("times_hit", "sum"),
        times_pressured=("times_pressured", "sum"),
        times_pressured_pct=("times_pressured_pct", "mean"),
    ).reset_index()
    return g.sort_values("times_pressured_pct", ascending=False)
