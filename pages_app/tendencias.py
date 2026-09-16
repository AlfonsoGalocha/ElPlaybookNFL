"""pages_app/tendencias.py — cambios de rendimiento entre jornadas, con los datos siempre visibles."""

import plotly.graph_objects as go
import streamlit as st

import nfl_graficos as G
from analytics.trends import MIN_WEEKS_FOR_TREND, trend_table, weekly_team_epa, weekly_team_situational
from data.loaders import load_pbp

FG, ACCENT, ACCENT2 = G.FG, G.ACCENT, G.ACCENT2


def _trend_movers(result, label_fmt, higher_is_better=True):
    table = result["table"]
    subida = table.sort_values("delta", ascending=not higher_is_better).head(5)
    bajada = table.sort_values("delta", ascending=higher_is_better).head(5)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 📈 Suben")
        for _, r in subida.iterrows():
            st.markdown(f"**{r.team}** — {label_fmt(r.early)} → {label_fmt(r.recent)} "
                        f"<span class='up-badge'>({r.delta:+.3f})</span>", unsafe_allow_html=True)
    with c2:
        st.markdown("##### 📉 Bajan")
        for _, r in bajada.iterrows():
            st.markdown(f"**{r.team}** — {label_fmt(r.early)} → {label_fmt(r.recent)} "
                        f"<span class='down-badge'>({r.delta:+.3f})</span>", unsafe_allow_html=True)
    st.caption(f"Comparando jornadas {result['early_weeks'][0]}–{result['early_weeks'][-1]} "
               f"frente a {result['recent_weeks'][0]}–{result['recent_weeks'][-1]}.")


def render(ctx):
    st.markdown('<div class="sect-title">Tendencias</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Qué ha cambiado entre las primeras y las últimas jornadas, '
                'siempre con los datos a la vista.</div>', unsafe_allow_html=True)

    pbp = load_pbp(ctx.season)
    if pbp is None or pbp.empty:
        st.warning("No hay datos de jugada a jugada disponibles todavía para esta temporada.")
        return

    n_weeks = pbp.week.nunique()
    if n_weeks < MIN_WEEKS_FOR_TREND:
        st.info(f"Esta temporada solo lleva {n_weeks} jornada(s) con datos. Necesitamos al menos "
                f"{MIN_WEEKS_FOR_TREND} para comparar 'antes' contra 'ahora' de forma fiable — "
                "por ahora te enseñamos la evolución semana a semana.")

    st.markdown("#### Eficiencia de ataque (EPA/jugada) — ¿quién sube y quién baja?")
    weekly_epa = weekly_team_epa(pbp)
    result = trend_table(weekly_epa, "epa_play", weight_col="plays")
    if result:
        _trend_movers(result, lambda v: f"{v:+.3f} EPA/jugada")
    else:
        st.caption("Con más jornadas jugadas podremos comparar la tendencia de forma fiable.")

    st.markdown("#### % de jugadas de pase — ¿quién está pasando más o menos que al principio?")
    weekly_pass = weekly_team_situational(pbp)
    result_pass = trend_table(weekly_pass, "pass_rate", weight_col="plays")
    if result_pass:
        _trend_movers(result_pass, lambda v: f"{v*100:.0f}% pase")
    else:
        st.caption("Con más jornadas jugadas podremos comparar la tendencia de forma fiable.")

    st.markdown("---")
    st.markdown("#### Evolución semana a semana de un equipo")
    team = st.selectbox("Equipo", ctx.all_teams,
                        index=ctx.all_teams.index("BUF") if "BUF" in ctx.all_teams else 0)
    td = weekly_epa[weekly_epa.team == team].sort_values("week")
    if td.empty:
        st.info("Sin jugadas registradas para este equipo todavía.")
        return
    fig = go.Figure(go.Scatter(x=td.week, y=td.epa_play, mode="lines+markers",
                               line=dict(color=ctx.colors.get(team, ACCENT), width=3),
                               marker=dict(size=8)))
    fig.add_hline(y=0, line_color="rgba(255,255,255,.25)")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       height=340, margin=dict(l=10, r=20, t=20, b=10), font=dict(color=FG),
                       xaxis_title="Jornada", yaxis_title="EPA/jugada (ataque)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("EPA/jugada medio de las jugadas de ataque de este equipo, calculado semana a semana "
               "sobre el play-by-play oficial.")
