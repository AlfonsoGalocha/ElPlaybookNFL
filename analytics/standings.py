"""analytics/standings.py — clasificacion (W-L-T, PF/PA) a partir del calendario."""

import numpy as np
import pandas as pd


def team_meta_table(teams_df, colors):
    out = {}
    for r in teams_df.iter_rows(named=True):
        out[r["team_abbr"]] = {
            "name": r["team_name"], "conf": r["team_conf"], "div": r["team_division"],
            "logo": r["team_logo_espn"], "color": colors.get(r["team_abbr"]),
        }
    return out


def standings_table(sched, meta):
    rows = {a: {"W": 0, "L": 0, "T": 0, "PF": 0, "PA": 0} for a in meta}
    for g in sched.itertuples():
        h, a = g.home_team, g.away_team
        hs, as_ = g.home_score, g.away_score
        if h not in rows or a not in rows or np.isnan(hs) or np.isnan(as_):
            continue
        rows[h]["PF"] += hs; rows[h]["PA"] += as_
        rows[a]["PF"] += as_; rows[a]["PA"] += hs
        if hs > as_:
            rows[h]["W"] += 1; rows[a]["L"] += 1
        elif hs < as_:
            rows[a]["W"] += 1; rows[h]["L"] += 1
        else:
            rows[h]["T"] += 1; rows[a]["T"] += 1
    out = []
    for a, r in rows.items():
        gp = r["W"] + r["L"] + r["T"]
        pct = (r["W"] + 0.5 * r["T"]) / gp if gp else 0.0
        out.append({"team": a, **r, "PCT": pct, "DIFF": int(r["PF"] - r["PA"]),
                    "conf": meta[a]["conf"], "division": meta[a]["div"]})
    return pd.DataFrame(out).sort_values("PCT", ascending=False).reset_index(drop=True)
