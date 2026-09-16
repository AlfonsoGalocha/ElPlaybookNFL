"""pages_app/rankings.py — leaderboard de una metrica, temporada completa o por jornada."""

import streamlit as st

import nfl_graficos as G
from components.leaderboard import leaderboard_data, leaderboard_html


def render(ctx):
    st.markdown('<div class="sect-title">Rankings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Los lideres de la temporada, jornada a jornada o acumulados.</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 1])
    stat_label = c1.selectbox("Metrica", [v[1] for v in G.STATS.values()], index=0)
    stat_key = [k for k, v in G.STATS.items() if v[1] == stat_label][0]
    ambito = c2.selectbox("Ambito", ["Temporada completa"] + [f"Jornada {w}" for w in ctx.weeks])
    top_n = c3.slider("Top", 5, 15, 10)
    week = None if ambito == "Temporada completa" else int(ambito.split()[1])

    rows = leaderboard_data(ctx.pdf, ctx.colors, G.STATS[stat_key][0], week, top_n)
    sub = "Temporada completa" if week is None else f"Jornada {week}"
    st.markdown(f"<h3 style='margin:.6rem 0 1rem'>{stat_label} · {sub}</h3>", unsafe_allow_html=True)
    st.markdown(leaderboard_html(rows, stat_key), unsafe_allow_html=True)

    with st.expander("⬇️ Descargar como imagen vertical (para subir)"):
        if st.button("Generar PNG del ranking", type="primary"):
            with st.spinner("Generando..."):
                fig = G.make_ranking(ctx.pdf, ctx.season, week, stat_key, top_n, ctx.teams)
                png = G.fig_a_png(fig)
            st.image(png, width=320)
            fn = f"ranking_{stat_key}_{ctx.season}" + (f"_j{week}" if week else "") + ".png"
            st.download_button("Descargar PNG", png, file_name=fn, mime="image/png")
