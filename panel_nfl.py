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
import os
from types import SimpleNamespace

import streamlit as st
from matplotlib.colors import to_hex

import nfl_graficos as G
from analytics.efficiency import team_efficiency_table
from analytics.games import completed_week, featured_game, highlight_week
from analytics.matchups import with_percentiles
from analytics.standings import standings_table, team_meta_table
from analytics.totals import top_performers
from analytics.utils import headshot_of
from analytics.weekly import story_of_the_week
from components import footer, navbar
from components.head_tags import head_injection_html
from components.hero import (
    leader_widget_html, matchup_widget_html, news_widget_html, player_widget_html,
    top_teams_widget_html,
)
from components.navbar import TIKTOK_URL, go_to
from components.styles import css_block
from data.loaders import get_news, load_pbp, load_schedules, load_season, load_teams

HERO_SLIDE_COUNT = 5

LOGO_PATH = "logo.png"
LOGO_B64 = base64.b64encode(open(LOGO_PATH, "rb").read()).decode()

HERO_IMAGES_DIR = "assets/hero"
_HERO_IMG_EXTS = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}


def hero_image_b64(slide_key):
    """Busca assets/hero/<slide_key>.(jpg|jpeg|png|webp) y lo devuelve como data URI, o
    None si todavia no se ha subido ninguna imagen para ese slide (el hero se ve bien sin ella)."""
    for ext, mime in _HERO_IMG_EXTS.items():
        path = os.path.join(HERO_IMAGES_DIR, f"{slide_key}{ext}")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f"data:image/{mime};base64,{data}"
    return None

st.set_page_config(
    page_title="El Playbook NFL — Estadísticas y análisis de la NFL en español",
    page_icon=LOGO_PATH, layout="wide")

_head_html = head_injection_html()
if _head_html:
    st.markdown(_head_html, unsafe_allow_html=True)

st.markdown(css_block(), unsafe_allow_html=True)

season = navbar.render(LOGO_B64)

# Los datos base (jugadores/equipos/calendario) vienen de nflreadpy, que a su vez
# descarga de GitHub — si la red o la fuente fallan, mostramos un error claro en
# vez de dejar caer la app entera con un traceback crudo.
try:
    pdf = load_season(season)
    teams_df = load_teams()
    sched = load_schedules(season)
except Exception:
    st.error(
        "⚠️ No se han podido cargar los datos de la NFL en este momento. "
        "Puede ser un problema temporal de conexión con la fuente de datos — "
        "prueba a recargar la página en unos minutos.")
    st.stop()

teams = G.team_info(teams_df)
colors = {a: to_hex(c) for a, (c, _) in teams.items()}
season_teams = set(sched.home_team) | set(sched.away_team)
team_meta = {a: m for a, m in team_meta_table(teams_df, colors).items() if a in season_teams}
standings = standings_table(sched, team_meta)
weeks = sorted(pdf["week"].unique().tolist())
all_names = sorted(pdf.player_display_name.dropna().unique().tolist())
all_teams = sorted(team_meta.keys())

page = st.session_state.get("page", navbar.DEFAULT_PAGE)

pbp = load_pbp(season)  # ya devuelve None con gracia si la fuente falla
pct = None
if pbp is not None and not pbp.empty:
    eff = team_efficiency_table(pbp).dropna(subset=["off_epa_play", "def_epa_play"])
    pct = with_percentiles(eff) if len(eff) >= 2 else None

played_week = completed_week(sched)  # ultima jornada ya disputada, o None
upcoming_week = highlight_week(sched)  # proxima jornada sin jugar (o la ultima, si acabo la temporada)

# En "El Playbook Weekly" el duelo del hero es el de la jornada que se esta repasando
# (la ultima jugada), no el de la proxima jornada como en el resto de la app.
weekly_week, weekly_duel = None, None
if page == "weekly" and played_week is not None and pct is not None:
    fg = featured_game(sched[sched.week == played_week], pct)
    if fg:
        weekly_week = played_week
        _g, weekly_duel = fg

