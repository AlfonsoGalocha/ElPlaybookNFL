"""pages_app/home.py — home editorial: esta semana en la NFL, tendencias, duelo destacado y accesos."""

import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from analytics.efficiency import team_efficiency_table
from analytics.games import featured_game, highlight_week
from analytics.matchups import with_percentiles
from analytics.trends import MIN_WEEKS_FOR_TREND, trend_table, weekly_team_epa
from components.navbar import go_to
from data.loaders import load_pbp

WEEKDAY_ES = {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
              "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"}


def _madrid_time(gameday, gametime):
    try:
        naive = dt.datetime.strptime(f"{gameday} {gametime}", "%Y-%m-%d %H:%M")
        eastern = naive.replace(tzinfo=ZoneInfo("America/New_York"))
        return eastern.astimezone(ZoneInfo("Europe/Madrid"))
    except Exception:
        return None


def _game_card(g, team_meta):
    home_meta = team_meta.get(g.home_team, {})
    away_meta = team_meta.get(g.away_team, {})
    played = pd.notna(g.home_score) and pd.notna(g.away_score)
    madrid = _madrid_time(g.gameday, g.gametime)
    when = (f"{WEEKDAY_ES.get(madrid.strftime('%A'), madrid.strftime('%A')).capitalize()} "
            f"{madrid.strftime('%d/%m')} · {madrid.strftime('%H:%M')}h") if madrid else g.gameday

    if played:
        center = (f'<div class="game-score">{int(g.away_score)} - {int(g.home_score)}</div>'
                  f'<div class="game-final">FINAL</div>')
    else:
        center = f'<div class="game-vs">VS</div><div class="game-time">{when}</div>'

    return f"""
      <div class="game-card fade-up">
        <div class="game-team gt-home">
          <div class="gt-name">{home_meta.get('name', g.home_team)}</div>
          <img src="{home_meta.get('logo', '')}"/>
        </div>
        <div class="game-center"><div class="game-pill">{center}</div></div>
        <div class="game-team gt-away">
          <img src="{away_meta.get('logo', '')}"/>
          <div class="gt-name">{away_meta.get('name', g.away_team)}</div>
        </div>
      </div>"""


def _access_card(col, icon, title, sub, page):
    with col:
        st.markdown(f"""
          <div class="stat-card fade-up" style="margin-bottom:.6rem">
            <div class="sc-label">{icon} {title.upper()}</div>
            <div class="sc-value" style="font-size:1.1rem; font-family:'Inter'; font-weight:600">{sub}</div>
          </div>""", unsafe_allow_html=True)
        if st.button(f"Ir a {title} →", key=f"home_go_{page}", use_container_width=True):
            go_to(page)


def render(ctx):
    st.markdown('<div class="sect-title">Esta semana en la NFL</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Entiende la NFL. No solo la sigas.</div>', unsafe_allow_html=True)

    week_options = sorted(ctx.sched.week.unique().tolist())
    current_week = highlight_week(ctx.sched)
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        st.markdown("#### Jornada · horarios en España")
    with hc2:
        week = st.selectbox("Jornada", week_options,
                            index=week_options.index(current_week) if current_week in week_options else 0,
                            key="home_week", label_visibility="collapsed")
    games = ctx.sched[ctx.sched.week == week].sort_values("gameday")
    if games.empty:
        st.info("Todavía no hay partidos programados para esta temporada.")
    else:
        game_list = list(games.itertuples())
        for i in range(0, len(game_list), 3):
            row = game_list[i:i + 3]
            cols = st.columns(3)
            for col, g in zip(cols, row):
                with col:
                    st.markdown(_game_card(g, ctx.team_meta), unsafe_allow_html=True)

    pbp = load_pbp(ctx.season)
    duel_game = None
    if pbp is not None and not pbp.empty and not games.empty:
        eff = team_efficiency_table(pbp).dropna(subset=["off_epa_play", "def_epa_play"])
        if len(eff) >= 2:
            pct = with_percentiles(eff)
            duel_game = featured_game(games, pct)

    if duel_game:
        g, d = duel_game
        st.markdown(f"""
          <div class="duel-card fade-up">
            <div class="dc-tag">⚔️ PARTIDO DESTACADO · JORNADA {week} · EL DUELO CLAVE</div>
            <div class="dc-title">{ctx.team_meta[g.away_team]['name']} @ {ctx.team_meta[g.home_team]['name']}</div>
            <div class="dc-detail">{d['label']}: EPA/jugada {d['off_epa']:+.3f} de ataque
            (percentil {d['off_pct']:.0f}) contra {d['def_epa']:+.3f} de EPA permitida en defensa
            (percentil {d['def_pct']:.0f}).</div>
          </div>""", unsafe_allow_html=True)
        if st.button("Ver el matchup completo →", type="primary"):
            go_to("matchups")

    if pbp is not None and not pbp.empty:
        n_weeks = pbp.week.nunique()
        if n_weeks >= MIN_WEEKS_FOR_TREND:
            weekly_epa = weekly_team_epa(pbp)
            result = trend_table(weekly_epa, "epa_play", weight_col="plays")
            if result:
                table = result["table"]
                riser = table.sort_values("delta", ascending=False).iloc[0]
                faller = table.sort_values("delta", ascending=True).iloc[0]
                st.markdown("#### Tendencias de la temporada")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"<div class='stat-card'><div class='sc-label'>📈 MÁS SUBE</div>"
                                f"<div class='sc-value'>{riser.team}</div>"
                                f"<div class='sc-label'>EPA/jugada {riser.early:+.3f} → {riser.recent:+.3f}"
                                f" <span class='up-badge'>({riser.delta:+.3f})</span></div></div>",
                                unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='stat-card'><div class='sc-label'>📉 MÁS BAJA</div>"
                                f"<div class='sc-value'>{faller.team}</div>"
                                f"<div class='sc-label'>EPA/jugada {faller.early:+.3f} → {faller.recent:+.3f}"
                                f" <span class='down-badge'>({faller.delta:+.3f})</span></div></div>",
                                unsafe_allow_html=True)
                if st.button("Ver todas las tendencias →"):
                    go_to("tendencias")

    st.markdown("#### Explora El Playbook")
    cols = st.columns(4)
    _access_card(cols[0], "🔬", "Laboratorio", "Eficiencia real de equipos y QBs (EPA, presión...)",
                 "laboratorio")
    _access_card(cols[1], "⚔️", "Matchups", "Compara dos equipos, ataque contra defensa", "matchups")
    _access_card(cols[2], "🎓", "Football IQ", "Aprende la NFL desde cero o profundiza", "football_iq")
    _access_card(cols[3], "🧠", "Quiz", "Pon a prueba lo que sabes", "quiz")
