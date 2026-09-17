"""pages_app/laboratorio.py — eficiencia de equipos y QBs con datos reales (EPA, success rate, presión)."""

import plotly.graph_objects as go
import streamlit as st

import nfl_graficos as G
from analytics.efficiency import pressure_table, qb_efficiency_table, team_efficiency_table
from components.tracking import track_laboratory_viewed
from data.loaders import load_pbp, load_pfr

FG, CARD, ACCENT, ACCENT2 = G.FG, G.CARD, G.ACCENT, G.ACCENT2


def _bar(labels, values, colors, title, xlab="", fmt="{:+.3f}"):
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors,
                            text=[fmt.format(v) for v in values], textposition="outside"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       height=max(320, 32 * len(labels)), margin=dict(l=10, r=40, t=40, b=10),
                       font=dict(color=FG), showlegend=False, title=title, xaxis_title=xlab)
    fig.add_vline(x=0, line_color="rgba(255,255,255,.25)")
    st.plotly_chart(fig, use_container_width=True)


def render(ctx):
    st.markdown('<div class="sect-title">Laboratorio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Eficiencia real de equipos y jugadores, con EPA, success rate '
                'y presión — no solo estadísticas contables.</div>', unsafe_allow_html=True)
    track_laboratory_viewed()

    pbp = load_pbp(ctx.season)
    if pbp is None or pbp.empty:
        st.warning("No hay datos de jugada a jugada (play-by-play) disponibles todavía para esta "
                   "temporada. Prueba con una temporada completa, como 2025.")
        return

    vista = st.radio("Vista", ["Equipos", "Quarterbacks", "Presión"], horizontal=True,
                      key="lab_scope", label_visibility="collapsed")

    if vista == "Equipos":
        eff = team_efficiency_table(pbp)
        eff = eff.dropna(subset=["off_epa_play", "def_epa_play"])
        if eff.empty:
            st.info("Sin jugadas suficientes todavía para calcular eficiencia por equipo.")
            return
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Ataque · EPA por jugada")
            st.caption("Más alto = ataque más eficiente por jugada (no solo más yardas).")
            e = eff.sort_values("off_epa_play", ascending=True).tail(16)
            _bar(e.team, e.off_epa_play, [ctx.colors.get(t, ACCENT) for t in e.team], "")
        with c2:
            st.markdown("##### Defensa · EPA permitida por jugada")
            st.caption("Más bajo (más a la izquierda) = defensa más eficiente: concede menos por jugada.")
            e = eff.sort_values("def_epa_play", ascending=False).tail(16)
            _bar(e.team, e.def_epa_play, [ctx.colors.get(t, ACCENT2) for t in e.team], "")
        st.dataframe(
            eff.rename(columns={"team": "Equipo", "off_plays": "Jugadas ataque",
                                 "off_epa_play": "EPA/jugada (ataque)", "off_success": "% éxito ataque",
                                 "def_plays": "Jugadas defensa", "def_epa_play": "EPA/jugada permitida",
                                 "def_success": "% éxito permitido"})
            .sort_values("EPA/jugada (ataque)", ascending=False).set_index("Equipo"),
            use_container_width=True)

    elif vista == "Quarterbacks":
        min_db = st.slider("Mínimo de pases para entrar en la tabla", 5, 100, 20)
        qbs = qb_efficiency_table(pbp, min_dropbacks=min_db)
        if qbs.empty:
            st.info("Ningún QB llega todavía a ese mínimo de pases esta temporada. Baja el mínimo o "
                    "cambia de temporada.")
            return
        top = qbs.head(15)
        _bar(top.passer_player_name[::-1], top.epa_play[::-1],
             [ctx.colors.get(t, ACCENT) for t in top.team[::-1]], "EPA por pase, líderes de la temporada")
        st.dataframe(
            qbs.rename(columns={"passer_player_name": "QB", "team": "Equipo", "dropbacks": "Pases",
                                 "epa_play": "EPA/pase", "success_rate": "% éxito",
                                 "cpoe": "CPOE (aprox. pbp)", "air_yards": "Air yards medios"})
            .set_index("QB"), use_container_width=True)
        st.caption("EPA/pase y % de éxito calculados sobre jugadas de pase con EPA registrado en el "
                   "play-by-play de nflverse. CPOE aquí es la media directa de la columna `cpoe` del pbp.")

    else:  # Presión
        pfr = load_pfr("pass", ctx.season)
        pt = pressure_table(pfr)
        if pt.empty:
            st.info("No hay datos de presión (Pro Football Reference) disponibles para esta temporada.")
            return
        pt = pt[pt.times_pressured >= 10]
        if pt.empty:
            st.info("Ningún QB acumula todavía presiones suficientes esta temporada para una "
                    "comparación fiable.")
            return
        top = pt.sort_values("times_pressured_pct", ascending=False).head(15)
        _bar(top.pfr_player_name[::-1], top.times_pressured_pct[::-1],
             ["#E4203C"] * len(top), "% medio de presión sufrida por partido (más alto = más presionado)",
             fmt="{:.0%}")
        show = pt.rename(columns={"pfr_player_name": "QB", "team": "Equipo", "times_sacked": "Sacks",
                                   "times_hurried": "Apresurado", "times_hit": "Golpeado",
                                   "times_pressured": "Presiones totales",
                                   "times_pressured_pct": "% presión (media por partido)"}
                          ).sort_values("% presión (media por partido)", ascending=False).set_index("QB")
        st.dataframe(show.style.format({"% presión (media por partido)": "{:.0%}"}),
                     use_container_width=True)
        st.caption("Presiones totales sumadas de la temporada; el % es la media por partido jugado, "
                   "entre QBs con al menos 10 presiones sufridas en el año. "
                   "Datos de charting de Pro Football Reference vía nflverse (`load_pfr_advstats`).")
