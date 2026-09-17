"""pages_app/jugadores.py — perfil de jugador: ficha, contexto de liga, evolución y tarjeta."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import nfl_graficos as G
from analytics.context import stat_context
from analytics.context import position_population as _position_population
from analytics.efficiency import (
    league_epa_by_position, player_recent_vs_season, player_season_epa, player_weekly_epa,
)
from analytics.explanations import breakdown_insight, epa_breakdown
from analytics.totals import full_totals_table, headline_stat, player_season
from analytics.utils import headshot_of, mode
from components.explanation import why_expander
from components.stat_context import stat_context_html
from components.tracking import track_player_viewed, track_share_result
from data.loaders import load_pbp

FAMOSOS = ["Patrick Mahomes", "Josh Allen", "Lamar Jackson", "Jalen Hurts",
           "Joe Burrow", "Ja'Marr Chase", "Justin Jefferson",
           "Christian McCaffrey", "Saquon Barkley", "Travis Kelce"]

FG, ACCENT, ACCENT2 = G.FG, G.ACCENT, G.ACCENT2


def _context_row(ctx, player, pos):
    """Tarjetas DATOS -> CONTEXTO: la métrica de cabecera de la posición + EPA/jugada si aplica."""
    totals = full_totals_table(ctx.pdf)
    pop = _position_population(totals, pos)
    row = totals[totals.player_display_name == player]
    if pop is None or row.empty:
        return

    cards = []
    hs = headline_stat(pos)
    if hs:
        label, col = hs
        if col in row.columns and col in pop.columns:
            value = float(row.iloc[0][col])
            c = stat_context(pop, col, value, population_label=f"{pos}")
            cards.append(stat_context_html(label.upper(), f"{value:,.0f}".replace(",", "."), c,
                                           subject=player, decimals=0))

    pid = None
    pbp = load_pbp(ctx.season)
    if pbp is not None and not pbp.empty:
        league_epa = league_epa_by_position(pbp, pos)
        player_id_row = ctx.pdf[ctx.pdf.player_display_name == player]["player_id"]
        if league_epa is not None and len(player_id_row):
            pid = mode(player_id_row)
            weekly = player_weekly_epa(pbp, pid, pos)
            season_epa = player_season_epa(weekly)
            if season_epa is not None:
                c = stat_context(league_epa, "epa_play", season_epa, population_label=f"{pos}")
                cards.append(stat_context_html("EPA / JUGADA", f"{season_epa:+.2f}", c,
                                               subject=player, decimals=2))

    if not cards:
        return
    st.markdown("#### 🧠 Contexto")
    cols = st.columns(len(cards))
    for col, html in zip(cols, cards):
        col.markdown(html, unsafe_allow_html=True)

    if (pos or "").upper() == "QB" and pid is not None:
        player_plays = pbp[(pbp.passer_player_id == pid) | (pbp.rusher_player_id == pid)]
        bd = epa_breakdown(player_plays)
        why_expander(bd, breakdown_insight(bd, subject=f"El rendimiento ofensivo de {player}"))


def _evolution_chart(ctx, player, pos):
    hs = headline_stat(pos)
    if not hs:
        return
    label, col = hs
    p = ctx.pdf[ctx.pdf.player_display_name == player].sort_values("week")
    if col not in p.columns:
        return
    if p.week.nunique() < 2:
        st.markdown(f"#### 📈 Evolución · {label}")
        st.caption("Necesitamos más jornadas de este jugador para mostrar una evolución.")
        return
    st.markdown(f"#### 📈 Evolución · {label}")
    fig = go.Figure(go.Scatter(x=p.week, y=p[col], mode="lines+markers",
                               line=dict(color=ACCENT, width=3), marker=dict(size=8)))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       height=280, margin=dict(l=10, r=20, t=10, b=10), font=dict(color=FG),
                       xaxis_title="Jornada", yaxis_title=label)
    st.plotly_chart(fig, use_container_width=True)


def _recent_form(ctx, player, pos):
    if (pos or "").upper() not in ("QB", "RB", "FB", "WR", "TE"):
        return
    pbp = load_pbp(ctx.season)
    if pbp is None or pbp.empty:
        return
    player_id_row = ctx.pdf[ctx.pdf.player_display_name == player]["player_id"]
    if not len(player_id_row):
        return
    pid = mode(player_id_row)
    weekly = player_weekly_epa(pbp, pid, pos)
    rf = player_recent_vs_season(weekly, recent_n=4)
    if rf is None:
        if weekly is not None and not weekly.empty:
            st.markdown("#### 🔥 Últimas jornadas")
            st.caption("Necesitamos más jornadas para comparar el rendimiento reciente con el de temporada.")
        return
    delta = rf["delta"]
    if delta > 0.03:
        insight = f"{player} está generando más valor por jugada en sus últimas jornadas que en el conjunto de la temporada."
    elif delta < -0.03:
        insight = f"{player} está rindiendo por debajo de su nivel de temporada en sus últimas jornadas."
    else:
        insight = f"{player} se mantiene estable respecto a su nivel de temporada."
    st.markdown("#### 🔥 Últimas jornadas")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-context-card"><div class="sxc-label">TEMPORADA · EPA/JUGADA</div>'
                    f'<div class="sxc-value">{rf["season_epa"]:+.2f}</div></div>', unsafe_allow_html=True)
    with c2:
        weeks_txt = f"últimas {len(rf['recent_weeks'])}" if len(rf["recent_weeks"]) < 4 else "últimas 4"
        st.markdown(f'<div class="stat-context-card"><div class="sxc-label">{weeks_txt.upper()} · EPA/JUGADA</div>'
                    f'<div class="sxc-value">{rf["recent_epa"]:+.2f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sxc-insight" style="margin-top:8px">🧠 {insight}</div>', unsafe_allow_html=True)


def render(ctx):
    st.markdown('<div class="sect-title">Jugadores</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Busca cualquier jugador y genera su tarjeta.</div>',
                unsafe_allow_html=True)

    if ("sel_player" not in st.session_state
            or st.session_state.sel_player not in ctx.all_names):
        st.session_state.sel_player = ("Josh Allen" if "Josh Allen" in ctx.all_names
                                       else ctx.all_names[0])

    def _pick(name):
        st.session_state.sel_player = name

    st.selectbox("🔍 Busca cualquier jugador", ctx.all_names, key="sel_player")

    famosos = [n for n in FAMOSOS if n in ctx.all_names][:6]
    if famosos:
        st.markdown("<div class='conf-h'>⭐ Destacados</div>", unsafe_allow_html=True)
        cols = st.columns(len(famosos))
        for col, name in zip(cols, famosos):
            with col:
                hs = headshot_of(ctx.pdf, name)
                if hs:
                    st.markdown(f"<div style='text-align:center'><img src='{hs}' "
                                f"style='width:70px;height:70px;border-radius:50%;"
                                f"object-fit:cover;border:2px solid rgba(255,255,255,.15)'></div>",
                                unsafe_allow_html=True)
                st.button(name, key=f"fam_{name}", on_click=_pick, args=(name,),
                          use_container_width=True)

    st.markdown("---")
    player = st.session_state.sel_player
    track_player_viewed(player)
    info = player_season(ctx.pdf, player)
    pos = info["pos"]
    headshot = headshot_of(ctx.pdf, player)
    st.markdown("<div class='conf-h'>Perfil del jugador</div>", unsafe_allow_html=True)
    st.markdown(f"""
      <div class="prof-hd fade-up">
        <img src="{headshot}"/>
        <div><div class="prof-name">{player.upper()}</div>
        <div class="prof-meta">{pos} · {info['team']} · Temporada {ctx.season}</div></div>
      </div>""", unsafe_allow_html=True)

    st.markdown("<div class='conf-h'>Estadísticas principales</div>", unsafe_allow_html=True)
    tiles = info["tiles"]
    m = st.columns(len(tiles))
    for col, (label, value) in zip(m, tiles):
        col.metric(label, value)

    _context_row(ctx, player, pos)
    _evolution_chart(ctx, player, pos)
    _recent_form(ctx, player, pos)

    st.markdown("#### 🪪 Genera su tarjeta")
    cc1, cc2 = st.columns([1, 1])
    modo = cc1.radio("Imagen", ["Cara (circulo)", "Cuerpo (imagen grande)"])
    modo_key = "circulo" if modo.startswith("Cara") else "cuerpo"
    up = cc2.file_uploader("Tu propia foto (opcional)", type=["png", "jpg", "jpeg"])
    if st.button("Generar tarjeta", type="primary"):
        foto = None
        if up is not None:
            from PIL import Image
            foto = np.asarray(Image.open(up).convert("RGBA")).astype(float) / 255.0
        with st.spinner("Generando tarjeta..."):
            fig = G.make_card(ctx.pdf, ctx.season, player, ctx.teams, modo_key, foto)
            png = G.fig_a_png(fig)
        track_share_result("player")
        st.image(png, width=340)
        fn = f"tarjeta_{player.lower().replace(' ', '_')}_{ctx.season}.png"
        st.download_button("⬇️ Descargar PNG", png, file_name=fn, mime="image/png")
