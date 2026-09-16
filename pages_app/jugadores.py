"""pages_app/jugadores.py — buscador + estrellas destacadas + ficha con tarjeta descargable."""

import numpy as np
import streamlit as st

import nfl_graficos as G
from analytics.totals import player_season
from analytics.utils import headshot_of

FAMOSOS = ["Patrick Mahomes", "Josh Allen", "Lamar Jackson", "Jalen Hurts",
           "Joe Burrow", "Ja'Marr Chase", "Justin Jefferson",
           "Christian McCaffrey", "Saquon Barkley", "Travis Kelce"]


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
    info = player_season(ctx.pdf, player)
    headshot = headshot_of(ctx.pdf, player)
    st.markdown(f"""
      <div class="prof-hd fade-up">
        <img src="{headshot}"/>
        <div><div class="prof-name">{player.upper()}</div>
        <div class="prof-meta">{info['pos']} · {info['team']} · Temporada {ctx.season}</div></div>
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
            fig = G.make_card(ctx.pdf, ctx.season, player, ctx.teams, modo_key, foto)
            png = G.fig_a_png(fig)
        st.image(png, width=340)
        fn = f"tarjeta_{player.lower().replace(' ', '_')}_{ctx.season}.png"
        st.download_button("⬇️ Descargar PNG", png, file_name=fn, mime="image/png")
