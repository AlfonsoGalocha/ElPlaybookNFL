#!/usr/bin/env python3
"""
panel_nfl.py — EL PLAYBOOK NFL · panel interactivo
  - Cabecera tipo revista deportiva: navbar + carrusel de noticias
  - Equipos: selector + stats del equipo + plantilla
  - Clasificacion: general y por conferencia/division
  - Rankings tipo leaderboard (foto, medallas, barras de equipo)
  - Comparador de jugadores (tabla + barras + radar)
  - Jugadores: buscador + estrellas destacadas + ficha con tarjeta descargable
  - Pie de pagina con el contacto del canal

Lanzar:  streamlit run panel_nfl.py
"""

import base64
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import polars as pl
import plotly.graph_objects as go
import streamlit as st
import nflreadpy as nfl
from matplotlib.colors import to_hex

import nfl_graficos as G

BG, CARD, FG, MUTED, ACCENT, ACCENT2 = G.BG, G.CARD, G.FG, G.MUTED, G.ACCENT, G.ACCENT2

# --- CONTACTO DEL CANAL (cambia por tus enlaces reales) --------------------
REDES = {
    "TikTok":    "https://www.tiktok.com/@elplaybooknfl",
    "Instagram": "https://www.instagram.com/elplaybooknfl",
    "YouTube":   "https://www.youtube.com/@elplaybooknfl",
    "Contacto":  "mailto:elplaybooknfl@gmail.com",
}

# Estrellas para accesos rapidos (se filtran a las que existan en la temporada)
FAMOSOS = ["Patrick Mahomes", "Josh Allen", "Lamar Jackson", "Jalen Hurts",
           "Joe Burrow", "Ja'Marr Chase", "Justin Jefferson",
           "Christian McCaffrey", "Saquon Barkley", "Travis Kelce"]

NEWS_FEED = "https://www.espn.com/espn/rss/nfl/news"

METRICS = {
    "Yardas de pase": "passing_yards", "TD de pase": "passing_tds",
    "Intercepciones": "passing_interceptions", "Yardas por tierra": "rushing_yards",
    "TD por tierra": "rushing_tds", "Recepciones": "receptions",
    "Yardas de recepcion": "receiving_yards", "TD de recepcion": "receiving_tds",
    "TD totales": "total_tds",
}
RADAR_AXES = {"Pase (yds)": "passing_yards", "Carrera (yds)": "rushing_yards",
              "Recepcion (yds)": "receiving_yards", "TD totales": "total_tds",
              "1os downs": "first_downs_total"}

PAGES = [
    ("equipos", "🏟️ Equipos"),
    ("clasificacion", "📋 Clasificación"),
    ("rankings", "🏆 Rankings"),
    ("comparar", "📊 Comparar"),
    ("jugadores", "👤 Jugadores"),
]

HERO_GRADIENTS = [
    f"linear-gradient(135deg,{ACCENT}dd,#1a0a12 70%)",
    f"linear-gradient(135deg,{ACCENT2}dd,#08131f 70%)",
    "linear-gradient(135deg,#7a1130dd,#0B0E14 70%)",
    "linear-gradient(135deg,#0e5f9add,#0B0E14 70%)",
    "linear-gradient(135deg,#3a0d1add,#0B0E14 70%)",
]

FALLBACK_NEWS = [
    ("Bienvenido a El Playbook NFL", "#"),
    ("Rankings, clasificación y equipos en un solo lugar", "#"),
    ("Sigue a tus jugadores favoritos jornada a jornada", "#"),
    ("Compara stats y genera tu propia tarjeta descargable", "#"),
    ("Datos oficiales de nflverse, actualizados cada semana", "#"),
]

LOGO_PATH = "logo.png"
LOGO_B64 = base64.b64encode(open(LOGO_PATH, "rb").read()).decode()

