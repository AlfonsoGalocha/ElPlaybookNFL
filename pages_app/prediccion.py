"""pages_app/prediccion.py — predicción del ganador de cada partido de una jornada.

De momento solo se elige el ganador (no el marcador exacto — eso vendrá más
adelante). Las predicciones se guardan en st.query_params (la URL de la pestaña),
no solo en st.session_state: así sobreviven a un F5/recarga real del navegador,
que reiniciaría cualquier cosa guardada solo en sesión. No hay usuarios ni base de
datos — es un "recuerda lo que elegiste en esta pestaña", nada más.
"""

import streamlit as st

from analytics.games import highlight_week
from analytics.utils import game_when_label
from components.tracking import track_prediction_made, track_prediction_viewed


def _pred_param_key(season, week):
    return f"pred_{season}_{week}"


def _game_key(g):
    return f"{g.home_team}{g.away_team}"


def _load_picks(season, week):
    raw = st.query_params.get(_pred_param_key(season, week), "")
    picks = {}
    for pair in raw.split(","):
        if ":" in pair:
            gk, team = pair.split(":", 1)
            picks[gk] = team
    return picks


def _save_picks(season, week, picks):
    key = _pred_param_key(season, week)
    if picks:
        st.query_params[key] = ",".join(f"{gk}:{team}" for gk, team in picks.items())
    elif key in st.query_params:
        del st.query_params[key]


def _pick_button(col, label, key, active):
    with col:
        return st.button(label, key=key, use_container_width=True,
                          type="primary" if active else "secondary")


def _prediction_card(g, team_meta, pick):
    home_meta = team_meta.get(g.home_team, {})
    away_meta = team_meta.get(g.away_team, {})
    when = game_when_label(g.gameday, g.gametime)
    made_class = " pred-made" if pick else ""
    st.markdown(f"""
      <div class="pred-card fade-up{made_class}">
        <div class="pred-time">{when}</div>
        <div class="pred-matchup">
          <div class="pred-team-info">
            <img src="{home_meta.get('logo', '')}"/>
            <div class="pt-name">{home_meta.get('name', g.home_team)}</div>
          </div>
          <div class="pred-vs">VS</div>
          <div class="pred-team-info">
            <img src="{away_meta.get('logo', '')}"/>
            <div class="pt-name">{away_meta.get('name', g.away_team)}</div>
          </div>
        </div>
      </div>""", unsafe_allow_html=True)


def render(ctx):
    # El evento de "pick hecho" se dispara aqui, en el rerun SIGUIENTE al clic, no
    # dentro del propio manejador del boton. tracking.py inyecta el script en un
    # iframe (components.html) que necesita un instante para cargar y ejecutarse en
    # el navegador; si el manejador del boton llama a st.rerun() justo despues (como
    # hace este, para refrescar la tarjeta al instante), ese rerun sustituye el DOM
    # antes de que el iframe llegue a ejecutar su script y el evento se pierde. Al
    # disparar el evento en el siguiente render (uno que no termina en rerun), el
    # iframe tiene tiempo de sobra para cargar.
    pending = st.session_state.pop("pred_pending_track", None)
    if pending:
        track_prediction_made(*pending)

    st.markdown('<div class="sect-title">Predicción de la jornada</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sect-sub">Elige quién crees que gana cada partido. De momento solo el '
        'ganador — el marcador exacto llegará más adelante.</div>',
        unsafe_allow_html=True)

    week_options = sorted(ctx.sched.week.unique().tolist())
    if not week_options:
        st.info("Todavía no hay calendario disponible para esta temporada.")
        return

    current_week = highlight_week(ctx.sched)
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        st.markdown("#### Jornada a predecir")
    with hc2:
        week = st.selectbox("Jornada", week_options,
                             index=week_options.index(current_week) if current_week in week_options else 0,
                             key="pred_week", label_visibility="collapsed")

    games = ctx.sched[ctx.sched.week == week].sort_values("gameday")
    if games.empty:
        st.info("Todavía no hay partidos programados para esta jornada.")
        return

    track_prediction_viewed()
    game_list = list(games.itertuples())
    picks = _load_picks(ctx.season, week)
    made = sum(1 for g in game_list if _game_key(g) in picks)
    st.markdown(f"#### {made}/{len(game_list)} predicciones hechas")
    st.progress(made / len(game_list) if game_list else 0)

    for i in range(0, len(game_list), 2):
        row = game_list[i:i + 2]
        cols = st.columns(2)
        for col, g in zip(cols, row):
            with col:
                gk = _game_key(g)
                pick = picks.get(gk)
                _prediction_card(g, ctx.team_meta, pick)
                b1, b2 = st.columns(2)
                home_label = ctx.team_meta.get(g.home_team, {}).get("name", g.home_team)
                away_label = ctx.team_meta.get(g.away_team, {}).get("name", g.away_team)
                if _pick_button(b1, home_label, f"pred_{gk}_home", pick == g.home_team):
                    picks[gk] = g.home_team
                    _save_picks(ctx.season, week, picks)
                    st.session_state.pred_pending_track = (week, g.home_team)
                    st.rerun()
                if _pick_button(b2, away_label, f"pred_{gk}_away", pick == g.away_team):
                    picks[gk] = g.away_team
                    _save_picks(ctx.season, week, picks)
                    st.session_state.pred_pending_track = (week, g.away_team)
                    st.rerun()
