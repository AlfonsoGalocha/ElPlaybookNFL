"""pages_app/partido.py — Resumen de Partido: análisis (no en vivo) de un partido ya disputado.

Reutiliza analytics.efficiency (contexto de temporada) y analytics.matchups
(Duelo Clave) tal cual las usa Matchups, y nfl_graficos para las tiles de
jugador — nada de esto se duplica aquí.
"""

import plotly.graph_objects as go
import streamlit as st

import nfl_graficos as G
from analytics.efficiency import team_efficiency_table
from analytics.explanations import breakdown_insight, epa_breakdown
from analytics.game_summary import game_pbp, key_factors, quarter_epa_evolution, team_boxscore
from analytics.matchups import duelo_clave, with_percentiles
from components.explanation import why_expander
from data.loaders import load_pbp

FG, ACCENT = G.FG, G.ACCENT


def _boxscore_html(home_box, away_box, home_name, away_name):
    rows = [
        ("Yardas totales", home_box["total_yards"], away_box["total_yards"]),
        ("Yardas de pase", home_box["pass_yards"], away_box["pass_yards"]),
        ("Yardas de carrera", home_box["rush_yards"], away_box["rush_yards"]),
        ("Pérdidas de balón", home_box["turnovers"], away_box["turnovers"]),
        ("Sacks encajados", home_box["sacks_allowed"], away_box["sacks_allowed"]),
        ("Jugadas explosivas (20+ yds)", home_box["explosive_plays"], away_box["explosive_plays"]),
    ]
    if home_box.get("third_pct") is not None and away_box.get("third_pct") is not None:
        rows.append(("Acierto en 3ª down", f"{home_box['third_pct']:.0%}", f"{away_box['third_pct']:.0%}"))
    if home_box.get("rz_pct") is not None and away_box.get("rz_pct") is not None:
        rows.append(("TD en zona roja", f"{home_box['rz_pct']:.0%}", f"{away_box['rz_pct']:.0%}"))
    head = (f'<div class="std-head"><div class="std-team">Estadística</div>'
            f'<div class="std-stat" style="width:130px">{home_name}</div>'
            f'<div class="std-stat" style="width:130px">{away_name}</div></div>')
    body = "".join(
        f'<div class="std-row"><div class="std-team">{label}</div>'
        f'<div class="std-stat" style="width:130px">{h}</div>'
        f'<div class="std-stat" style="width:130px">{a}</div></div>'
        for label, h, a in rows
    )
    return head + body


def _top_performers(pdf, week, teams, n=4):
    pool = pdf[(pdf.week == week) & (pdf.team.isin(teams))].copy()
    tds = pool.passing_tds.fillna(0) + pool.rushing_tds.fillna(0) + pool.receiving_tds.fillna(0)
    yards = pool.passing_yards.fillna(0) + pool.rushing_yards.fillna(0) + pool.receiving_yards.fillna(0)
    pool["_sort"] = tds * 6 + yards
    return pool[pool["_sort"] > 0].sort_values("_sort", ascending=False).head(n)