st.set_page_config(page_title="El Playbook NFL", page_icon=LOGO_PATH, layout="wide")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}
.stApp {{ background: radial-gradient(1200px 560px at 12% -12%, #2a1420 0%, #0B0E14 45%),
                       radial-gradient(1000px 480px at 100% 0%, #0e2438 0%, #0B0E14 55%); color:#E9EDF5; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding-top:1rem; padding-bottom:0; max-width:1360px; }}
h1,h2,h3 {{ font-family:'Oswald', sans-serif; letter-spacing:.5px; color:#fff; }}

@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
.fade-up {{ animation:fadeUp .5s ease both; }}
.d0{{animation-delay:.02s}} .d1{{animation-delay:.06s}} .d2{{animation-delay:.10s}} .d3{{animation-delay:.14s}}
.d4{{animation-delay:.18s}} .d5{{animation-delay:.22s}} .d6{{animation-delay:.26s}} .d7{{animation-delay:.30s}}
.d8{{animation-delay:.34s}} .d9{{animation-delay:.38s}}

/* --- Navbar --- */
.navbar {{ display:flex; align-items:center; gap:14px; padding:.3rem 0 .6rem; }}
.nav-brand {{ font-family:'Oswald'; font-weight:700; font-size:1.22rem; letter-spacing:.5px; color:#fff; display:flex; align-items:center; gap:.4rem; white-space:nowrap; overflow:hidden; }}
.nav-brand img {{ height:32px; width:32px; min-width:32px; border-radius:50%; object-fit:cover; box-shadow:0 0 0 2px rgba(255,255,255,.18); }}
.nav-brand .nfl {{ background:linear-gradient(135deg,{ACCENT},{ACCENT2}); color:#fff; padding:.02rem .4rem; border-radius:6px; font-size:.95rem; }}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {{
    border-radius:999px !important; font-family:'Oswald'; font-size:.8rem; letter-spacing:.2px;
    padding:.4rem .5rem !important; white-space:nowrap; border:1px solid rgba(255,255,255,.10) !important;
    background:rgba(255,255,255,.03) !important; color:#C9D2DE !important; transition:all .18s ease;
}}
div[data-testid="stButton"] button:hover {{ border-color:{ACCENT} !important; color:#fff !important; transform:translateY(-1px); }}
div[data-testid="stButton"] button[kind="primary"] {{
    background:linear-gradient(135deg,{ACCENT},#a4142c) !important; border-color:transparent !important;
    color:#fff !important; box-shadow:0 4px 16px rgba(228,32,60,.35);
}}

/* --- Hero carousel --- */
.hero-carousel {{ position:relative; height:230px; border-radius:20px; overflow:hidden; margin:.2rem 0 1.4rem;
    border:1px solid rgba(255,255,255,.08); }}
.hc-slide {{ position:absolute; inset:0; display:flex; flex-direction:column; justify-content:flex-end;
    padding:22px 28px; text-decoration:none; opacity:0; animation:hcFade 25s infinite ease-in-out; }}
@keyframes hcFade {{ 0%{{opacity:1}} 16%{{opacity:1}} 20%{{opacity:0}} 96%{{opacity:0}} 100%{{opacity:0}} }}
.hc-tag {{ font-family:'Oswald'; font-size:.72rem; font-weight:700; letter-spacing:2px; color:#fff;
    background:rgba(0,0,0,.35); display:inline-block; padding:3px 10px; border-radius:20px; margin-bottom:10px;
    width:fit-content; }}
.hc-title {{ font-family:'Bebas Neue'; font-size:2.1rem; line-height:1.05; color:#fff; max-width:78%;
    text-shadow:0 2px 12px rgba(0,0,0,.5); }}
.hc-cta {{ color:#fff; opacity:.85; font-size:.82rem; font-weight:600; margin-top:8px; }}
.hc-dots {{ position:absolute; bottom:14px; right:20px; display:flex; gap:6px; }}
.hc-dot {{ width:22px; height:4px; border-radius:3px; background:rgba(255,255,255,.25); animation:hcDot 25s infinite; }}
@keyframes hcDot {{ 0%{{background:#fff}} 16%{{background:#fff}} 20%{{background:rgba(255,255,255,.25)}} 100%{{background:rgba(255,255,255,.25)}} }}

/* --- Titulos de seccion --- */
.sect-title {{ font-family:'Bebas Neue'; font-size:2.1rem; letter-spacing:1px; color:#fff; margin:.1rem 0 .2rem;
    position:relative; display:inline-block; }}
.sect-title::after {{ content:""; display:block; height:4px; width:64px; margin-top:4px; border-radius:3px;
    background:linear-gradient(90deg,{ACCENT},{ACCENT2}); }}
.sect-sub {{ color:#8A93A6; font-size:.92rem; margin:.3rem 0 1.1rem; }}

/* --- Cards genericas --- */
.lb-row, .std-row, .news-card {{ background:#131A26; border:1px solid rgba(255,255,255,.05); border-radius:14px;
    transition:transform .15s, border-color .15s; }}
.lb-row {{ display:flex; align-items:center; gap:14px; padding:10px 16px; margin-bottom:10px; }}
.lb-row:hover {{ transform:translateX(4px); border-color:rgba(228,32,60,.5); }}
.lb-rank {{ font-family:'Oswald'; font-weight:700; font-size:1.45rem; width:36px; text-align:center; color:#8A93A6; }}
.rank-1 {{ color:#FFD54A; }} .rank-2 {{ color:#C9D2DE; }} .rank-3 {{ color:#E0925B; }}
.lb-photo {{ width:52px; height:52px; border-radius:50%; object-fit:cover; background:#222C3D; border:2px solid rgba(255,255,255,.15); }}
.lb-info {{ flex:1; min-width:0; }}
.lb-name {{ font-family:'Oswald'; font-weight:600; font-size:1.15rem; color:#fff; line-height:1.15; }}
.lb-meta {{ color:#8A93A6; font-size:.78rem; margin-bottom:6px; }}
.lb-track {{ height:8px; background:rgba(255,255,255,.06); border-radius:6px; overflow:hidden; }}
.lb-fill {{ height:100%; border-radius:6px; }}
.lb-value {{ font-family:'Oswald'; font-weight:700; font-size:1.5rem; color:#fff; text-align:right; white-space:nowrap; }}
.lb-value span {{ font-size:.72rem; color:#8A93A6; font-weight:500; margin-left:3px; }}
.prof-hd {{ display:flex; align-items:center; gap:16px; margin:.4rem 0 1rem; }}
.prof-hd img {{ width:84px; height:84px; border-radius:50%; object-fit:cover; background:#222C3D; border:3px solid rgba(255,255,255,.15); }}
.prof-name {{ font-family:'Oswald'; font-size:2rem; color:#fff; line-height:1; }}
.prof-meta {{ color:{ACCENT}; font-weight:600; font-size:.95rem; }}

/* --- Equipos --- */
.conf-h {{ font-family:'Oswald'; font-weight:700; font-size:1.05rem; letter-spacing:1px; color:{ACCENT2}; margin:1rem 0 .5rem; }}
.team-pick img {{ width:40px; height:40px; object-fit:contain; display:block; margin:0 auto 4px; }}
.team-hd {{ display:flex; align-items:center; gap:18px; margin:1rem 0 1.1rem; padding:18px 22px; border-radius:16px;
    border:1px solid rgba(255,255,255,.08); }}
.team-hd img {{ width:76px; height:76px; object-fit:contain; }}
.team-hd .tname {{ font-family:'Bebas Neue'; font-size:2.3rem; color:#fff; line-height:1; letter-spacing:1px; }}
.team-hd .tmeta {{ color:rgba(255,255,255,.85); font-weight:600; font-size:.95rem; margin-top:3px; }}

/* --- Clasificacion --- */
.div-h {{ font-family:'Oswald'; font-weight:700; font-size:.9rem; letter-spacing:1px; color:#8A93A6; text-transform:uppercase;
    margin:0 0 .5rem; padding-left:.5rem; border-left:3px solid {ACCENT2}; }}
.std-row {{ display:flex; align-items:center; gap:12px; padding:8px 14px; margin-bottom:6px; }}
.std-row:hover {{ border-color:rgba(31,163,232,.5); }}
.std-rank {{ width:22px; color:#8A93A6; font-weight:700; font-family:'Oswald'; }}
.std-logo {{ width:28px; height:28px; object-fit:contain; }}
.std-team {{ flex:1; min-width:0; font-weight:600; color:#fff; font-size:.92rem; }}
.std-team small {{ color:#8A93A6; font-weight:500; }}
.std-stat {{ width:50px; text-align:center; font-family:'Oswald'; font-weight:600; color:#E9EDF5; font-size:.92rem; }}
.std-head {{ display:flex; align-items:center; gap:12px; padding:0 14px; margin-bottom:4px; color:#8A93A6; font-size:.68rem; letter-spacing:.5px; text-transform:uppercase; }}
.std-head .std-rank {{ width:22px; }} .std-head .std-logo {{ width:28px; }} .std-head .std-team {{ flex:1; }}
.std-head .std-stat {{ width:50px; text-align:center; }}
.div-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0 26px; }}
@media (max-width:900px) {{ .div-grid {{ grid-template-columns:1fr; }} }}
.div-block {{ margin-bottom:1.2rem; }}

/* --- Footer --- */
.site-footer {{ margin-top:3rem; padding:2rem 0 1.4rem; border-top:1px solid rgba(255,255,255,.08); text-align:center; }}
.footer-brand {{ display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:.9rem; }}
.footer-brand img {{ width:34px; height:34px; border-radius:50%; object-fit:cover; }}
.footer-brand span {{ font-family:'Oswald'; font-weight:700; font-size:1.05rem; color:#fff; letter-spacing:.5px; }}
.footer-links {{ display:flex; justify-content:center; gap:22px; flex-wrap:wrap; margin-bottom:1rem; }}
.footer-links a {{ color:#C9D2DE; text-decoration:none; font-size:.88rem; font-weight:600; transition:color .15s; }}
.footer-links a:hover {{ color:{ACCENT}; }}
.footer-meta {{ color:#5C6579; font-size:.78rem; }}

/* --- Widgets nativos: look de pill --- */
div[data-baseweb="select"] > div {{ border-radius:10px !important; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Cargando datos de la NFL...")
def load_season(season):
    df = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    return df.to_pandas()


@st.cache_resource
def load_teams():
    return nfl.load_teams()


@st.cache_data(show_spinner=False)
def load_schedules(season):
    df = nfl.load_schedules([season]).filter(pl.col("game_type") == "REG")
    return df.to_pandas()


@st.cache_data(ttl=1800, show_spinner=False)
def get_news(url, n=6):
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


def _mode(s):
    m = s.mode()
    return m.iloc[0] if len(m) else ""


def headshot_of(pdf, name):
    s = pdf[pdf.player_display_name == name]["headshot_url"].dropna()
    return s.iloc[0] if s.size else ""


def player_season(pdf, name):
    p = pdf[pdf.player_display_name == name]
    pos = _mode(p["position"])
    return {
        "pos": pos, "team": _mode(p["team"]),
        "headshot": headshot_of(pdf, name),
        "tiles": G._tiles(pos, G.player_totals(p)),
    }


def team_meta_table(teams_df, colors):
    out = {}
    for r in teams_df.iter_rows(named=True):
        out[r["team_abbr"]] = {
            "name": r["team_name"], "conf": r["team_conf"], "div": r["team_division"],
            "logo": r["team_logo_espn"], "color": colors.get(r["team_abbr"], ACCENT),
        }
    return out


def team_stat_tiles(std_row, s):
    yards_total = s["passing_yards"] + s["rushing_yards"]
    return [
        ("RECORD", f"{int(std_row['W'])}-{int(std_row['L'])}-{int(std_row['T'])}"),
        ("PTS A FAVOR", f"{std_row['PF']:,.0f}".replace(",", ".")),
        ("PTS EN CONTRA", f"{std_row['PA']:,.0f}".replace(",", ".")),
        ("YARDAS TOTALES", f"{yards_total:,.0f}".replace(",", ".")),
        ("SACKS", f"{s['def_sacks']:.1f}"),
        ("INTERCEP.", f"{s['def_interceptions']:,.0f}"),
    ]


def standings_table(sched, meta):
    rows = {a: {"W": 0, "L": 0, "T": 0, "PF": 0, "PA": 0} for a in meta}
    for g in sched.itertuples():
        h, a = g.home_team, g.away_team
        hs, as_ = g.home_score, g.away_score
        if h not in rows or a not in rows or np.isnan(hs) or np.isnan(as_):
            continue
        rows[h]["PF"] += hs; rows[h]["PA"] += as_
        rows[a]["PF"] += as_; rows[a]["PA"] += hs
        if hs > as_:
            rows[h]["W"] += 1; rows[a]["L"] += 1
        elif hs < as_:
            rows[a]["W"] += 1; rows[h]["L"] += 1
        else:
            rows[h]["T"] += 1; rows[a]["T"] += 1
    out = []
    for a, r in rows.items():
        gp = r["W"] + r["L"] + r["T"]
        pct = (r["W"] + 0.5 * r["T"]) / gp if gp else 0.0
        out.append({"team": a, **r, "PCT": pct, "DIFF": int(r["PF"] - r["PA"]),
                    "conf": meta[a]["conf"], "division": meta[a]["div"]})
    return pd.DataFrame(out).sort_values("PCT", ascending=False).reset_index(drop=True)


def totals_table(pdf, week_range=None):
    d = pdf
    if week_range is not None:
        d = d[(d["week"] >= week_range[0]) & (d["week"] <= week_range[1])]
    g = d.groupby("player_display_name").agg(
        position=("position", _mode), team=("team", _mode),
        passing_yards=("passing_yards", "sum"), passing_tds=("passing_tds", "sum"),
        passing_interceptions=("passing_interceptions", "sum"),
        rushing_yards=("rushing_yards", "sum"), rushing_tds=("rushing_tds", "sum"),
        receptions=("receptions", "sum"), receiving_yards=("receiving_yards", "sum"),
        receiving_tds=("receiving_tds", "sum"),
        pfd=("passing_first_downs", "sum"), rfd=("rushing_first_downs", "sum"),
        recfd=("receiving_first_downs", "sum"),
    ).reset_index()
    g["total_tds"] = g.passing_tds + g.rushing_tds + g.receiving_tds
    g["first_downs_total"] = g.pfd + g.rfd + g.recfd
    return g


def leaderboard_data(pdf, colors, stat_col, week, n):
    d = pdf if week is None else pdf[pdf["week"] == week]
    g = d.groupby("player_display_name").agg(
        value=(stat_col, "sum"), team=("team", _mode), pos=("position", _mode),
        headshot=("headshot_url", lambda s: s.dropna().iloc[0] if s.dropna().size else ""),
    ).reset_index()
    g = g[g["value"] > 0].sort_values("value", ascending=False).head(n)
    return [dict(name=r.player_display_name, team=r.team, pos=r.pos, value=r.value,
                 headshot=r.headshot, color=colors.get(r.team, ACCENT))
            for _, r in g.iterrows()]


def leaderboard_html(rows, stat_key):
    _, _, suffix, dec = G.STATS[stat_key]
    maxv = max((r["value"] for r in rows), default=1) or 1
    medal = {0: "rank-1", 1: "rank-2", 2: "rank-3"}
    out = []
    for i, r in enumerate(rows):
        pct = max(6, r["value"] / maxv * 100)
        val = f"{r['value']:,.{dec}f}".replace(",", ".")
        dcls = f"fade-up d{min(i, 9)}"
        out.append(
            f'<div class="lb-row {dcls}"><div class="lb-rank {medal.get(i, "")}">{i+1}</div>'
            f'<img class="lb-photo" src="{r["headshot"]}" />'
            f'<div class="lb-info"><div class="lb-name">{r["name"]}</div>'
            f'<div class="lb-meta">{r["pos"]} · {r["team"]}</div>'
            f'<div class="lb-track"><div class="lb-fill" '
            f'style="width:{pct:.0f}%;background:{r["color"]}"></div></div></div>'
            f'<div class="lb-value">{val}<span>{suffix}</span></div></div>'
        )
    return "".join(out)


def hero_html(items):
    src = list(items or FALLBACK_NEWS)[:5]
    if not src:
        src = FALLBACK_NEWS
    while len(src) < 5:
        src = src + src
    src = src[:5]
    slides = []
    for i, (title, link) in enumerate(src):
        slides.append(
            f'<a class="hc-slide" href="{link}" target="_blank" rel="noopener" '
            f'style="animation-delay:-{i * 5}s; background:{HERO_GRADIENTS[i % len(HERO_GRADIENTS)]}">'
            f'<div class="hc-tag">🏈 NFL · ÚLTIMA HORA</div>'
            f'<div class="hc-title">{title}</div>'
            f'<div class="hc-cta">Leer más →</div></a>'
        )
    dots = "".join(f'<span class="hc-dot" style="animation-delay:-{i * 5}s"></span>' for i in range(5))
    return f'<div class="hero-carousel">{"".join(slides)}<div class="hc-dots">{dots}</div></div>'


def section_title(text, sub=None):
    st.markdown(f'<div class="sect-title">{text}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sect-sub">{sub}</div>', unsafe_allow_html=True)


def render_footer():
    links = "".join(f'<a href="{u}" target="_blank">{n}</a>' for n, u in REDES.items())
    st.markdown(f"""
    <div class="site-footer">
      <div class="footer-brand"><img src="data:image/png;base64,{LOGO_B64}"/><span>EL PLAYBOOK NFL</span></div>
      <div class="footer-links">{links}</div>
      <div class="footer-meta">{G.CANAL} · Datos: nflverse · Hecho con Streamlit</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Navbar (marca + navegacion + temporada) — sustituye a la barra lateral
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "equipos"

nav_l, nav_c, nav_r = st.columns([2.0, 5.9, 1.0], vertical_alignment="center")
with nav_l:
    st.markdown(
        f'<div class="nav-brand"><img src="data:image/png;base64,{LOGO_B64}"/>'
        f'EL PLAYBOOK <span class="nfl">NFL</span></div>', unsafe_allow_html=True)
with nav_c:
    ncols = st.columns(len(PAGES))
    for col, (key, label) in zip(ncols, PAGES):
        with col:
            active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()
with nav_r:
    season = st.selectbox("Temporada", list(range(2026, 1998, -1)), index=0,
                          label_visibility="collapsed")

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

st.markdown(hero_html(get_news(NEWS_FEED)), unsafe_allow_html=True)

page = st.session_state.page

# ---------------------------------------------------------------------------
# PAGINA — Equipos (picker + stats del equipo + plantilla)
# ---------------------------------------------------------------------------
if page == "equipos":
    section_title("Equipos", "Elige un equipo para ver su récord, sus stats y su plantilla completa.")

    if ("sel_team" not in st.session_state
            or st.session_state.sel_team not in all_teams):
        st.session_state.sel_team = "BUF" if "BUF" in all_teams else all_teams[0]

    for conf in ["AFC", "NFC"]:
        st.markdown(f'<div class="conf-h">{conf}</div>', unsafe_allow_html=True)
        conf_teams = sorted(a for a in all_teams if team_meta[a]["conf"] == conf)
        cols = st.columns(8)
        for i, abbr in enumerate(conf_teams):
            with cols[i % 8]:
                meta = team_meta[abbr]
                st.markdown(f"<div class='team-pick'><img src='{meta['logo']}'></div>",
                            unsafe_allow_html=True)
                active = st.session_state.sel_team == abbr
                if st.button(abbr, key=f"team_{abbr}", use_container_width=True,
                             type="primary" if active else "secondary"):
                    st.session_state.sel_team = abbr
                    st.rerun()

    st.markdown("---")
    team = st.session_state.sel_team
    meta = team_meta[team]
    std_rows = standings[standings.team == team]
    st.markdown(f"""
      <div class="team-hd fade-up" style="background:linear-gradient(120deg,{meta['color']}33,transparent)">
        <img src="{meta['logo']}"/>
        <div><div class="tname">{meta['name'].upper()}</div>
        <div class="tmeta">{meta['conf']} · {meta['div']} · Temporada {season}</div></div>
      </div>""", unsafe_allow_html=True)

    if len(std_rows):
        s = G.player_totals(pdf[pdf.team == team])
        tiles = team_stat_tiles(std_rows.iloc[0], s)
        m = st.columns(len(tiles))
        for col, (label, value) in zip(m, tiles):
            col.metric(label, value)

    st.markdown("#### Plantilla")
    roster = totals_table(pdf[pdf.team == team])
    if roster.empty:
        st.info("No hay jugadores con estadisticas para este equipo en esta temporada.")
    else:
        roster["yds_total"] = roster.passing_yards + roster.rushing_yards + roster.receiving_yards
        roster["td_total"] = roster.passing_tds + roster.rushing_tds + roster.receiving_tds
        roster = roster.sort_values(["yds_total", "td_total"], ascending=False)
        show_r = {"player_display_name": "Jugador", "position": "Pos",
                  "passing_yards": "Yds pase", "passing_tds": "TD pase",
                  "rushing_yards": "Yds tierra", "rushing_tds": "TD tierra",
                  "receptions": "Recep.", "receiving_yards": "Yds recep.",
                  "receiving_tds": "TD recep.", "td_total": "TD tot."}
        st.dataframe(roster[list(show_r)].rename(columns=show_r).set_index("Jugador"),
                     use_container_width=True, height=420)

# ---------------------------------------------------------------------------
# PAGINA — Clasificacion (general y por conferencia/division)
# ---------------------------------------------------------------------------
elif page == "clasificacion":
    section_title("Clasificación", "Récord de la temporada regular, calculado a partir de los resultados oficiales.")
    vista = st.radio("Vista", ["General", "Por conferencia"], horizontal=True,
                      key="std_scope", label_visibility="collapsed")

    def _std_block_html(df, stats):
        labels = {"PJ": "PJ", "V": "V", "D": "D", "E": "E", "PCT": "%",
                  "PF": "PF", "PC": "PC", "DIF": "DIF"}
        head_stats = "".join(f'<div class="std-stat">{labels[s]}</div>' for s in stats)
        head = (f'<div class="std-head"><div class="std-rank">#</div><div class="std-logo"></div>'
                f'<div class="std-team">Equipo</div>{head_stats}</div>')
        rows = []
        for i, r in enumerate(df.itertuples(), 1):
            meta = team_meta[r.team]
            gp = r.W + r.L + r.T
            vals = {"PJ": gp, "V": r.W, "D": r.L, "E": r.T, "PCT": f"{r.PCT:.3f}",
                    "PF": f"{r.PF:.0f}", "PC": f"{r.PA:.0f}", "DIF": f"{r.DIFF:+d}"}
            stat_html = "".join(f'<div class="std-stat">{vals[s]}</div>' for s in stats)
            rows.append(
                f'<div class="std-row fade-up d{min(i - 1, 9)}"><div class="std-rank">{i}</div>'
                f'<img class="std-logo" src="{meta["logo"]}"/>'
                f'<div class="std-team">{meta["name"]} <small>{r.team}</small></div>{stat_html}</div>'
            )
        return head + "".join(rows)

    if vista == "General":
        st.markdown(_std_block_html(standings, ["PJ", "V", "D", "E", "PCT", "PF", "PC", "DIF"]),
                    unsafe_allow_html=True)
    else:
        for conf in ["AFC", "NFC"]:
            st.markdown(f'<div class="conf-h">{conf}</div>', unsafe_allow_html=True)
            cdf = standings[standings.conf == conf]
            divs = sorted(cdf["division"].unique())
            blocks = []
            for div in divs:
                ddf = cdf[cdf["division"] == div].sort_values("PCT", ascending=False)
                blocks.append(
                    f'<div class="div-block"><div class="div-h">{div}</div>'
                    f'{_std_block_html(ddf, ["V", "D", "E", "DIF"])}</div>'
                )
            st.markdown(f'<div class="div-grid">{"".join(blocks)}</div>', unsafe_allow_html=True)
    st.caption("PJ partidos jugados · % porcentaje de victorias · PF/PC puntos a favor/en contra · DIF diferencia de puntos.")

# ---------------------------------------------------------------------------
# PAGINA — Rankings
# ---------------------------------------------------------------------------
elif page == "rankings":
    section_title("Rankings", "Los lideres de la temporada, jornada a jornada o acumulados.")
    c1, c2, c3 = st.columns([2, 2, 1])
    stat_label = c1.selectbox("Metrica", [v[1] for v in G.STATS.values()], index=0)
    stat_key = [k for k, v in G.STATS.items() if v[1] == stat_label][0]
    ambito = c2.selectbox("Ambito", ["Temporada completa"] + [f"Jornada {w}" for w in weeks])
    top_n = c3.slider("Top", 5, 15, 10)
    week = None if ambito == "Temporada completa" else int(ambito.split()[1])
    rows = leaderboard_data(pdf, colors, G.STATS[stat_key][0], week, top_n)
    sub = "Temporada completa" if week is None else f"Jornada {week}"
    st.markdown(f"<h3 style='margin:.6rem 0 1rem'>{stat_label} · {sub}</h3>", unsafe_allow_html=True)
    st.markdown(leaderboard_html(rows, stat_key), unsafe_allow_html=True)
    with st.expander("⬇️ Descargar como imagen vertical (para subir)"):
        if st.button("Generar PNG del ranking", type="primary"):
            with st.spinner("Generando..."):
                fig = G.make_ranking(pdf, season, week, stat_key, top_n, teams)
                png = G.fig_a_png(fig)
            st.image(png, width=320)
            fn = f"ranking_{stat_key}_{season}" + (f"_j{week}" if week else "") + ".png"
            st.download_button("Descargar PNG", png, file_name=fn, mime="image/png")

# ---------------------------------------------------------------------------
# PAGINA — Comparador
# ---------------------------------------------------------------------------
elif page == "comparar":
    section_title("Comparador", "Enfrenta a dos o mas jugadores cara a cara.")
    scope = st.radio("Ambito", ["Temporada completa", "Rango de jornadas"],
                     horizontal=True, key="cmp_scope")
    wr = None
    if scope == "Rango de jornadas" and len(weeks) > 1:
        wr = st.slider("Jornadas", min(weeks), max(weeks), (min(weeks), max(weeks)))
    totals = totals_table(pdf, wr)
    active = totals[(totals.passing_yards + totals.rushing_yards
                     + totals.receiving_yards) > 0]
    cnames = sorted(active.player_display_name.tolist())
    default = [n for n in ["Josh Allen", "Lamar Jackson", "Jalen Hurts"]
               if n in cnames][:2]
    picked = st.multiselect("🔍 Busca y elige jugadores a comparar", cnames, default=default)
    metric_label = st.selectbox("Metrica del grafico de barras",
                                list(METRICS.keys()), index=0)
    if not picked:
        st.info("Elige al menos un jugador para empezar.")
    else:
        sel = totals[totals.player_display_name.isin(picked)].copy()
        show = {"player_display_name": "Jugador", "position": "Pos", "team": "Equipo",
                "passing_yards": "Yds pase", "passing_tds": "TD pase",
                "passing_interceptions": "INT", "rushing_yards": "Yds tierra",
                "rushing_tds": "TD tierra", "receptions": "Recep.",
                "receiving_yards": "Yds recep.", "total_tds": "TD tot."}
        st.dataframe(sel[list(show)].rename(columns=show).set_index("Jugador"),
                     use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<h3>{metric_label}</h3>", unsafe_allow_html=True)
            mcol = METRICS[metric_label]
            b = sel.sort_values(mcol)
            fig = go.Figure(go.Bar(
                x=b[mcol], y=b.player_display_name, orientation="h",
                marker_color=[colors.get(t, ACCENT) for t in b.team],
                text=b[mcol], textposition="outside"))
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", height=90 + 70 * len(b),
                margin=dict(l=10, r=30, t=10, b=10), font=dict(color=FG), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<h3>Perfil comparado (radar)</h3>", unsafe_allow_html=True)
            lbls, acols = list(RADAR_AXES), list(RADAR_AXES.values())
            mx = {c: max(sel[c].max(), 1) for c in acols}
            radar = go.Figure()
            for _, row in sel.iterrows():
                vv = [row[c] / mx[c] for c in acols]
                radar.add_trace(go.Scatterpolar(
                    r=vv + [vv[0]], theta=lbls + [lbls[0]], fill="toself",
                    name=row.player_display_name, line_color=colors.get(row.team, ACCENT)))
            radar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                polar=dict(bgcolor=CARD, radialaxis=dict(visible=True, range=[0, 1],
                    showticklabels=False)), height=430,
                margin=dict(l=30, r=30, t=30, b=30), font=dict(color=FG),
                legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(radar, use_container_width=True)
        st.caption("El radar normaliza cada eje respecto al mejor de los elegidos.")

# ---------------------------------------------------------------------------
# PAGINA — Jugadores (buscador + estrellas + ficha con tarjeta)
# ---------------------------------------------------------------------------
elif page == "jugadores":
    section_title("Jugadores", "Busca cualquier jugador y genera su tarjeta.")

    if ("sel_player" not in st.session_state
            or st.session_state.sel_player not in all_names):
        st.session_state.sel_player = ("Josh Allen" if "Josh Allen" in all_names
                                       else all_names[0])

    def _pick(name):
        st.session_state.sel_player = name

    st.selectbox("🔍 Busca cualquier jugador", all_names, key="sel_player")

    famosos = [n for n in FAMOSOS if n in all_names][:6]
    if famosos:
        st.markdown("<div class='conf-h'>⭐ Destacados</div>", unsafe_allow_html=True)
        cols = st.columns(len(famosos))
        for col, name in zip(cols, famosos):
            with col:
                hs = headshot_of(pdf, name)
                if hs:
                    st.markdown(f"<div style='text-align:center'><img src='{hs}' "
                                f"style='width:70px;height:70px;border-radius:50%;"
                                f"object-fit:cover;border:2px solid rgba(255,255,255,.15)'></div>",
                                unsafe_allow_html=True)
                st.button(name, key=f"fam_{name}", on_click=_pick, args=(name,),
                          use_container_width=True)

    st.markdown("---")
    player = st.session_state.sel_player
    info = player_season(pdf, player)
    st.markdown(f"""
      <div class="prof-hd fade-up">
        <img src="{info['headshot']}"/>
        <div><div class="prof-name">{player.upper()}</div>
        <div class="prof-meta">{info['pos']} · {info['team']} · Temporada {season}</div></div>
      </div>""", unsafe_allow_html=True)

    tiles = info["tiles"]
    m = st.columns(len(tiles))
    for col, (label, value) in zip(m, tiles):
        col.metric(label, value)

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
            fig = G.make_card(pdf, season, player, teams, modo_key, foto)
            png = G.fig_a_png(fig)
        st.image(png, width=340)
        fn = f"tarjeta_{player.lower().replace(' ', '_')}_{season}.png"
        st.download_button("⬇️ Descargar PNG", png, file_name=fn, mime="image/png")

render_footer()
