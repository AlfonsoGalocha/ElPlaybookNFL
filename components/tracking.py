"""components/tracking.py — eventos de Google Analytics 4 (GA4) desde Streamlit.

(Se llama "tracking" y no "analytics" para no confundirse con el paquete
`analytics/` del proyecto, que son funciones puras de agregacion de datos de la
NFL y no tiene nada que ver con Google Analytics.)

Dos problemas de Streamlit que este modulo resuelve:

1. Un <script> insertado via st.markdown(unsafe_allow_html=True) NUNCA se ejecuta
   (el HTML Standard trata como inertes los <script> metidos por innerHTML). La
   unica forma de ejecutar JS de verdad es un iframe real
   (streamlit.components.v1.html), que al ser same-origin puede escribir en
   `window.parent` (la pagina real de la app, no el iframe). Cada llamada de este
   modulo crea su propio iframe — por eso todo se lee/escribe siempre en
   `window.parent.dataLayer`, nunca en variables locales al iframo, que no
   persistirian entre llamadas. Ver components/head_tags.py para el mismo patron
   aplicado a la carga de gtag.js.

   Ademas, como cada iframe carga de forma independiente, no hay garantia de que
   el iframe que carga gtag.js (components/head_tags.py) termine de ejecutarse
   antes que el iframe de un evento. Por eso aqui no se llama a `gtag()` como
   funcion — se empuja directamente a `window.parent.dataLayer` con el mismo
   formato que gtag.js usa por debajo (`['event', nombre, params]`), que es
   precisamente el patron de cola que gtag.js esta diseñado para vaciar en cuanto
   termina de cargar, sin importar el orden de ejecucion.

2. Streamlit vuelve a ejecutar TODO el script de Python en cada interaccion
   (cambiar de pagina, pulsar un boton, mover un selector...), no solo cuando el
   usuario navega de verdad. Si mandaramos un evento de GA4 sin mas cada vez que
   el codigo Python pasa por esa linea, cada rerun duplicaria el evento — un
   page_view por cada clic, un "team_viewed" por cada rerender de la pagina de
   equipos, etc. La solucion: cada evento de "vista" se emite con una clave de
   deduplicacion; en el navegador guardamos en `window.parent.__gaLastByKey` el
   ultimo valor mandado para esa clave, y si el rerun actual pide mandar
   exactamente lo mismo que la ultima vez, no se manda otra vez. Si el valor
   cambia (otra pagina, otro equipo...) si que se manda, una sola vez por cambio
   real. Los eventos de "accion" (p.ej. share_result) no llevan esta
   deduplicacion — ver _gtag_event_now.

Nada de esto llega a JavaScript si GOOGLE_ANALYTICS_ID no esta configurado: todas las
funciones de aqui son no-op (no crean ningun iframe, no pueden lanzar un error)
mientras env.ANALYTICS_ENABLED sea False. Ver env.py y components/head_tags.py.

Privacidad: los parametros que aceptan estas funciones son siempre datos de contenido
publico de la app (equipo, jugador, nivel de quiz, tipo de contenido compartido...),
nunca nombres, emails, IPs ni ningun otro dato personal de quien visita el sitio.
"""

import json

import streamlit.components.v1 as components

import env


def _gtag_event(dedup_key, event_name, params=None):
    """Para eventos de "vista" (page_view, team_viewed...): empuja el evento al
    dataLayer solo cuando (event_name, params) cambia respecto a la ultima vez para
    esa dedup_key. Evita que un rerun no relacionado (mover el selector de temporada,
    pulsar un boton interno...) reenvie el mismo "vista de X" otra vez. No hace nada
    si Analytics esta desactivado."""
    if not env.ANALYTICS_ENABLED:
        return
    payload = json.dumps(params or {}, ensure_ascii=False)
    components.html(
        f"""<script>
(function() {{
  window.parent.__gaLastByKey = window.parent.__gaLastByKey || {{}};
  var k = {json.dumps(dedup_key)};
  var v = {json.dumps(event_name)} + ":" + {json.dumps(payload)};
  if (window.parent.__gaLastByKey[k] !== v) {{
    window.parent.__gaLastByKey[k] = v;
    window.parent.dataLayer = window.parent.dataLayer || [];
    window.parent.dataLayer.push(['event', {json.dumps(event_name)}, {payload}]);
  }}
}})();
</script>""",
        height=0,
    )


def _gtag_event_now(event_name, params=None):
    """Para eventos de "accion" (share_result...): empuja el evento al dataLayer sin
    deduplicar por valor. Solo debe llamarse desde un punto del codigo que Streamlit ya
    ejecuta una vez por accion real (p.ej. dentro de un `if st.button(...):`) — ahi
    deduplicar por valor seria incorrecto, porque compartir el mismo contenido dos
    veces seguidas son dos eventos reales, no una repeticion del mismo rerun."""
    if not env.ANALYTICS_ENABLED:
        return
    payload = json.dumps(params or {}, ensure_ascii=False)
    components.html(
        f"""<script>
window.parent.dataLayer = window.parent.dataLayer || [];
window.parent.dataLayer.push(['event', {json.dumps(event_name)}, {payload}]);
</script>""",
        height=0,
    )


def track_page_view(page_key, page_title):
    """Pagina/seccion vista. Se llama una vez por rerun desde panel_nfl.py; gracias a
    la deduplicacion por (page_key, page_title) solo genera un evento GA4 real cuando
    el usuario cambia de pagina, no en cada rerun dentro de la misma pagina (mover el
    selector de temporada, pulsar un boton interno, etc.)."""
    _gtag_event("page_view", "page_view", {
        "page_title": page_title,
        "page_path": f"/{page_key}",
    })


def track_quiz_completed(level, score, total, attempt):
    """attempt: contador que sube cada vez que se empieza una partida nueva (ver
    pages_app/quiz.py::_reset). Sin el, repetir el quiz y sacar la misma puntuacion
    no generaria un segundo evento, porque (level, score, total) seria identico al de
    la partida anterior."""
    _gtag_event("quiz_completed", "quiz_completed", {
        "level": str(level), "score": int(score), "total": int(total), "attempt": int(attempt),
    })


def track_team_viewed(team):
    _gtag_event("team_viewed", "team_viewed", {"team": str(team)})


def track_player_viewed(player):
    _gtag_event("player_viewed", "player_viewed", {"player": str(player)})


def track_matchup_viewed(team_home, team_away):
    _gtag_event("matchup_viewed", "matchup_viewed", {
        "team_home": str(team_home), "team_away": str(team_away),
    })


def track_laboratory_viewed():
    _gtag_event("laboratory_viewed", "laboratory_viewed")


def track_trend_viewed():
    _gtag_event("trend_viewed", "trend_viewed")


def track_football_iq_viewed():
    _gtag_event("football_iq_viewed", "football_iq_viewed")


def track_share_result(content_type):
    """content_type: p.ej. "quiz", "team", "player" — que tipo de tarjeta se ha
    generado para compartir. Debe llamarse solo dentro del `if st.button(...)` que
    genera la imagen: ese bloque ya ocurre una sola vez por clic real, y aqui NO se
    deduplica por valor porque compartir el mismo tipo de contenido dos veces seguidas
    son dos eventos reales distintos."""
    _gtag_event_now("share_result", {"content_type": str(content_type)})