def render(ctx):
    st.markdown('<div class="sect-title">Resumen de Partido</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Análisis de un partido ya disputado con los datos completos '
                '— no es un marcador en vivo.</div>', unsafe_allow_html=True)

    played = ctx.sched[ctx.sched.home_score.notna()].sort_values(["week", "gameday"])
    if played.empty:
        st.info("Todavía no hay partidos disputados esta temporada.")
        return

    weeks = sorted(played.week.unique().tolist())
    c1, c2 = st.columns([1, 3])
    week = c1.selectbox("Jornada", weeks, index=len(weeks) - 1, key="partido_week")
    week_games = played[played.week == week]
    if week_games.empty:
        st.info("No hay partidos disputados en esa jornada.")
        return

    labels = {}
    for g in week_games.itertuples():
        a_name = ctx.team_meta.get(g.away_team, {}).get("name", g.away_team)
        h_name = ctx.team_meta.get(g.home_team, {}).get("name", g.home_team)
        labels[f"{a_name} @ {h_name}  ({int(g.away_score)}-{int(g.home_score)})"] = g.game_id
    label = c2.selectbox("Partido", list(labels.keys()), key="partido_game")
    game_id = labels[label]
    g = week_games[week_games.game_id == game_id].iloc[0]
    home, away = g.home_team, g.away_team
    home_meta, away_meta = ctx.team_meta.get(home, {}), ctx.team_meta.get(away, {})
    home_name, away_name = home_meta.get("name", home), away_meta.get("name", away)

    st.markdown(f"""
      <div class="team-hd fade-up">
        <img src="{away_meta.get('logo', '')}" style="width:56px;height:56px"/>
        <div style="flex:1; text-align:center">
          <div class="tname" style="font-size:1.7rem">{away_name} {int(g.away_score)}
          <span style="opacity:.5; font-size:1.1rem"> — </span>
          {int(g.home_score)} {home_name}</div>
          <div class="tmeta">Semana {week} · {g.gameday}</div>
        </div>
        <img src="{home_meta.get('logo', '')}" style="width:56px;height:56px"/>
      </div>""", unsafe_allow_html=True)

    pbp = load_pbp(ctx.season)
    if pbp is None or pbp.empty:
        st.info("No hay datos de jugada a jugada disponibles todavía para analizar este partido.")
        return
    gp = game_pbp(pbp, game_id)
    if gp.empty:
        st.info("Todavía no hay jugada a jugada disponible para este partido concreto.")
        return

    home_box, away_box = team_boxscore(gp, home), team_boxscore(gp, away)
    if home_box and away_box:
        st.markdown("#### Resumen")
        st.markdown(_boxscore_html(home_box, away_box, home_name, away_name), unsafe_allow_html=True)

        factors = key_factors(home_box, away_box, home_name, away_name)
        if factors:
            st.markdown("#### 🔑 Claves del partido")
            for f in factors:
                st.markdown(f"- {f}")

        bd_home = epa_breakdown(gp[gp.posteam == home])
        bd_away = epa_breakdown(gp[gp.posteam == away])
        if bd_home or bd_away:
            c1, c2 = st.columns(2)
            with c1:
                why_expander(bd_home, breakdown_insight(bd_home, subject=f"El ataque de {home_name}"),
                             label=f"¿Por qué? · {home_name}")
            with c2:
                why_expander(bd_away, breakdown_insight(bd_away, subject=f"El ataque de {away_name}"),
                             label=f"¿Por qué? · {away_name}")
    else:
        st.info("No hay estadísticas de equipo suficientes para este partido en el play-by-play.")

    qe = quarter_epa_evolution(gp)
    st.markdown("#### 📈 Evolución del partido (EPA acumulado)")
    if qe:
        fig = go.Figure()
        for team, d in qe.items():
            meta = ctx.team_meta.get(team, {})
            fig.add_trace(go.Scatter(x=d["qtr"], y=d["cum_epa"], mode="lines+markers",
                                      name=meta.get("name", team),
                                      line=dict(color=ctx.colors.get(team, ACCENT), width=3)))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           height=320, margin=dict(l=10, r=20, t=10, b=10), font=dict(color=FG),
                           xaxis_title="Cuarto", yaxis_title="EPA acumulado",
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No hay suficiente detalle de jugada a jugada para mostrar la evolución por cuarto "
                   "de este partido.")

    top = _top_performers(ctx.pdf, week, [home, away])
    if not top.empty:
        st.markdown("#### ⭐ Jugadores destacados")
        cols = st.columns(len(top))
        for col, row in zip(cols, top.itertuples()):
            p = ctx.pdf[(ctx.pdf.player_display_name == row.player_display_name) & (ctx.pdf.week == week)]
            tiles = G._tiles(row.position, G.player_totals(p))
            with col:
                st.markdown(f"**{row.player_display_name}**")
                st.caption(f"{row.position} · {row.team}")
                for tl, tv in tiles[:3]:
                    st.metric(tl, tv)

    eff = team_efficiency_table(pbp).dropna(subset=["off_epa_play", "def_epa_play"])
    if len(eff) >= 2 and home in eff.team.values and away in eff.team.values:
        pct = with_percentiles(eff)
        duel = duelo_clave(pct, home, away)
        if duel:
            st.markdown(f"""
              <div class="duel-card fade-up">
                <div class="dc-tag">⚔️ EL DUELO CLAVE · SEGÚN CONTEXTO DE TEMPORADA</div>
                <div class="dc-title">{duel['label']}</div>
                <div class="dc-detail">EPA/jugada de ataque: {duel['off_epa']:+.3f}
                (percentil {duel['off_pct']:.0f}) frente a EPA/jugada permitida en defensa:
                {duel['def_epa']:+.3f} (percentil {duel['def_pct']:.0f}), con datos de toda la temporada.</div>
              </div>""", unsafe_allow_html=True)
