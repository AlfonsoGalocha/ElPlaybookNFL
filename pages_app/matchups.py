"""pages_app/matchups.py — comparativa ataque/defensa entre dos equipos y el Duelo Clave."""

import streamlit as st

import nfl_graficos as G
from analytics.efficiency import team_efficiency_table, team_situational_table
from analytics.explanations import breakdown_insight, epa_breakdown
from analytics.matchups import duelo_clave, with_percentiles
from components.explanation import why_expander
from components.tracking import track_matchup_viewed
from data.loaders import load_pbp, load_pfr

ACCENT, ACCENT2 = G.ACCENT, G.ACCENT2


def _vs_card(label, val_a, val_b, team_a, team_b, fmt="{:+.3f}", higher_is_better=True):
    better_a = (val_a > val_b) if higher_is_better else (val_a < val_b)
    ca = "up-badge" if better_a else ""
    cb = "up-badge" if not better_a else ""
    st.markdown(f"""
      <div class="stat-card">
        <div class="sc-label">{label}</div>
        <div style="display:flex; justify-content:space-between; margin-top:8px">
          <div><div class="sc-value {ca}">{fmt.format(val_a)}</div><div class="sc-label">{team_a}</div></div>
          <div style="text-align:right"><div class="sc-value {cb}">{fmt.format(val_b)}</div>
          <div class="sc-label">{team_b}</div></div>
        </div>
      </div>""", unsafe_allow_html=True)


def render(ctx):
    st.markdown('<div class="sect-title">Matchups</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Compara dos equipos con datos reales: ataque, defensa y el '
                'duelo que puede decidir el partido.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    default_a = "BUF" if "BUF" in ctx.all_teams else ctx.all_teams[0]
    default_b = "KC" if "KC" in ctx.all_teams else ctx.all_teams[-1]
    team_a = c1.selectbox("Equipo A", ctx.all_teams, index=ctx.all_teams.index(default_a))
    team_b = c2.selectbox("Equipo B", ctx.all_teams,
                          index=ctx.all_teams.index(default_b) if default_b != team_a else
                          (ctx.all_teams.index(default_b) + 1) % len(ctx.all_teams))

    if team_a == team_b:
        st.info("Elige dos equipos distintos para comparar.")
        return

    track_matchup_viewed(team_a, team_b)

    pbp = load_pbp(ctx.season)
    if pbp is None or pbp.empty:
        st.warning("No hay datos de jugada a jugada disponibles todavía para esta temporada.")
        return

    eff = team_efficiency_table(pbp).dropna(subset=["off_epa_play", "def_epa_play"])
    if team_a not in eff.team.values or team_b not in eff.team.values:
        st.info("Todavía no hay jugadas suficientes de alguno de los dos equipos esta temporada.")
        return
    pct = with_percentiles(eff)
    duel = duelo_clave(pct, team_a, team_b)

    meta_a, meta_b = ctx.team_meta[team_a], ctx.team_meta[team_b]
    if duel:
        st.markdown(f"""
          <div class="duel-card fade-up">
            <div class="dc-tag">⚔️ EL DUELO CLAVE</div>
            <div class="dc-title">{duel['label']}</div>
            <div class="dc-detail">EPA/jugada del ataque de {duel['off_team']}: <b>{duel['off_epa']:+.3f}</b>
            (percentil {duel['off_pct']:.0f} de la liga) · EPA/jugada permitida por la defensa de
            {duel['def_team']}: <b>{duel['def_epa']:+.3f}</b> (percentil {duel['def_pct']:.0f} en defensa).</div>
            <div class="dc-detail" style="margin-top:6px">{'Ventaja para el ataque' if duel['favours_offense'] else 'Ventaja para la defensa'}
            según los datos de esta temporada.</div>
          </div>""", unsafe_allow_html=True)

    a_row = eff[eff.team == team_a].iloc[0]
    b_row = eff[eff.team == team_b].iloc[0]

    st.markdown("#### Ataque vs Ataque")
    c1, c2 = st.columns(2)
    with c1:
        _vs_card("EPA/jugada (ataque)", a_row.off_epa_play, b_row.off_epa_play, team_a, team_b)
        bd_a = epa_breakdown(pbp[pbp.posteam == team_a])
        why_expander(bd_a, breakdown_insight(bd_a, subject=f"El ataque de {team_a}"),
                     label=f"¿Por qué? · {team_a}")
        bd_b = epa_breakdown(pbp[pbp.posteam == team_b])
        why_expander(bd_b, breakdown_insight(bd_b, subject=f"El ataque de {team_b}"),
                     label=f"¿Por qué? · {team_b}")
    with c2:
        _vs_card("% de jugadas exitosas (ataque)", a_row.off_success, b_row.off_success,
                  team_a, team_b, fmt="{:.1%}")

    st.markdown("#### Defensa vs Defensa")
    st.caption("Menor EPA/jugada permitida = mejor defensa.")
    c1, c2 = st.columns(2)
    with c1:
        _vs_card("EPA/jugada permitida", a_row.def_epa_play, b_row.def_epa_play, team_a, team_b,
                  higher_is_better=False)
    with c2:
        _vs_card("% de jugadas exitosas permitidas", a_row.def_success, b_row.def_success,
                  team_a, team_b, fmt="{:.1%}", higher_is_better=False)

    sit = team_situational_table(pbp)
    sa = sit[sit.team == team_a]
    sb = sit[sit.team == team_b]
    if len(sa) and len(sb):
        sa, sb = sa.iloc[0], sb.iloc[0]
        st.markdown("#### Tendencias de juego")
        c1, c2, c3 = st.columns(3)
        with c1:
            _vs_card("% de jugadas de pase", sa.pass_rate, sb.pass_rate, team_a, team_b, fmt="{:.0%}")
        with c2:
            _vs_card("Acierto en 3ª down", sa.third_down_pct, sb.third_down_pct, team_a, team_b, fmt="{:.0%}")
        with c3:
            _vs_card("% TD en zona roja", sa.rz_td_pct, sb.rz_td_pct, team_a, team_b, fmt="{:.0%}")

    pfr_def = load_pfr("def", ctx.season)
    if pfr_def is not None and not pfr_def.empty:
        team_pressure = pfr_def.groupby("team").agg(def_pressures=("def_pressures", "sum"),
                                                      def_sacks=("def_sacks", "sum")).reset_index()
        pa = team_pressure[team_pressure.team == team_a]
        pb = team_pressure[team_pressure.team == team_b]
        if len(pa) and len(pb):
            st.markdown("#### Pass rush")
            c1, c2 = st.columns(2)
            with c1:
                _vs_card("Presiones generadas (temporada)", pa.iloc[0].def_pressures, pb.iloc[0].def_pressures,
                          team_a, team_b, fmt="{:.0f}")
            with c2:
                _vs_card("Sacks (temporada)", pa.iloc[0].def_sacks, pb.iloc[0].def_sacks,
                          team_a, team_b, fmt="{:.0f}")

    st.caption("Todos los datos de esta página son medias o sumas directas del play-by-play y de las "
               "estadísticas avanzadas de nflverse — el Duelo Clave se calcula por percentil real de "
               "EPA/jugada, no por una puntuación inventada.")
