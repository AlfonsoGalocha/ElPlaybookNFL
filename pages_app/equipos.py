"""pages_app/equipos.py — selector de equipo + stats del equipo + plantilla clicable."""

import streamlit as st

import nfl_graficos as G
from analytics.totals import team_stat_tiles, totals_table
from components.hero import team_news_html
from components.navbar import go_to
from share.cards import team_summary_card


def render(ctx):
    st.markdown('<div class="sect-title">Equipos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Elige un equipo para ver su récord, sus stats y su plantilla completa.</div>',
                unsafe_allow_html=True)

    if ("sel_team" not in st.session_state
            or st.session_state.sel_team not in ctx.all_teams):
        st.session_state.sel_team = "BUF" if "BUF" in ctx.all_teams else ctx.all_teams[0]

    for conf in ["AFC", "NFC"]:
        st.markdown(f'<div class="conf-h">{conf}</div>', unsafe_allow_html=True)
        conf_teams = sorted(a for a in ctx.all_teams if ctx.team_meta[a]["conf"] == conf)
        cols = st.columns(8)
        for i, abbr in enumerate(conf_teams):
            with cols[i % 8]:
                meta = ctx.team_meta[abbr]
                st.markdown(f"<div class='team-pick'><img src='{meta['logo']}'></div>",
                            unsafe_allow_html=True)
                active = st.session_state.sel_team == abbr
                if st.button(abbr, key=f"team_{abbr}", use_container_width=True,
                             type="primary" if active else "secondary"):
                    st.session_state.sel_team = abbr
                    st.rerun()

    st.markdown("---")
    team = st.session_state.sel_team
    meta = ctx.team_meta[team]
    std_rows = ctx.standings[ctx.standings.team == team]
    st.markdown(f"""
      <div class="team-hd fade-up" style="background:linear-gradient(120deg,{meta['color']}33,transparent)">
        <img src="{meta['logo']}"/>
        <div><div class="tname">{meta['name'].upper()}</div>
        <div class="tmeta">{meta['conf']} · {meta['div']} · Temporada {ctx.season}</div></div>
      </div>""", unsafe_allow_html=True)

    tiles = None
    if len(std_rows):
        s = G.player_totals(ctx.pdf[ctx.pdf.team == team])
        tiles = team_stat_tiles(std_rows.iloc[0], s)
        m = st.columns(len(tiles))
        for col, (label, value) in zip(m, tiles):
            col.metric(label, value)

    with st.expander("📤 Compartir resumen del equipo"):
        if tiles and st.button("Generar imagen", type="primary", key="share_team"):
            with st.spinner("Generando..."):
                png = team_summary_card(meta["name"], meta, ctx.season, tiles)
            st.image(png, width=280)
            st.download_button("⬇️ Descargar PNG", png, file_name=f"equipo_{team}_{ctx.season}.png",
                               mime="image/png")

    st.markdown("#### Plantilla")
    roster = totals_table(ctx.pdf[ctx.pdf.team == team])
    p_left, p_right = st.columns([1.6, 1])
    with p_left:
        if roster.empty:
            st.info("No hay jugadores con estadisticas para este equipo en esta temporada.")
        else:
            roster["yds_total"] = roster.passing_yards + roster.rushing_yards + roster.receiving_yards
            roster["td_total"] = roster.passing_tds + roster.rushing_tds + roster.receiving_tds
            roster = roster.sort_values(["yds_total", "td_total"], ascending=False)
            with st.container(height=420, border=True):
                for _, row in roster.iterrows():
                    label = f"{row.player_display_name}  ·  {row.position or '?'}"
                    if st.button(label, key=f"roster_{team}_{row.player_display_name}",
                                 use_container_width=True):
                        go_to("jugadores", sel_player=row.player_display_name)
    with p_right:
        st.markdown(team_news_html(meta), unsafe_allow_html=True)
