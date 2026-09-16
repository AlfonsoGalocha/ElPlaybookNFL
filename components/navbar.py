"""components/navbar.py — cabecera con marca, navegacion (2 filas) y selector de temporada."""

import streamlit as st

PAGES_PRIMARY = [
    ("home", "🏠 Inicio"),
    ("equipos", "🏟️ Equipos"),
    ("clasificacion", "📋 Clasificación"),
    ("rankings", "🏆 Rankings"),
    ("jugadores", "👤 Jugadores"),
]

PAGES_SECONDARY = [
    ("laboratorio", "🔬 Laboratorio"),
    ("tendencias", "📈 Tendencias"),
    ("matchups", "⚔️ Matchups"),
    ("comparar", "📊 Comparar"),
    ("football_iq", "🎓 Football IQ"),
    ("quiz", "🧠 Quiz"),
]

PAGES = PAGES_PRIMARY + PAGES_SECONDARY
DEFAULT_PAGE = "home"
SEASON_RANGE = list(range(2026, 1998, -1))


def _nav_row(items):
    cols = st.columns(len(items))
    for col, (key, label) in zip(cols, items):
        with col:
            active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()


def render(logo_b64):
    """Dibuja la navbar (marca + temporada + 2 filas de navegacion) y devuelve la temporada elegida."""
    if "page" not in st.session_state:
        st.session_state.page = DEFAULT_PAGE

    nav_l, nav_c, nav_r = st.columns([2.1, 5.9, 1.0], vertical_alignment="center")
    with nav_l:
        st.markdown(
            f'<div class="nav-brand"><img src="data:image/png;base64,{logo_b64}"/>'
            f'EL PLAYBOOK <span class="nfl">NFL</span></div>', unsafe_allow_html=True)
    with nav_c:
        _nav_row(PAGES_PRIMARY)
    with nav_r:
        season = st.selectbox("Temporada", SEASON_RANGE, index=0, label_visibility="collapsed")

    _nav_row(PAGES_SECONDARY)
    return season


def go_to(page, **extra_state):
    """Navega a otra pagina desde codigo (p.ej. al pulsar un jugador en la plantilla de un equipo)."""
    st.session_state.page = page
    for k, v in extra_state.items():
        st.session_state[k] = v
    st.rerun()
