"""components/leaderboard.py — filas de ranking tipo leaderboard (foto, medalla, barra)."""

from analytics.utils import mode

import nfl_graficos as G

ACCENT = G.ACCENT


def leaderboard_data(pdf, colors, stat_col, week, n):
    d = pdf if week is None else pdf[pdf["week"] == week]
    g = d.groupby("player_display_name").agg(
        value=(stat_col, "sum"), team=("team", mode), pos=("position", mode),
        headshot=("headshot_url", lambda s: s.dropna().iloc[0] if s.dropna().size else ""),
    ).reset_index()
    g = g[g["value"] > 0].sort_values("value", ascending=False).head(n)
    return [dict(name=r.player_display_name, team=r.team, pos=r.pos, value=r.value,
                 headshot=r.headshot, color=colors.get(r.team, ACCENT))
            for _, r in g.iterrows()]


def leaderboard_html(rows, stat_key):
    _, _, suffix, dec = G.STATS[stat_key]
    maxv = max((r["value"] for r in rows), default=1) or 1
    medal = {0: "rank-1", 1: "rank-2", 2: "rank-3"}
    out = []
    for i, r in enumerate(rows):
        pct = max(6, r["value"] / maxv * 100)
        val = f"{r['value']:,.{dec}f}".replace(",", ".")
        dcls = f"fade-up d{min(i, 9)}"
        out.append(
            f'<div class="lb-row {dcls}"><div class="lb-rank {medal.get(i, "")}">{i+1}</div>'
            f'<img class="lb-photo" src="{r["headshot"]}" />'
            f'<div class="lb-info"><div class="lb-name">{r["name"]}</div>'
            f'<div class="lb-meta">{r["pos"]} · {r["team"]}</div>'
            f'<div class="lb-track"><div class="lb-fill" '
            f'style="width:{pct:.0f}%;background:{r["color"]}"></div></div></div>'
            f'<div class="lb-value">{val}<span>{suffix}</span></div></div>'
        )
    return "".join(out)
