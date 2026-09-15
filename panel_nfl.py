#!/usr/bin/env python3
"""
panel_nfl.py — EL PLAYBOOK NFL · panel interactivo
  - Rankings tipo leaderboard (foto, medallas, barras de equipo) + noticias
  - Comparador de jugadores (tabla + barras + radar)
  - Jugadores: buscador + estrellas destacadas + ficha con tarjeta descargable
  - Contacto del canal en la barra lateral

Lanzar:  streamlit run panel_nfl.py
"""

import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
import polars as pl
import plotly.graph_objects as go
import streamlit as st
import nflreadpy as nfl
from matplotlib.colors import to_hex

import nfl_graficos as G

BG, CARD, FG, MUTED, ACCENT = G.BG, G.CARD, G.FG, G.MUTED, G.ACCENT

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

st.set_page_config(page_title="El Playbook NFL", page_icon="🏈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Inter', sans-serif; }
.stApp { background: radial-gradient(1100px 500px at 15% -10%, #14243f 0%, #0B0E14 55%); color:#E9EDF5; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:1.1rem; max-width:1320px; }
h1,h2,h3 { font-family:'Oswald', sans-serif; letter-spacing:.5px; color:#fff; }
.hero { display:flex; align-items:center; justify-content:space-between; padding-bottom:.6rem; margin-bottom:.3rem; border-bottom:1px solid rgba(255,255,255,.07); }
.brand { font-family:'Oswald'; font-weight:700; font-size:2rem; letter-spacing:1px; color:#fff; display:flex; align-items:center; gap:.55rem; }
.brand .nfl { background:linear-gradient(135deg,#00E5A0,#12B8FF); color:#0B0E14; padding:.02rem .5rem; border-radius:9px; }
.brand .ball { font-size:1.7rem; }
.tagline { color:#8A93A6; font-size:.9rem; text-align:right; }
.stTabs [data-baseweb="tab-list"] { gap:.2rem; border-bottom:1px solid rgba(255,255,255,.08); }
.stTabs [data-baseweb="tab"] { font-family:'Oswald'; font-size:1.05rem; letter-spacing:.5px; }
.stTabs [aria-selected="true"] { color:#00E5A0 !important; }
section[data-testid="stSidebar"] { background:#0E1420; border-right:1px solid rgba(255,255,255,.06); }
.lb-row { display:flex; align-items:center; gap:14px; background:#131A26; border:1px solid rgba(255,255,255,.05); border-radius:14px; padding:10px 16px; margin-bottom:10px; transition:transform .15s, border-color .15s; }
.lb-row:hover { transform:translateX(4px); border-color:rgba(0,229,160,.45); }
.lb-rank { font-family:'Oswald'; font-weight:700; font-size:1.45rem; width:36px; text-align:center; color:#8A93A6; }
.rank-1 { color:#FFD54A; } .rank-2 { color:#C9D2DE; } .rank-3 { color:#E0925B; }
.lb-photo { width:52px; height:52px; border-radius:50%; object-fit:cover; background:#222C3D; border:2px solid rgba(255,255,255,.15); }
.lb-info { flex:1; min-width:0; }
.lb-name { font-family:'Oswald'; font-weight:600; font-size:1.15rem; color:#fff; line-height:1.15; }
.lb-meta { color:#8A93A6; font-size:.78rem; margin-bottom:6px; }
.lb-track { height:8px; background:rgba(255,255,255,.06); border-radius:6px; overflow:hidden; }
.lb-fill { height:100%; border-radius:6px; }
.lb-value { font-family:'Oswald'; font-weight:700; font-size:1.5rem; color:#fff; text-align:right; white-space:nowrap; }
.lb-value span { font-size:.72rem; color:#8A93A6; font-weight:500; margin-left:3px; }
.news-h { font-family:'Oswald'; font-size:1.25rem; color:#fff; margin:.2rem 0 .7rem; border-left:3px solid #00E5A0; padding-left:.5rem; }
.news-card { display:block; background:#131A26; border:1px solid rgba(255,255,255,.05); border-radius:12px; padding:12px 14px; margin-bottom:10px; text-decoration:none; }
.news-card:hover { border-color:rgba(0,229,160,.45); }
.news-title { color:#E9EDF5; font-size:.9rem; font-weight:600; line-height:1.3; }
.news-src { color:#00E5A0; font-size:.7rem; text-transform:uppercase; letter-spacing:.5px; margin-top:5px; }
.contact a { color:#C9D2DE !important; text-decoration:none; display:block; padding:4px 0; font-size:.92rem; }
.contact a:hover { color:#00E5A0 !important; }
.prof-hd { display:flex; align-items:center; gap:16px; margin:.4rem 0 1rem; }
.prof-hd img { width:84px; height:84px; border-radius:50%; object-fit:cover; background:#222C3D; border:3px solid rgba(255,255,255,.15); }
.prof-name { font-family:'Oswald'; font-size:2rem; color:#fff; line-height:1; }
.prof-meta { color:#00E5A0; font-weight:600; font-size:.95rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Cargando datos de la NFL...")
def load_season(season):
    df = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    return df.to_pandas()


@st.cache_resource
def load_teams():
    return nfl.load_teams()


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
    g = lambda c: int(p[c].sum())
    return {
        "pos": _mode(p["position"]), "team": _mode(p["team"]),
        "headshot": headshot_of(pdf, name),
        "Yds pase": g("passing_yards"), "TD pase": g("passing_tds"),
        "Yds tierra": g("rushing_yards"), "TD tierra": g("rushing_tds"),
        "Yds recep.": g("receiving_yards"),
        "TD tot.": g("passing_tds") + g("rushing_tds") + g("receiving_tds"),
    }


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
        out.append(
            f'<div class="lb-row"><div class="lb-rank {medal.get(i, "")}">{i+1}</div>'
            f'<img class="lb-photo" src="{r["headshot"]}" />'
            f'<div class="lb-info"><div class="lb-name">{r["name"]}</div>'
            f'<div class="lb-meta">{r["pos"]} · {r["team"]}</div>'
            f'<div class="lb-track"><div class="lb-fill" '
            f'style="width:{pct:.0f}%;background:{r["color"]}"></div></div></div>'
            f'<div class="lb-value">{val}<span>{suffix}</span></div></div>'
        )
    return "".join(out)


def news_html(items):
    if not items:
        return ('<div class="news-card"><div class="news-title">Noticias no '
                'disponibles ahora mismo.</div></div>')
    return "".join(
        f'<a class="news-card" href="{l}" target="_blank">'
        f'<div class="news-title">{t}</div><div class="news-src">Leer mas →</div></a>'
        for t, l in items)


# ---------------------------------------------------------------------------
# Barra lateral + cabecera
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🏈 EL PLAYBOOK NFL")
season = st.sidebar.selectbox("Temporada", list(range(2026, 1998, -1)), index=0)
pdf = load_season(season)
teams_df = load_teams()
teams = G.team_info(teams_df)
colors = {a: to_hex(c) for a, (c, _) in teams.items()}
weeks = sorted(pdf["week"].unique().tolist())
all_names = sorted(pdf.player_display_name.dropna().unique().tolist())

st.sidebar.markdown("---")
st.sidebar.markdown("**📣 Sigue al canal**")
links = "".join(f'<a href="{u}" target="_blank">{n}</a>' for n, u in REDES.items())
st.sidebar.markdown(f"<div class='contact'>{links}</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<br><span style='color:{ACCENT};font-weight:700'>{G.CANAL}</span>",
                    unsafe_allow_html=True)
st.sidebar.caption("Datos: nflverse")

st.markdown(f"""
<div class="hero">
  <div class="brand"><span class="ball">🏈</span>EL PLAYBOOK <span class="nfl">NFL</span></div>
  <div class="tagline">Datos NFL en español<br>Temporada {season}</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "📊 Comparar", "👤 Jugadores"])

# ---------------------------------------------------------------------------
# TAB 1 — Rankings + Noticias
# ---------------------------------------------------------------------------
with tab1:
    main, side = st.columns([2.4, 1], gap="large")
    with main:
        c1, c2, c3 = st.columns([2, 2, 1])
        stat_label = c1.selectbox("Metrica", [v[1] for v in G.STATS.values()], index=0)
        stat_key = [k for k, v in G.STATS.items() if v[1] == stat_label][0]
        ambito = c2.selectbox("Ambito", ["Temporada completa"]
                              + [f"Jornada {w}" for w in weeks])
        top_n = c3.slider("Top", 5, 15, 10)
        week = None if ambito == "Temporada completa" else int(ambito.split()[1])
        rows = leaderboard_data(pdf, colors, G.STATS[stat_key][0], week, top_n)
        sub = "Temporada completa" if week is None else f"Jornada {week}"
        st.markdown(f"<h2 style='margin:.3rem 0 1rem'>{stat_label} · {sub}</h2>",
                    unsafe_allow_html=True)
        st.markdown(leaderboard_html(rows, stat_key), unsafe_allow_html=True)
        with st.expander("⬇️ Descargar como imagen vertical (para subir)"):
            if st.button("Generar PNG del ranking", type="primary"):
                with st.spinner("Generando..."):
                    fig = G.make_ranking(pdf, season, week, stat_key, top_n, teams)
                    png = G.fig_a_png(fig)
                st.image(png, width=320)
                fn = f"ranking_{stat_key}_{season}" + (f"_j{week}" if week else "") + ".png"
                st.download_button("Descargar PNG", png, file_name=fn, mime="image/png")
    with side:
        st.markdown('<div class="news-h">📰 Últimas noticias</div>', unsafe_allow_html=True)
        st.markdown(news_html(get_news(NEWS_FEED)), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2 — Comparador
# ---------------------------------------------------------------------------
with tab2:
    st.markdown("<h2>Comparador de jugadores</h2>", unsafe_allow_html=True)
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
# TAB 3 — Jugadores (buscador + estrellas + ficha con tarjeta)
# ---------------------------------------------------------------------------
with tab3:
    if ("sel_player" not in st.session_state
            or st.session_state.sel_player not in all_names):
        st.session_state.sel_player = ("Josh Allen" if "Josh Allen" in all_names
                                       else all_names[0])

    def _pick(name):
        st.session_state.sel_player = name

    st.markdown("<h2>Jugadores</h2>", unsafe_allow_html=True)
    st.selectbox("🔍 Busca cualquier jugador", all_names, key="sel_player")

    famosos = [n for n in FAMOSOS if n in all_names][:6]
    if famosos:
        st.markdown("<div class='news-h'>⭐ Destacados</div>", unsafe_allow_html=True)
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
      <div class="prof-hd">
        <img src="{info['headshot']}"/>
        <div><div class="prof-name">{player.upper()}</div>
        <div class="prof-meta">{info['pos']} · {info['team']} · Temporada {season}</div></div>
      </div>""", unsafe_allow_html=True)

    m = st.columns(6)
    for col, key in zip(m, ["Yds pase", "TD pase", "Yds tierra", "TD tierra",
                            "Yds recep.", "TD tot."]):
        col.metric(key, f"{info[key]:,}".replace(",", "."))

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