"""analytics/game_summary.py — resumen de un partido ya disputado, a partir del mismo pbp de
temporada (data.loaders.load_pbp) filtrado a un game_id. No pide datos nuevos ni duplica la
carga: solo agrega a nivel de partido en vez de temporada completa.
"""

EXPLOSIVE_YARDS = 20  # jugada "explosiva": convencion habitual en analitica de NFL


def game_pbp(pbp, game_id):
    return pbp[pbp.game_id == game_id]


def team_boxscore(g_pbp, team):
    """Yardas, turnovers, 3a down, zona roja, jugadas explosivas y EPA de un equipo en un partido."""
    off = g_pbp[g_pbp.posteam == team]
    if off.empty:
        return None
    off_epa = off[off.epa.notna()]
    pass_plays = off[off.pass_attempt == 1]
    rush_plays = off[off.rush_attempt == 1]
    third = off[off.down == 3]
    rz = off[off.yardline_100 <= 20]
    return {
        "team": team,
        "plays": int(len(off)),
        "pass_yards": int(pass_plays.yards_gained.fillna(0).sum()),
        "rush_yards": int(rush_plays.yards_gained.fillna(0).sum()),
        "total_yards": int(off.yards_gained.fillna(0).sum()),
        "turnovers": int(off.interception.fillna(0).sum() + off.fumble_lost.fillna(0).sum()),
        "sacks_allowed": int(off.sack.fillna(0).sum()),
        "third_att": int(len(third)),
        "third_pct": float(third.third_down_converted.fillna(0).mean()) if len(third) else None,
        "rz_plays": int(len(rz)),
        "rz_pct": float(rz.touchdown.fillna(0).mean()) if len(rz) else None,
        "explosive_plays": int((off.yards_gained.fillna(0) >= EXPLOSIVE_YARDS).sum()),
        "epa_total": float(off_epa.epa.sum()) if len(off_epa) else None,
        "epa_play": float(off_epa.epa.mean()) if len(off_epa) else None,
    }


def quarter_epa_evolution(g_pbp):
    """EPA acumulado por cuarto y equipo. Devuelve {team: {"qtr": [...], "cum_epa": [...]}} o None."""
    d = g_pbp[g_pbp.epa.notna() & g_pbp.qtr.notna() & g_pbp.posteam.notna()]
    if d.empty:
        return None
    g = d.groupby(["posteam", "qtr"])["epa"].sum().reset_index()
    out = {}
    for team, sub in g.groupby("posteam"):
        sub = sub.sort_values("qtr")
        out[team] = {"qtr": sub.qtr.tolist(), "cum_epa": sub.epa.cumsum().tolist()}
    return out if len(out) == 2 else None


def key_factors(home_box, away_box, home_name, away_name):
    """Frases deterministas comparando los boxscores de ambos equipos. Sin puntuacion magica:
    cada frase sale de una comparacion directa de datos reales."""
    factors = []

    if home_box.get("epa_total") is not None and away_box.get("epa_total") is not None:
        leader = home_name if home_box["epa_total"] > away_box["epa_total"] else away_name
        factors.append(f"{leader} dominó en EPA total generado "
                        f"({home_box['epa_total']:+.1f} vs {away_box['epa_total']:+.1f}).")

    if home_box["turnovers"] != away_box["turnovers"]:
        fewer = home_name if home_box["turnovers"] < away_box["turnovers"] else away_name
        factors.append(f"{fewer} cuidó mejor el balón "
                        f"({home_box['turnovers']} vs {away_box['turnovers']} pérdidas).")

    if home_box.get("third_pct") is not None and away_box.get("third_pct") is not None:
        better = home_name if home_box["third_pct"] > away_box["third_pct"] else away_name
        factors.append(f"{better} fue más efectivo en 3ª down "
                        f"({home_box['third_pct']:.0%} vs {away_box['third_pct']:.0%}).")

    if home_box.get("rz_pct") is not None and away_box.get("rz_pct") is not None:
        better = home_name if home_box["rz_pct"] >= away_box["rz_pct"] else away_name
        factors.append(f"{better} convirtió mejor en zona roja "
                        f"({home_box['rz_pct']:.0%} vs {away_box['rz_pct']:.0%}).")

    if home_box["explosive_plays"] != away_box["explosive_plays"]:
        more = home_name if home_box["explosive_plays"] > away_box["explosive_plays"] else away_name
        factors.append(f"{more} generó más jugadas explosivas de {EXPLOSIVE_YARDS}+ yardas "
                        f"({home_box['explosive_plays']} vs {away_box['explosive_plays']}).")

    return factors
