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
from analytics.games import completed_week, featured_game, highlight_week
from analytics.matchups import with_percentiles
from analytics.standings import standings_table, team_meta_table
from components import footer, navbar
from components.hero import leader_widget_html, matchup_widget_html, news_widget_html
from components.navbar import go_to
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

page = st.session_state.get("page", navbar.DEFAULT_PAGE)

weekly_week, weekly_duel = None, None
pbp = load_pbp(season)
pct = None
if pbp is not None and not pbp.empty:
    eff = team_efficiency_table(pbp).dropna(subset=["off_epa_play", "def_epa_play"])
    pct = with_percentiles(eff) if len(eff) >= 2 else None

    # En "El Playbook Weekly" el duelo del hero es el de la jornada que se esta
    # repasando (la ultima jugada), no el de la proxima jornada como en el resto de la app.
    if page == "weekly":
        weekly_week = completed_week(sched)
        if weekly_week is not None and pct is not None:
            fg = featured_game(sched[sched.week == weekly_week], pct)
            if fg:
                _g, weekly_duel = fg

hero_week = weekly_week if page == "weekly" else highlight_week(sched)

# Widget dinamico de la derecha del hero: Partido de la Semana > lider de la
# clasificacion > ultima noticia — el primero con datos suficientes gana.
widget_html = None
if pct is not None and hero_week is not None:
    week_games = sched[sched.week == hero_week]
    if not week_games.empty:
        fg = featured_game(week_games, pct)
        if fg:
            g, _d = fg
            away = {"abbr": g.away_team, "name": team_meta[g.away_team]["name"],
                    "logo": team_meta[g.away_team]["logo"]}
            home = {"abbr": g.home_team, "name": team_meta[g.home_team]["name"],
                    "logo": team_meta[g.home_team]["logo"]}
            widget_html = matchup_widget_html("🔥 PARTIDO DE LA SEMANA", hero_week, away, home)

if widget_html is None and not standings.empty:
    leader = standings.iloc[0]
    lmeta = team_meta[leader.team]
    record = f"{int(leader.W)}-{int(leader.L)}-{int(leader.T)} · {leader.PCT:.3f} PCT"
    widget_html = leader_widget_html("🏆 LÍDER DE LA CLASIFICACIÓN", lmeta["name"], lmeta["logo"], record)

if widget_html is None:
    news = get_news()
    title, link = news[0] if news else ("Bienvenido a El Playbook NFL", "#")
    widget_html = news_widget_html("📰 ÚLTIMA HORA", title, link)

with st.container(key="hero_banner"):
    hero_l, hero_r = st.columns([3, 2], vertical_alignment="center")
    with hero_l:
        st.markdown(
            '<div class="hero-badge">🏈 NFL · ÚLTIMA HORA</div>'
            '<div class="hero-headline">RANKINGS, CLASIFICACIÓN Y EQUIPOS EN UN SOLO LUGAR</div>'
            '<div class="hero-sub">Entiende la NFL de verdad: clasificación en vivo, análisis de cada '
            'equipo y las estadísticas que importan, todo en un solo lugar.</div>',
            unsafe_allow_html=True)
        if st.button("Ver la clasificación completa →", type="primary"):
            go_to("clasificacion")
    with hero_r:
        st.markdown(widget_html, unsafe_allow_html=True)

ctx = SimpleNamespace(
    season=season, pdf=pdf, teams_df=teams_df, teams=teams, colors=colors,
    sched=sched, team_meta=team_meta, standings=standings, weeks=weeks,
    all_names=all_names, all_teams=all_teams, logo_b64=LOGO_B64,
    weekly_week=weekly_week, weekly_duel=weekly_duel,
)

PAGE_MODULES = {}


def _page(key):
    if key not in PAGE_MODULES:
        import importlib
        PAGE_MODULES[key] = importlib.import_module(f"pages_app.{key}")
    return PAGE_MODULES[key]


try:
    _page(page).render(ctx)
except ModuleNotFoundError:
    st.session_state.page = navbar.DEFAULT_PAGE
    _page(navbar.DEFAULT_PAGE).render(ctx)

footer.render(LOGO_B64)
