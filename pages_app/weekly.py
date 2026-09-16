"""pages_app/weekly.py — El Playbook Weekly: "las 5 cosas que tienes que entender de esta
jornada". Pagina editorial que reutiliza analytics.weekly (automatizacion sin IA),
analytics.matchups/analytics.games (Duelo Clave — el mismo duelo que aparece en el hero de
arriba cuando estas en esta pagina), analytics.totals (jugadores destacados) y
content.football_iq_data (concepto de la semana). Nada aqui es una lista de tablas: cada
seccion explica un dato con contexto y una frase deterministica, no generada por IA.
"""

import plotly.graph_objects as go
import streamlit as st

import nfl_graficos as G
from analytics.games import completed_week
from analytics.totals import top_performers
from analytics.weekly import biggest_movers, has_enough_history, story_of_the_week
from content.football_iq_data import LEVEL_ORDER, LEVELS
from data.loaders import load_pbp

FG, ACCENT, ACCENT2 = G.FG, G.ACCENT, G.ACCENT2


def _more_weeks_needed(msg="Necesitamos más jornadas para detectar una tendencia fiable todavía."):
    st.caption(f"📊 {msg}")


def _story_section(pbp, week, team_meta):
    st.markdown('<div class="conf-h">🔥 La historia de la semana</div>', unsafe_allow_html=True)
    if not has_enough_history(week):
        _more_weeks_needed()
        return
    story = story_of_the_week(pbp, week, team_meta)
    if story is None:
        st.caption("Ningún equipo tuvo un cambio de rendimiento lo bastante grande esta semana "
                   "como para destacar como \"la historia\" — jornada de continuidad según los datos.")
        return
    verbo = "mejoró" if story["delta"] > 0 else "cayó"
    emoji = "📈" if story["delta"] > 0 else "📉"
    st.markdown(f"""
      <div class="stat-context-card fade-up">
        <div class="sxc-label">EPA/JUGADA OFENSIVO · {story['team_name'].upper()}</div>
        <div class="sxc-value">{story['cur_epa']:+.2f}</div>
        <div class="sxc-insight">{emoji} <b>{story['team_name']}</b> {verbo} de forma notable
        de la semana {story['prev_week']} a la semana {story['cur_week']}: de
        {story['prev_epa']:+.2f} a {story['cur_epa']:+.2f} EPA/jugada ofensivo
        (cambio de {story['delta']:+.2f}).</div>
      </div>""", unsafe_allow_html=True)
    fig = go.Figure(go.Bar(
        x=[f"Semana {story['prev_week']}", f"Semana {story['cur_week']}"],
        y=[story["prev_epa"], story["cur_epa"]],
        marker_color=["#5C6579", ACCENT if story["delta"] > 0 else "#C0392B"],
        text=[f"{story['prev_epa']:+.2f}", f"{story['cur_epa']:+.2f}"], textposition="outside"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       height=240, margin=dict(l=10, r=10, t=20, b=10), font=dict(color=FG),
                       yaxis_title="EPA/jugada", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _movers_section(pbp, week, team_meta):
    st.markdown('<div class="conf-h">📈📉 Quién sube, quién baja</div>', unsafe_allow_html=True)
    if not has_enough_history(week):
        _more_weeks_needed()
        return
    movers = biggest_movers(pbp, week)
    if movers is None or not (movers["improving"] or movers["declining"]):
        st.caption("Todavía no hay datos suficientes de dos jornadas seguidas para medir "
                   "mejoras o caídas de rendimiento equipo a equipo.")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🔺 Más mejoran (EPA/jugada)**")
        for r in movers["improving"]:
            name = team_meta.get(r["team"], {}).get("name", r["team"])
            st.markdown(f"- **{name}**: {r['epa_play_prev']:+.2f} → {r['epa_play_cur']:+.2f} "
                       f"(<span class='up-badge'>{r['delta']:+.2f}</span>)", unsafe_allow_html=True)
    with c2:
        st.markdown("**🔻 Más caen (EPA/jugada)**")
        for r in movers["declining"]:
            name = team_meta.get(r["team"], {}).get("name", r["team"])
            st.markdown(f"- **{name}**: {r['epa_play_prev']:+.2f} → {r['epa_play_cur']:+.2f} "
                       f"({r['delta']:+.2f})", unsafe_allow_html=True)


def _standouts_section(pdf, week, team_meta):
    st.markdown('<div class="conf-h">⭐ Jugadores destacados de la jornada</div>', unsafe_allow_html=True)
    top = top_performers(pdf, week, n=4)
    if top is None or top.empty:
        st.caption("Todavía no hay producción destacada registrada esta jornada.")
        return
    cols = st.columns(len(top))
    for col, row in zip(cols, top.itertuples()):
        p = pdf[(pdf.player_display_name == row.player_display_name) & (pdf.week == week)]
        tiles = G._tiles(row.position, G.player_totals(p))
        with col:
            st.markdown(f"**{row.player_display_name}**")
            st.caption(f"{row.position} · {row.team}")
            for tl, tv in tiles[:2]:
                st.metric(tl, tv)


def _matchup_section(ctx):
    st.markdown('<div class="conf-h">⚔️ Matchup de la semana</div>', unsafe_allow_html=True)
    duel = ctx.weekly_duel
    if duel is None:
        st.caption("Todavía no hay un duelo destacado que calcular para esta jornada — hace "
                   "falta más jugada a jugada de la temporada.")
        return
    st.markdown(f"""
      <div class="duel-card fade-up">
        <div class="dc-tag">⚔️ EL DUELO CLAVE DE LA SEMANA {ctx.weekly_week}</div>
        <div class="dc-title">{duel['label']}</div>
        <div class="dc-detail">EPA/jugada del ataque de {duel['off_team']}: <b>{duel['off_epa']:+.3f}</b>
        (percentil {duel['off_pct']:.0f}) frente a EPA/jugada permitida por la defensa de
        {duel['def_team']}: <b>{duel['def_epa']:+.3f}</b> (percentil {duel['def_pct']:.0f}).</div>
        <div class="dc-detail" style="margin-top:6px">{'Ventaja para el ataque' if duel['favours_offense'] else 'Ventaja para la defensa'}
        según los datos de esta temporada — el mismo duelo que ves arriba, en la cabecera.</div>
      </div>""", unsafe_allow_html=True)
    if st.button("Ver el matchup completo en Matchups →"):
        st.session_state.page = "matchups"
        st.rerun()


def _concept_of_week(week):
    all_terms = [(lvl, t) for lvl in LEVEL_ORDER for t in LEVELS[lvl]["terms"]]
    lvl, term = all_terms[(week or 1) % len(all_terms)]
    st.markdown('<div class="conf-h">🧠 Aprende esto</div>', unsafe_allow_html=True)
    st.markdown(f"""
      <div class="term-card fade-up">
        <span class="iq-level-tag {LEVELS[lvl]['css']}">{LEVELS[lvl]['title'].upper()}</span>
        <div class="tc-term" style="margin-top:8px">{term['term']}</div>
        <div class="tc-def">{term['def']}</div>
        <div class="tc-example">💡 {term['example']}</div>
      </div>""", unsafe_allow_html=True)
    if st.button("Aprender más conceptos →"):
        st.session_state.iq_level = lvl
        st.session_state.page = "football_iq"
        st.rerun()


def render(ctx):
    st.markdown('<div class="sect-title">EL PLAYBOOK WEEKLY</div>', unsafe_allow_html=True)
    week = ctx.weekly_week or completed_week(ctx.sched)
    if week is None:
        st.markdown('<div class="sect-sub">Todavía no se ha jugado ninguna jornada esta '
                    'temporada — vuelve cuando termine la primera semana.</div>',
                    unsafe_allow_html=True)
        return
    st.markdown(f'<div class="sect-sub">SEMANA {week} · TEMPORADA {ctx.season} — '
                f'las 5 cosas que tienes que entender de esta jornada.</div>', unsafe_allow_html=True)

    pbp = load_pbp(ctx.season)
    if pbp is None or pbp.empty:
        st.info("Todavía no hay datos de jugada a jugada disponibles para analizar esta jornada.")
        return

    _story_section(pbp, week, ctx.team_meta)
    st.markdown("---")
    _movers_section(pbp, week, ctx.team_meta)
    st.markdown("---")
    _standouts_section(ctx.pdf, week, ctx.team_meta)
    st.markdown("---")
    _matchup_section(ctx)
    st.markdown("---")
    _concept_of_week(week)

    st.caption("Todo lo anterior sale de comparar datos reales de esta jornada y la anterior — "
               "sin puntuaciones inventadas ni generación por IA.")
