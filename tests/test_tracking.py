"""tests/test_tracking.py — comprobaciones de la integracion de Google Analytics 4.

Cubre lo pedido al integrar GA4:
  1. La app no se rompe si GOOGLE_ANALYTICS_ID no esta configurado.
  2. El Measurement ID configurado se usa correctamente en el script inyectado.
  3. Los eventos no llevan ningun dato personal (solo las claves permitidas).
  4. No hay duplicacion evidente del tracking (misma vista -> mismo "valor" de
     deduplicacion; vista distinta -> valor distinto; y los eventos de accion como
     share_result no llevan por error el guard de deduplicacion de las vistas).

Todas las funciones de components/tracking.py y components/head_tags.py renderizan
via streamlit.components.v1.html (un iframe real — necesario para que el JS se
ejecute de verdad, ver el docstring de components/tracking.py). Aqui se intercepta
esa llamada para capturar el HTML/JS generado sin necesitar un navegador ni una app
de Streamlit corriendo.
"""

import json
import re
from unittest.mock import patch

import env
from components import head_tags, tracking

# dataLayer.push(['event', "<name>", <json>]) — capturamos nombre y payload.
_DATALAYER_EVENT_RE = re.compile(
    r"dataLayer\.push\(\['event',\s*\"([^\"]+)\",\s*(\{.*?\})\]\);"
)

# Claves permitidas por evento — esto ES la lista blanca de PII: cualquier parametro
# nuevo que se añada a un evento y no este aqui hara fallar test_no_pii_in_events.
ALLOWED_PARAMS = {
    "page_view": {"page_title", "page_path"},
    "quiz_completed": {"level", "score", "total", "attempt"},
    "team_viewed": {"team"},
    "player_viewed": {"player"},
    "matchup_viewed": {"team_home", "team_away"},
    "laboratory_viewed": set(),
    "trend_viewed": set(),
    "football_iq_viewed": set(),
    "share_result": {"content_type"},
}

# Fragmentos que jamas deberian aparecer como clave de un parametro de evento.
PII_KEY_SUBSTRINGS = [
    "email", "e_mail", "correo", "ip", "phone", "telefono", "address", "direccion",
    "user_id", "uid", "session", "password", "contrasena", "token", "dni", "nif",
    "apellido", "lastname", "surname", "birth", "nacimiento",
]


def _enable_analytics(monkeypatch, ga_id="G-TEST1234X"):
    monkeypatch.setattr(env, "GOOGLE_ANALYTICS_ID", ga_id)
    monkeypatch.setattr(env, "ANALYTICS_ENABLED", True)
    monkeypatch.setattr(tracking.env, "GOOGLE_ANALYTICS_ID", ga_id)
    monkeypatch.setattr(tracking.env, "ANALYTICS_ENABLED", True)
    monkeypatch.setattr(head_tags.env, "GOOGLE_ANALYTICS_ID", ga_id)
    monkeypatch.setattr(head_tags.env, "ANALYTICS_ENABLED", True)


def _captured_scripts(calls):
    """Ejecuta `calls` (funciones sin argumentos) e intercepta cada llamada a
    components.html en components/tracking.py, devolviendo la lista de HTML/JS
    generados en orden."""
    scripts = []
    with patch("components.tracking.components.html",
               side_effect=lambda html, **kw: scripts.append(html)):
        for call in calls:
            call()
    return scripts


def _captured_events(calls):
    events = []
    for html in _captured_scripts(calls):
        m = _DATALAYER_EVENT_RE.search(html)
        assert m, f"no se encontro un dataLayer.push(['event', ...]) en el script:\n{html}"
        name, payload_str = m.group(1), m.group(2)
        events.append((name, json.loads(payload_str)))
    return events


# --- 1. GA4 no rompe la app cuando no hay Measurement ID ------------------------

def test_head_injection_is_empty_without_id(monkeypatch):
    monkeypatch.setattr(env, "GOOGLE_ANALYTICS_ID", "")
    monkeypatch.setattr(env, "ANALYTICS_ENABLED", False)
    assert head_tags.head_injection_html() == ""


def test_inject_head_scripts_is_noop_without_id(monkeypatch):
    monkeypatch.setattr(head_tags.env, "GOOGLE_ANALYTICS_ID", "")
    monkeypatch.setattr(head_tags.env, "ANALYTICS_ENABLED", False)
    monkeypatch.setattr(head_tags.env, "ADSENSE_ENABLED", False)
    with patch("components.head_tags.components.html") as html_mock:
        head_tags.inject_head_scripts()
    html_mock.assert_not_called()  # sin ID no se crea ni un iframe


def test_tracking_functions_are_noop_without_id(monkeypatch):
    monkeypatch.setattr(tracking.env, "GOOGLE_ANALYTICS_ID", "")
    monkeypatch.setattr(tracking.env, "ANALYTICS_ENABLED", False)
    with patch("components.tracking.components.html") as html_mock:
        tracking.track_page_view("home", "Inicio")
        tracking.track_team_viewed("KC")
        tracking.track_player_viewed("Josh Allen")
        tracking.track_matchup_viewed("KC", "BUF")
        tracking.track_laboratory_viewed()
        tracking.track_trend_viewed()
        tracking.track_football_iq_viewed()
        tracking.track_quiz_completed("rookie", 3, 5, 1)
        tracking.track_share_result("quiz")
    html_mock.assert_not_called()  # nada se inyecta: cero riesgo de romper la app


# --- 2. El Measurement ID configurado se usa correctamente -----------------------

