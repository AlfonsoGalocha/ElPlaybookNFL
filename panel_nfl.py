#!/usr/bin/env python3
"""
panel_nfl.py — EL PLAYBOOK NFL · entrypoint de la app.

Ensambla la navbar, carga los datos base (jugadores/equipos/calendario) y
despacha a la pagina activa (pages_app/*.py) segun st.session_state.page.
El resto de la logica vive repartida en modulos:

  data/        - unico punto de contacto con nflreadpy (cacheado)
  analytics/   - funciones puras de agregacion (sin streamlit)
  components/  - piezas de UI reutilizables (navbar, hero, footer, css...)
  pages_app/   - una pagina por modulo, cada una expone render(ctx)
  content/     - contenido editorial (Football IQ, banco de preguntas del Quiz)
  share/       - generacion de imagenes verticales para compartir
  nfl_graficos.py - generacion de PNG de rankings y tarjetas de jugador (legado, se mantiene)

Lanzar:  streamlit run panel_nfl.py
"""

import base64
from types import SimpleNamespace

import streamlit as st
from matplotlib.colors import to_hex

import nfl_graficos as G
from analytics.efficiency import team_efficiency_table
from analytics.games import featured_game, highlight_week
from analytics.matchups import with_percentiles
from analytics.standings import standings_table, team_meta_table
from components import footer, navbar
from components.hero import brand_slide, duel_slide, hero_html, player_slide, top_teams_slide
from components.leaderboard import leaderboard_data
from components.styles import css_block
from data.loaders import get_news, load_pbp, load_schedules, load_season, load_teams

LOGO_PATH = "logo.png"
LOGO_B64 = base64.b64encode(open(LOGO_PATH, "rb").read()).decode()

st.set_page_config(page_title="El Playbook NFL", page_icon=LOGO_PATH, layout="wide")
st.markdown(css_block(), unsafe_allow_html=True)

season = navbar.render(LOGO_B64)

pdf = load_season(season)
teams_df = load_teams()
teams = G.team_info(teams_df)
colors = {a: to_hex(c) for a, (c, _) in teams.items()}
sched = load_schedules(season)
season_teams = set(sched.home_team) | set(sched.away_team)
team_meta = {a: m for a, m in team_meta_table(teams_df, colors).items() if a in season_teams}
standings = standings_table(sched, team_meta)
weeks = sorted(pdf["week"].unique().tolist())
all_names = sorted(pdf.player_display_name.dropna().unique().tolist())
all_teams = sorted(team_meta.keys())

feature_slides = [brand_slide(LOGO_B64, i=0)]

top3 = standings.sort_values("PCT", ascending=False).head(3)
if len(top3) >= 3:
    top3_data = [(r.team, team_meta[r.team]["name"], team_meta[r.team]["logo"]) for r in top3.itertuples()]
    feature_slides.append(top_teams_slide(top3_data, i=len(feature_slides)))

pbp = load_pbp(season)
if pbp is not None and not pbp.empty:
    hero_week = highlight_week(sched)
    week_games = sched[sched.week == hero_week]
    eff = team_efficiency_table(pbp).dropna(subset=["off_epa_play", "def_epa_play"])
    if len(eff) >= 2 and not week_games.empty:
        pct = with_percentiles(eff)
        fg = featured_game(week_games, pct)
        if fg:
            g, _d = fg
            feature_slides.append(duel_slide(
                hero_week,
                {"abbr": g.away_team, "logo": team_meta[g.away_team]["logo"]},
                {"abbr": g.home_team, "logo": team_meta[g.home_team]["logo"]},
                i=len(feature_slides)))

top_passers = leaderboard_data(pdf, colors, "passing_yards", None, 1)
if top_passers:
    p = top_passers[0]
    feature_slides.append(player_slide(
        p["name"], p["headshot"], "Yardas de pase esta temporada",
        f"{p['value']:,.0f}".replace(",", "."), i=len(feature_slides)))

st.markdown(hero_html(feature_slides, get_news()), unsafe_allow_html=True)

ctx = SimpleNamespace(
    season=season, pdf=pdf, teams_df=teams_df, teams=teams, colors=colors,
    sched=sched, team_meta=team_meta, standings=standings, weeks=weeks,
    all_names=all_names, all_teams=all_teams, logo_b64=LOGO_B64,
)

PAGE_MODULES = {}


def _page(key):
    if key not in PAGE_MODULES:
        import importlib
        PAGE_MODULES[key] = importlib.import_module(f"pages_app.{key}")
    return PAGE_MODULES[key]


page = st.session_state.get("page", navbar.DEFAULT_PAGE)
try:
    _page(page).render(ctx)
except ModuleNotFoundError:
    st.session_state.page = navbar.DEFAULT_PAGE
    _page(navbar.DEFAULT_PAGE).render(ctx)

footer.render(LOGO_B64)
