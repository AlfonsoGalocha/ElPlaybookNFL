"""pages_app/clasificacion.py — clasificacion general y por conferencia/division.

Cada fila de equipo es clicable (boton invisible superpuesto sobre la fila) y lleva a
su ficha detallada en la pagina Equipos.
"""

import streamlit as st

from components.navbar import go_to

_LABELS = {"PJ": "PJ", "V": "V", "D": "D", "E": "E", "PCT": "%",
           "PF": "PF", "PC": "PC", "DIF": "DIF"}


def _std_head_html(stats):
    head_stats = "".join(f'<div class="std-stat">{_LABELS[s]}</div>' for s in stats)
    return (f'<div class="std-head"><div class="std-rank">#</div><div class="std-logo"></div>'
            f'<div class="std-team">Equipo</div>{head_stats}</div>')


def _std_row_html(rank, r, meta, stats):
    gp = r.W + r.L + r.T
    vals = {"PJ": gp, "V": r.W, "D": r.L, "E": r.T, "PCT": f"{r.PCT:.3f}",
            "PF": f"{r.PF:.0f}", "PC": f"{r.PA:.0f}", "DIF": f"{r.DIFF:+d}"}
    stat_html = "".join(f'<div class="std-stat">{vals[s]}</div>' for s in stats)
    return (
        f'<div class="std-row fade-up d{min(rank - 1, 9)}"><div class="std-rank">{rank}</div>'
        f'<img class="std-logo" src="{meta["logo"]}"/>'
        f'<div class="std-team">{meta["name"]} <small>{r.team}</small></div>{stat_html}</div>'
    )


def _render_std_block(df, stats, team_meta):
    st.markdown(_std_head_html(stats), unsafe_allow_html=True)
    for i, r in enumerate(df.itertuples(), 1):
        with st.container(key=f"std_row_{r.team}"):
            st.markdown(_std_row_html(i, r, team_meta[r.team], stats), unsafe_allow_html=True)
            if st.button(" ", key=f"std_click_{r.team}"):
                go_to("equipos", sel_team=r.team)


def render(ctx):
    st.markdown('<div class="sect-title">Clasificación</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Récord de la temporada regular, calculado a partir de los '
                'resultados oficiales. Haz clic en un equipo para ver su ficha completa.</div>',
                unsafe_allow_html=True)
    vista = st.radio("Vista", ["General", "Por conferencia"], horizontal=True,
                      key="std_scope", label_visibility="collapsed")

    standings, team_meta = ctx.standings, ctx.team_meta

    if vista == "General":
        _render_std_block(standings, ["PJ", "V", "D", "E", "PCT", "PF", "PC", "DIF"], team_meta)
    else:
        for conf in ["AFC", "NFC"]:
            st.markdown(f'<div class="conf-h">{conf}</div>', unsafe_allow_html=True)
            cdf = standings[standings.conf == conf]
            divs = sorted(cdf["division"].unique())
            col_a, col_b = st.columns(2)
            for i, div in enumerate(divs):
                with (col_a if i % 2 == 0 else col_b):
                    st.markdown(f'<div class="div-h">{div}</div>', unsafe_allow_html=True)
                    ddf = cdf[cdf["division"] == div].sort_values("PCT", ascending=False)
                    _render_std_block(ddf, ["V", "D", "E", "DIF"], team_meta)
    st.caption("PJ partidos jugados · % porcentaje de victorias · PF/PC puntos a favor/en contra · "
               "DIF diferencia de puntos.")
