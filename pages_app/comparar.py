"""pages_app/comparar.py — comparador de jugadores de la misma posicion (tabla + barras + radar)."""

from collections import Counter

import plotly.graph_objects as go
import streamlit as st

import nfl_graficos as G
from analytics.totals import full_totals_table, metrics_for_position

BG, CARD, FG, ACCENT = G.BG, G.CARD, G.FG, G.ACCENT


@st.dialog("⚠️ Solo se puede comparar la misma posición")
def _position_mismatch_dialog(positions):
    st.write("Has elegido jugadores de posiciones distintas, y no se pueden comparar entre si:")
    for name, pos in positions.items():
        st.write(f"- **{name}** — {pos or 'sin posición'}")
    st.write("Compara QB con QB, WR con WR, y asi sucesivamente.")
    keep_pos = Counter(positions.values()).most_common(1)[0][0]
    if st.button(f"Quedarme solo con los {keep_pos}", type="primary", use_container_width=True):
        st.session_state.cmp_players = [n for n, p in positions.items() if p == keep_pos]
        st.rerun()
    if st.button("Vaciar seleccion", use_container_width=True):
        st.session_state.cmp_players = []
        st.rerun()


def render(ctx):
    st.markdown('<div class="sect-title">Comparador</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Enfrenta a jugadores de la misma posición cara a cara.</div>',
                unsafe_allow_html=True)

    scope = st.radio("Ambito", ["Temporada completa", "Rango de jornadas"],
                     horizontal=True, key="cmp_scope")
    wr = None
    if scope == "Rango de jornadas" and len(ctx.weeks) > 1:
        wr = st.slider("Jornadas", min(ctx.weeks), max(ctx.weeks), (min(ctx.weeks), max(ctx.weeks)))

    totals = full_totals_table(ctx.pdf, wr)
    cnames = sorted(ctx.all_names)
    default = [n for n in ["Josh Allen", "Lamar Jackson", "Jalen Hurts"] if n in cnames][:2]
    picked = st.multiselect("🔍 Busca y elige jugadores a comparar (misma posición)",
                            cnames, default=default, key="cmp_players")

    if not picked:
        st.info("Elige al menos un jugador para empezar.")
        return

    sel = totals[totals.player_display_name.isin(picked)].copy()
    positions = dict(zip(sel.player_display_name, sel.position))
    unique_pos = sorted(set(positions.values()))
    if len(unique_pos) > 1:
        st.error("⚠️ Has elegido jugadores de posiciones distintas: "
                 + ", ".join(f"{n} ({p})" for n, p in positions.items()))
        _position_mismatch_dialog(positions)
        return

    pos = unique_pos[0]
    metric_map = metrics_for_position(pos)
    show = {"player_display_name": "Jugador", "position": "Pos", "team": "Equipo"}
    show.update({col: label for label, col in metric_map.items()})
    st.dataframe(sel[list(show)].rename(columns=show).set_index("Jugador"), use_container_width=True)

    metric_label = st.selectbox("Metrica del grafico de barras", list(metric_map.keys()), index=0)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<h3>{metric_label}</h3>", unsafe_allow_html=True)
        mcol = metric_map[metric_label]
        b = sel.sort_values(mcol)
        fig = go.Figure(go.Bar(
            x=b[mcol], y=b.player_display_name, orientation="h",
            marker_color=[ctx.colors.get(t, ACCENT) for t in b.team],
            text=b[mcol], textposition="outside"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=90 + 70 * len(b),
            margin=dict(l=10, r=30, t=10, b=10), font=dict(color=FG), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(f"<h3>Perfil comparado · {pos}</h3>", unsafe_allow_html=True)
        lbls, acols = list(metric_map.keys()), list(metric_map.values())
        mx = {c: max(sel[c].max(), 1) for c in acols}
        radar = go.Figure()
        for _, row in sel.iterrows():
            vv = [row[c] / mx[c] for c in acols]
            radar.add_trace(go.Scatterpolar(
                r=vv + [vv[0]], theta=lbls + [lbls[0]], fill="toself",
                name=row.player_display_name, line_color=ctx.colors.get(row.team, ACCENT)))
        radar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            polar=dict(bgcolor=CARD, radialaxis=dict(visible=True, range=[0, 1],
                showticklabels=False)), height=430,
            margin=dict(l=30, r=30, t=30, b=30), font=dict(color=FG),
            legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(radar, use_container_width=True)
    st.caption("El radar normaliza cada eje respecto al mejor de los elegidos.")
