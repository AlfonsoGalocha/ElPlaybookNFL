"""
data/loaders.py — Unico punto de contacto con nflreadpy (y con el RSS de noticias).

Cualquier pagina que necesite datos de la NFL pasa por aqui. Asi el cacheo
(@st.cache_data) y las columnas que se cargan quedan en un solo sitio en vez
de repetidas por cada pagina.
"""

import urllib.request
import xml.etree.ElementTree as ET

import nflreadpy as nfl
import polars as pl
import streamlit as st

# Columnas de pbp que usa la app (de las 372 que trae nflverse). Cargar solo
# estas mantiene la memoria y el tiempo de carga razonables.
PBP_COLS = [
    "game_id", "season", "week", "season_type", "posteam", "defteam",
    "play_id", "down", "ydstogo", "yardline_100", "play_type",
    "pass_attempt", "rush_attempt", "pass", "rush", "sack", "qb_hit",
    "touchdown", "interception", "fumble_lost",
    "third_down_converted", "third_down_failed",
    "fourth_down_converted", "fourth_down_failed",
    "epa", "success", "air_yards", "yards_after_catch", "cpoe", "cp",
    "wpa", "shotgun", "no_huddle", "qb_dropback",
    "passer_player_name", "rusher_player_name", "receiver_player_name",
]


@st.cache_data(show_spinner="Cargando datos de la NFL...")
def load_season(season):
    """Stats semanales por jugador (ataque, defensa, kicking, punting), temporada regular."""
    df = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    return df.to_pandas()


@st.cache_resource
def load_teams():
    """Info de los 32+ equipos (nombre, conferencia, division, colores, logos)."""
    return nfl.load_teams()


@st.cache_data(show_spinner=False)
def load_schedules(season):
    """Calendario y resultados de temporada regular."""
    df = nfl.load_schedules([season]).filter(pl.col("game_type") == "REG")
    return df.to_pandas()


@st.cache_data(show_spinner="Cargando jugada a jugada...", ttl=3600)
def load_pbp(season):
    """Play-by-play de temporada regular, con solo las columnas que usa la app."""
    df = nfl.load_pbp([season]).filter(pl.col("season_type") == "REG")
    cols = [c for c in PBP_COLS if c in df.columns]
    return df.select(cols).to_pandas()


@st.cache_data(show_spinner=False, ttl=3600)
def load_ngs(stat_type, season):
    """Next Gen Stats semanales por jugador. stat_type: 'passing' | 'rushing' | 'receiving'.

    week==0 son las filas de resumen de temporada completa que añade nflverse:
    las quitamos aqui para que quien consuma esto solo vea semanas reales y no
    corra el riesgo de duplicar el total al agregar.
    """
    df = nfl.load_nextgen_stats(stat_type=stat_type, seasons=[season])
    df = df.filter((pl.col("season_type") == "REG") & (pl.col("week") > 0))
    return df.to_pandas()


@st.cache_data(show_spinner=False, ttl=3600)
def load_pfr(stat_type, season):
    """Stats avanzadas de Pro Football Reference (presion, blitz...). stat_type: 'pass' | 'def'."""
    try:
        df = nfl.load_pfr_advstats(seasons=[season], stat_type=stat_type)
        return df.to_pandas()
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def load_ftn(season):
    """Charting jugada a jugada (play action, RPO, blitz, box count...)."""
    try:
        df = nfl.load_ftn_charting(seasons=[season])
        return df.to_pandas()
    except Exception:
        return None


NEWS_FEED = "https://www.espn.com/espn/rss/nfl/news"


@st.cache_data(ttl=1800, show_spinner=False)
def get_news(url=NEWS_FEED, n=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            root = ET.fromstring(r.read())
        items = []
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "#").strip()
            if title:
                items.append((title, link))
            if len(items) >= n:
                break
        return items
    except Exception:
        return []
