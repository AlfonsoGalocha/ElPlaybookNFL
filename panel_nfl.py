#!/usr/bin/env python3
"""
panel_nfl.py — Panel INTERACTIVO de la NFL, todo en uno:
  1) Comparador de jugadores (tabla + barras + radar)
  2) Ranking de jornada/temporada  -> imagen vertical descargable
  3) Tarjeta de jugador (con foto)  -> imagen vertical descargable

Datos: nflverse (gratis y abierto) via nflreadpy.

Como se lanza (NO es 'python3'):
    streamlit run panel_nfl.py
Se abre solo en el navegador (http://localhost:8501). Para cerrarlo: Ctrl+C.
"""

import numpy as np
import polars as pl
import plotly.graph_objects as go
import streamlit as st
import nflreadpy as nfl
from matplotlib.colors import to_hex

import nfl_graficos as G   # modulo compartido con las imagenes

BG, CARD, FG, MUTED, ACCENT = G.BG, G.CARD, G.FG, G.MUTED, G.ACCENT

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

st.set_page_config(page_title="EL PLAYBOOK NFL", page_icon="🏈", layout="wide")
st.markdown(f"""
<style>
  .stApp {{ background:{BG}; color:{FG}; }}
  section[data-testid="stSidebar"] {{ background:{CARD}; }}
  h1,h2,h3,h4 {{ color:{FG}; }}
  .marca {{ color:{ACCENT}; font-weight:800; letter-spacing:1px; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Cargando datos de la NFL...")
def load_season(season):
    df = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    return df.to_pandas()


@st.cache_resource
def load_teams():
    return nfl.load_teams()


def totals_table(pdf, week_range=None):
    d = pdf
    if week_range is not None:
        d = d[(d["week"] >= week_range[0]) & (d["week"] <= week_range[1])]
    g = d.groupby("player_display_name").agg(
        position=("position", lambda x: x.mode().iloc[0] if len(x.mode()) else ""),
        team=("team", lambda x: x.mode().iloc[0] if len(x.mode()) else ""),
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


# ===========================================================================
# Barra lateral
# ===========================================================================
st.sidebar.markdown("### 🏈 EL PLAYBOOK NFL")
season = st.sidebar.selectbox("Temporada", list(range(2026, 1998, -1)), index=0)
pdf = load_season(season)
teams_df = load_teams()
teams = G.team_info(teams_df)
colors = {a: to_hex(c) for a, (c, _) in teams.items()}   # hex para Plotly
weeks = sorted(pdf["week"].unique().tolist())
st.sidebar.markdown(f"<br><span class='marca'>{G.CANAL}</span>",
                    unsafe_allow_html=True)
st.sidebar.caption("Datos: nflverse")

tab1, tab2, tab3 = st.tabs(["📊 Comparar", "📈 Ranking", "🪪 Tarjeta"])

# ---------------------------------------------------------------------------
# TAB 1 — Comparador
# ---------------------------------------------------------------------------
with tab1:
    st.markdown(f"## Comparador de jugadores  \n**Temporada {season}**")
    scope = st.radio("Ambito", ["Temporada completa", "Rango de jornadas"],
                     horizontal=True, key="cmp_scope")
    wr = None
    if scope == "Rango de jornadas" and len(weeks) > 1:
        wr = st.slider("Jornadas", min(weeks), max(weeks), (min(weeks), max(weeks)))
    totals = totals_table(pdf, wr)
    active = totals[(totals.passing_yards + totals.rushing_yards
                     + totals.receiving_yards) > 0]
    names = sorted(active.player_display_name.tolist())
    default = [n for n in ["Josh Allen", "Lamar Jackson", "Jalen Hurts"]
               if n in names][:2]
    picked = st.multiselect("Jugadores a comparar", names, default=default)
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
            st.subheader(metric_label)
            mcol = METRICS[metric_label]
            b = sel.sort_values(mcol)
            fig = go.Figure(go.Bar(
                x=b[mcol], y=b.player_display_name, orientation="h",
                marker_color=[colors.get(t, ACCENT) for t in b.team],
                text=b[mcol], textposition="outside"))
            fig.update_layout(template="plotly_dark", paper_bgcolor=BG,
                plot_bgcolor=BG, height=90 + 70 * len(b),
                margin=dict(l=10, r=30, t=10, b=10), font=dict(color=FG),
                showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Perfil comparado (radar)")
            lbls, acols = list(RADAR_AXES), list(RADAR_AXES.values())
            mx = {c: max(sel[c].max(), 1) for c in acols}
            radar = go.Figure()
            for _, row in sel.iterrows():
                vv = [row[c] / mx[c] for c in acols]
                radar.add_trace(go.Scatterpolar(
                    r=vv + [vv[0]], theta=lbls + [lbls[0]], fill="toself",
                    name=row.player_display_name,
                    line_color=colors.get(row.team, ACCENT)))
            radar.update_layout(template="plotly_dark", paper_bgcolor=BG,
                polar=dict(bgcolor=CARD, radialaxis=dict(visible=True,
                    range=[0, 1], showticklabels=False)),
                height=430, margin=dict(l=30, r=30, t=30, b=30),
                font=dict(color=FG), legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(radar, use_container_width=True)
        st.caption("El radar normaliza cada eje respecto al mejor de los elegidos: "
                   "muestra PERFILES, no valores absolutos (esos, en la tabla).")

# ---------------------------------------------------------------------------
# TAB 2 — Ranking descargable
# ---------------------------------------------------------------------------
with tab2:
    st.markdown(f"## Ranking · Temporada {season}")
    c1, c2, c3 = st.columns(3)
    stat_label = c1.selectbox("Metrica", [v[1] for v in G.STATS.values()], index=0)
    stat_key = [k for k, v in G.STATS.items() if v[1] == stat_label][0]
    ambito = c2.selectbox("Ambito", ["Temporada completa"]
                          + [f"Jornada {w}" for w in weeks])
    top_n = c3.slider("Cuantos jugadores", 5, 12, 10)
    week = None if ambito == "Temporada completa" else int(ambito.split()[1])

    if st.button("Generar ranking", type="primary"):
        with st.spinner("Generando imagen..."):
            fig = G.make_ranking(pdf, season, week, stat_key, top_n, teams)
            png = G.fig_a_png(fig)
        st.image(png, width=360)
        fname = f"ranking_{stat_key}_{season}" + (f"_j{week}" if week else "") + ".png"
        st.download_button("⬇️ Descargar PNG", png, file_name=fname,
                           mime="image/png")

# ---------------------------------------------------------------------------
# TAB 3 — Tarjeta descargable
# ---------------------------------------------------------------------------
with tab3:
    st.markdown(f"## Tarjeta de jugador · Temporada {season}")
    all_names = sorted(pdf.player_display_name.dropna().unique().tolist())
    idx = all_names.index("Josh Allen") if "Josh Allen" in all_names else 0
    player = st.selectbox("Jugador", all_names, index=idx)
    modo = st.radio("Imagen", ["Cara (circulo)", "Cuerpo (imagen grande)"],
                    horizontal=True)
    modo_key = "circulo" if modo.startswith("Cara") else "cuerpo"
    up = st.file_uploader("Tu propia foto (opcional; PNG con fondo transparente "
                          "para 'cuerpo')", type=["png", "jpg", "jpeg"])

    if st.button("Generar tarjeta", type="primary"):
        foto = None
        if up is not None:
            from PIL import Image
            foto = np.asarray(Image.open(up).convert("RGBA")).astype(float) / 255.0
        with st.spinner("Generando tarjeta..."):
            fig = G.make_card(pdf, season, player, teams, modo_key, foto)
            png = G.fig_a_png(fig)
        st.image(png, width=360)
        fname = f"tarjeta_{player.lower().replace(' ', '_')}_{season}.png"
        st.download_button("⬇️ Descargar PNG", png, file_name=fname,
                           mime="image/png")
        if up is None and modo_key == "circulo":
            st.caption("Si no aparece la foto, es que el servidor no pudo bajarla; "
                       "sube una tu mismo o usa el modo cuerpo con tu recorte.")