if page == "home":
    # --- Slide 1: Highlights de la jornada (mayor cambio de EPA/jugada semana a semana) ---
    story = (story_of_the_week(pbp, played_week, team_meta)
             if pbp is not None and not pbp.empty and played_week else None)
    slide_highlights = {
        "badge": "🎬 HIGHLIGHTS DE LA JORNADA", "headline": "", "sub": "",
        "widget": None,
        "cta": ("Ver El Playbook Weekly →", "weekly", {}) if story else None,
        "image": hero_image_b64("highlights"),
        "link": {"type": "external", "url": TIKTOK_URL},
    }

    # --- Slide 2: General (con el podio de los 3 primeros de la clasificacion) ---
    top3_teams = []
    for i, row in enumerate(standings.head(3).itertuples(), start=1):
        m = team_meta[row.team]
        top3_teams.append({
            "rank": i, "logo": m["logo"], "name": m["name"],
            "record": f"{int(row.W)}-{int(row.L)}-{int(row.T)}",
        })

    slide_general = {
        "badge": "🏈 NFL · ÚLTIMA HORA",
        "headline": "RANKINGS, CLASIFICACIÓN Y EQUIPOS EN UN SOLO LUGAR",
        "sub": "Entiende la NFL de verdad: clasificación en vivo, análisis de cada equipo y las "
               "estadísticas que importan, todo en un solo lugar.",
        "widget": None, "cta": ("Ver la clasificación completa →", "clasificacion", {}),
        "graphic": top_teams_widget_html(top3_teams) if top3_teams else None,
        "link": {"type": "internal", "page": "clasificacion", "extra": {}},
    }

    # --- Slide 3: Mejor jugador de la jornada (MVP) ---
    mvp_widget, mvp_name = None, None
    if played_week is not None:
        top = top_performers(pdf, played_week, n=1)
        if top is not None and not top.empty:
            row = top.iloc[0]
            p = pdf[(pdf.player_display_name == row.player_display_name) & (pdf.week == played_week)]
            tiles = G._tiles(row.position, G.player_totals(p))[:3]
            mvp_widget = player_widget_html("🥇 MVP DE LA JORNADA", row.player_display_name,
                                             headshot_of(pdf, row.player_display_name),
                                             row.team, row.position or "", tiles)
            mvp_name = row.player_display_name

    mvp_image = hero_image_b64("mvp")
    mvp_link_extra = {"sel_player": mvp_name} if mvp_name else {}
    if mvp_widget:
        slide_mvp = {
            "badge": "🥇 MEJOR JUGADOR DE LA JORNADA", "headline": mvp_name.upper(),
            "sub": f"La actuación más destacada de la semana {played_week}, según producción real "
                   "(touchdowns y yardas).",
            "widget": mvp_widget,
            "cta": ("Ver ficha completa →", "jugadores", {"sel_player": mvp_name}),
            "image": mvp_image,
            "link": {"type": "internal", "page": "jugadores", "extra": mvp_link_extra},
        }
    else:
        slide_mvp = {
            "badge": "🥇 MEJOR JUGADOR DE LA JORNADA", "headline": "TODAVÍA SIN DATOS DE ESTA JORNADA",
            "sub": "En cuanto se jueguen partidos, aquí aparecerá el jugador con más producción de la semana.",
            "widget": None, "cta": None, "image": mvp_image,
            "link": {"type": "internal", "page": "jugadores", "extra": mvp_link_extra},
        }

    # --- Slide 4: Proximo partido clave (Duelo Clave) > lider de la clasificacion > noticia ---
    big_game_widget, big_game_badge, big_game_headline, big_game_sub, big_game_cta = (None,) * 5
    big_game_link = None
    if pct is not None and upcoming_week is not None:
        week_games = sched[sched.week == upcoming_week]
        if not week_games.empty:
            fg = featured_game(week_games, pct)
            if fg:
                g, _d = fg
                away = {"abbr": g.away_team, "name": team_meta[g.away_team]["name"],
                        "logo": team_meta[g.away_team]["logo"]}
                home = {"abbr": g.home_team, "name": team_meta[g.home_team]["name"],
                        "logo": team_meta[g.home_team]["logo"]}
                big_game_widget = matchup_widget_html("🔥 DUELO CLAVE", upcoming_week, away, home)
                big_game_badge = "🏈 PRÓXIMO PARTIDO CLAVE"
                big_game_headline = f"{away['abbr']} @ {home['abbr']} · SEMANA {upcoming_week}"
                big_game_sub = "El emparejamiento con mayor brecha de percentil de EPA/jugada de la próxima jornada."
                big_game_cta = ("Ver el matchup completo →", "matchups", {})
                big_game_link = {"type": "internal", "page": "matchups", "extra": {}}

    if big_game_widget is None and not standings.empty:
        leader = standings.iloc[0]
        lmeta = team_meta[leader.team]
        record = f"{int(leader.W)}-{int(leader.L)}-{int(leader.T)} · {leader.PCT:.3f} PCT"
        big_game_widget = leader_widget_html("🏆 LÍDER DE LA CLASIFICACIÓN", lmeta["name"], lmeta["logo"], record)
        big_game_badge, big_game_headline = "🏆 LÍDER DE LA CLASIFICACIÓN", lmeta["name"].upper()
        big_game_sub = "Todavía no hay suficiente jugada a jugada esta temporada — de momento, quién manda en la clasificación."
        big_game_cta = ("Ver la clasificación completa →", "clasificacion", {})
        big_game_link = {"type": "internal", "page": "clasificacion", "extra": {}}

    if big_game_widget is None:
        news = get_news()
        title, link = news[0] if news else ("Bienvenido a El Playbook NFL", "#")
        big_game_widget = news_widget_html("📰 ÚLTIMA HORA", title, link)
        big_game_badge, big_game_headline = "📰 ÚLTIMA HORA", "MANTENTE AL DÍA"
        big_game_sub = "Todavía no hay suficientes datos de la temporada — aquí tienes la última noticia."
        # el propio widget ya es un enlace (news_widget_html) — no lo envolvemos otra vez.

    slide_big_game = {
        "badge": big_game_badge, "headline": big_game_headline, "sub": big_game_sub,
        "widget": big_game_widget, "cta": big_game_cta, "image": hero_image_b64("big_game"),
        "link": big_game_link,
    }

    # --- Slide 5: Trivia ---
    slide_trivia = {
        "badge": "🧠 APRENDE NFL",
        "headline": "¿CUÁNTO SABES DE FÚTBOL AMERICANO?",
        "sub": "Pon a prueba lo que sabes con nuestro Quiz interactivo, desde nivel Rookie hasta Avanzado.",
        "widget": None, "cta": ("Empezar el Quiz →", "quiz", {}), "image": hero_image_b64("trivia"),
        "link": {"type": "internal", "page": "quiz", "extra": {}},
    }

    hero_slides = [slide_highlights, slide_general, slide_mvp, slide_big_game, slide_trivia]

    if "hero_slide" not in st.session_state:
        st.session_state.hero_slide = 0
    hero_idx = st.session_state.hero_slide % HERO_SLIDE_COUNT
    slide = hero_slides[hero_idx]

    with st.container(key="hero_banner"):
        if slide.get("image"):
            # Fondo a sangre de toda la tarjeta (no una imagen-caja dentro de la caja):
            # background-image en el propio contenedor, no un <img> absoluto — un <img>
            # con position:absolute;height:100% no puede calcular su alto porque el
            # contenedor solo tiene min-height (auto), no un alto explicito.
            st.markdown(
                f'<style>div[class*="st-key-hero_banner"] {{ background-image: '
                f'linear-gradient(180deg, rgba(8,10,16,.15) 0%, rgba(8,10,16,.6) 65%, rgba(8,10,16,.88) 100%), '
                f'url(\'{slide["image"]}\'); }}</style>',
                unsafe_allow_html=True)

        arrow_l, hero_content, arrow_r = st.columns([0.6, 11, 0.6], vertical_alignment="center")
        with arrow_l:
            if st.button("‹", key="hero_prev", use_container_width=True):
                st.session_state.hero_slide = (hero_idx - 1) % HERO_SLIDE_COUNT
                st.rerun()
        with hero_content:
            inner_html = ""
            if slide.get("graphic"):
                inner_html += f'<div class="hero-top3-wrap">{slide["graphic"]}</div>'
            inner_html += '<div class="hero-slide-body">'
            inner_html += f'<div class="hero-badge">{slide["badge"]}</div>'
            if slide.get("headline"):
                inner_html += f'<div class="hero-headline">{slide["headline"]}</div>'
            if slide.get("sub"):
                inner_html += f'<div class="hero-sub">{slide["sub"]}</div>'
            inner_html += '</div>'
            if slide["widget"]:
                inner_html += f'<div class="hero-widget-wrap">{slide["widget"]}</div>'

            link = slide.get("link")
            if link and link["type"] == "external":
                st.markdown(
                    f'<a class="hero-slide-link" href="{link["url"]}" target="_blank" rel="noopener">'
                    f'{inner_html}</a>', unsafe_allow_html=True)
            elif link and link["type"] == "internal":
                with st.container(key=f"hero_click_{hero_idx}"):
                    st.markdown(inner_html, unsafe_allow_html=True)
                    if st.button(" ", key=f"hero_ovl_{hero_idx}"):
                        go_to(link["page"], **link.get("extra", {}))
            else:
                st.markdown(inner_html, unsafe_allow_html=True)

            if slide["cta"]:
                cta_label, cta_page, cta_extra = slide["cta"]
                cta_l, cta_c, cta_r = st.columns([1, 1.3, 1])
                with cta_c:
                    if st.button(cta_label, type="primary", key=f"hero_cta_{hero_idx}",
                                 use_container_width=True):
                        go_to(cta_page, **cta_extra)
        with arrow_r:
            if st.button("›", key="hero_next", use_container_width=True):
                st.session_state.hero_slide = (hero_idx + 1) % HERO_SLIDE_COUNT
                st.rerun()

        dots = "".join(
            f'<span class="hero-dot{" active" if i == hero_idx else ""}"></span>'
            for i in range(HERO_SLIDE_COUNT))
        st.markdown(f'<div class="hero-dots">{dots}</div>', unsafe_allow_html=True)

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
