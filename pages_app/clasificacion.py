"""pages_app/clasificacion.py — clasificacion general y por conferencia/division."""

import streamlit as st


def _std_block_html(df, stats, team_meta):
    labels = {"PJ": "PJ", "V": "V", "D": "D", "E": "E", "PCT": "%",
              "PF": "PF", "PC": "PC", "DIF": "DIF"}
    head_stats = "".join(f'<div class="std-stat">{labels[s]}</div>' for s in stats)
    head = (f'<div class="std-head"><div class="std-rank">#</div><div class="std-logo"></div>'
            f'<div class="std-team">Equipo</div>{head_stats}</div>')
    rows = []
    for i, r in enumerate(df.itertuples(), 1):
        meta = team_meta[r.team]
        gp = r.W + r.L + r.T
        vals = {"PJ": gp, "V": r.W, "D": r.L, "E": r.T, "PCT": f"{r.PCT:.3f}",
                "PF": f"{r.PF:.0f}", "PC": f"{r.PA:.0f}", "DIF": f"{r.DIFF:+d}"}
        stat_html = "".join(f'<div class="std-stat">{vals[s]}</div>' for s in stats)
        rows.append(
            f'<div class="std-row fade-up d{min(i - 1, 9)}"><div class="std-rank">{i}</div>'
            f'<img class="std-logo" src="{meta["logo"]}"/>'
            f'<div class="std-team">{meta["name"]} <small>{r.team}</small></div>{stat_html}</div>'
        )
    return head + "".join(rows)


def render(ctx):
    st.markdown('<div class="sect-title">Clasificación</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Récord de la temporada regular, calculado a partir de los '
                'resultados oficiales.</div>', unsafe_allow_html=True)
    vista = st.radio("Vista", ["General", "Por conferencia"], horizontal=True,
                      key="std_scope", label_visibility="collapsed")

    standings, team_meta = ctx.standings, ctx.team_meta

    if vista == "General":
        st.markdown(_std_block_html(standings, ["PJ", "V", "D", "E", "PCT", "PF", "PC", "DIF"], team_meta),
                    unsafe_allow_html=True)
    else:
        for conf in ["AFC", "NFC"]:
            st.markdown(f'<div class="conf-h">{conf}</div>', unsafe_allow_html=True)
            cdf = standings[standings.conf == conf]
            divs = sorted(cdf["division"].unique())
            blocks = []
            for div in divs:
                ddf = cdf[cdf["division"] == div].sort_values("PCT", ascending=False)
                blocks.append(
                    f'<div class="div-block"><div class="div-h">{div}</div>'
                    f'{_std_block_html(ddf, ["V", "D", "E", "DIF"], team_meta)}</div>'
                )
            st.markdown(f'<div class="div-grid">{"".join(blocks)}</div>', unsafe_allow_html=True)
    st.caption("PJ partidos jugados · % porcentaje de victorias · PF/PC puntos a favor/en contra · "
               "DIF diferencia de puntos.")