def test_inject_head_scripts_uses_configured_id(monkeypatch):
    # ID de formato realista pero inventado a proposito — no hace falta un
    # Measurement ID real para probar que la sustitucion funciona.
    test_id = "G-TESTID1234"
    monkeypatch.setattr(head_tags.env, "GOOGLE_ANALYTICS_ID", test_id)
    monkeypatch.setattr(head_tags.env, "ANALYTICS_ENABLED", True)
    monkeypatch.setattr(head_tags.env, "ADSENSE_ENABLED", False)
    scripts = []
    with patch("components.head_tags.components.html",
               side_effect=lambda html, **kw: scripts.append(html)):
        head_tags.inject_head_scripts()
    assert len(scripts) == 1
    html = scripts[0]
    assert test_id in html
    assert f"googletagmanager.com/gtag/js?id={test_id}" in html
    assert f"'config', '{test_id}'" in html
    # El page_view automatico de gtag va desactivado: lo manda track_page_view.
    assert "send_page_view: false" in html
    # Debe escribir en la pagina real (window.parent), no en el propio iframe.
    assert "window.parent.dataLayer" in html
    assert "window.dataLayer" not in html.replace("window.parent.dataLayer", "")


# --- 3. Los eventos no contienen informacion personal -----------------------------

def test_no_pii_in_events(monkeypatch):
    _enable_analytics(monkeypatch)
    events = _captured_events([
        lambda: tracking.track_page_view("jugadores", "Jugadores"),
        lambda: tracking.track_team_viewed("KC"),
        lambda: tracking.track_player_viewed("Josh Allen"),
        lambda: tracking.track_matchup_viewed("KC", "BUF"),
        lambda: tracking.track_laboratory_viewed(),
        lambda: tracking.track_trend_viewed(),
        lambda: tracking.track_football_iq_viewed(),
        lambda: tracking.track_quiz_completed("rookie", 3, 5, 1),
        lambda: tracking.track_share_result("quiz"),
    ])
    assert len(events) == 9
    for name, params in events:
        assert name in ALLOWED_PARAMS, f"evento no documentado en ALLOWED_PARAMS: {name}"
        allowed = ALLOWED_PARAMS[name]
        assert set(params.keys()) <= allowed, (
            f"{name} manda parametros fuera de la lista blanca: {set(params) - allowed}")
        for key, value in params.items():
            low = key.lower()
            assert not any(bad in low for bad in PII_KEY_SUBSTRINGS), (
                f"{name}.{key} parece un dato personal, no deberia mandarse a GA4")
            assert isinstance(value, (str, int, float)), (
                f"{name}.{key} no es un valor simple (str/int/float): {value!r}")


def test_pii_blocklist_catches_bad_params():
    """Verifica que el propio blocklist funciona (no es una lista vacia sin efecto)."""
    assert any("email" in bad for bad in PII_KEY_SUBSTRINGS)
    low = "user_email"
    assert any(bad in low for bad in PII_KEY_SUBSTRINGS)


# --- 4. No hay duplicacion evidente del tracking ----------------------------------

def test_page_view_same_page_has_stable_dedup_value(monkeypatch):
    """Dos renders seguidos de la MISMA pagina deben producir el mismo "valor" de
    deduplicacion (para que el guard de JS en el navegador los trate como iguales y
    no mande el evento dos veces)."""
    _enable_analytics(monkeypatch)
    scripts = _captured_scripts([
        lambda: tracking.track_page_view("home", "Inicio"),
        lambda: tracking.track_page_view("home", "Inicio"),
    ])
    assert len(scripts) == 2
    assert scripts[0] == scripts[1]  # mismo html -> misma clave "v" en el guard de JS
    assert "window.parent.__gaLastByKey" in scripts[0]


def test_page_view_different_page_has_different_dedup_value(monkeypatch):
    _enable_analytics(monkeypatch)
    scripts = _captured_scripts([
        lambda: tracking.track_page_view("home", "Inicio"),
        lambda: tracking.track_page_view("clasificacion", "Clasificación"),
    ])
    assert scripts[0] != scripts[1]


def test_view_events_use_dedup_guard_action_events_do_not(monkeypatch):
    """Los eventos de "vista" deben llevar el guard de deduplicacion por valor; los de
    "accion" (share_result) deben mandarse siempre que se llaman, sin deduplicar,
    porque ya estan detras de un `if st.button(...)` que solo se ejecuta una vez por
    clic real — deduplicar ahi silenciaria una segunda accion real identica."""
    _enable_analytics(monkeypatch)
    team_html, share_html = _captured_scripts([
        lambda: tracking.track_team_viewed("KC"),
        lambda: tracking.track_share_result("quiz"),
    ])
    assert "__gaLastByKey" in team_html
    assert "__gaLastByKey" not in share_html


def test_quiz_completed_dedup_key_includes_attempt(monkeypatch):
    """Sin el numero de intento, repetir el quiz y sacar la misma puntuacion no
    generaria un segundo evento (mismo (level, score, total) que la vez anterior)."""
    _enable_analytics(monkeypatch)
    scripts = _captured_scripts([
        lambda: tracking.track_quiz_completed("rookie", 3, 5, attempt=1),
        lambda: tracking.track_quiz_completed("rookie", 3, 5, attempt=2),
    ])
    assert scripts[0] != scripts[1]


def test_events_target_parent_window_not_iframe(monkeypatch):
    """Cada llamada de tracking crea su propio iframe — si escribieramos en
    `window.dataLayer` a secas (el del iframe) en vez de `window.parent.dataLayer`,
    el evento se perderia porque nadie lee el dataLayer de un iframe descartado."""
    _enable_analytics(monkeypatch)
    [html] = _captured_scripts([lambda: tracking.track_team_viewed("KC")])
    assert "window.parent.dataLayer" in html
    assert "window.dataLayer" not in html.replace("window.parent.dataLayer", "")
