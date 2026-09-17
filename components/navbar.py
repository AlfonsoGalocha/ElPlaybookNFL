"""components/navbar.py — cabecera con marca, navegacion principal (5 pestañas fijas), menu
de herramientas (st.popover), enlace a TikTok y selector de temporada, todo en una sola fila."""

import streamlit as st

TIKTOK_URL = "https://www.tiktok.com/@elplaybook_nfl"

PAGES_PRIMARY = [
    ("home", "🏠 Inicio"),
    ("clasificacion", "📊 Clasificación"),
    ("rankings", "🏆 Rankings"),
    ("matchups", "⚔️ Matchups"),
    ("laboratorio", "🧪 Laboratorio"),
]

PAGES_TOOLS = [
    ("weekly", "📰 Weekly"),
    ("equipos", "🏟️ Equipos"),
    ("jugadores", "👤 Jugadores"),
    ("tendencias", "📈 Tendencias"),
    ("partido", "🏈 Partido"),
    ("comparar", "📊 Comparar"),
    ("football_iq", "🎓 Football IQ"),
    ("quiz", "🧠 Quiz"),
]

PAGES = PAGES_PRIMARY + PAGES_TOOLS
TOOLS_KEYS = {key for key, _ in PAGES_TOOLS}
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


def _tools_menu():
    current = st.session_state.page
    active_label = next((label for key, label in PAGES_TOOLS if key == current), None)
    trigger = active_label or "🛠️ Más"
    with st.popover(trigger, use_container_width=True):
        st.caption("🛠️ Herramientas y análisis")
        for key, label in PAGES_TOOLS:
            active = current == key
            if st.button(label, key=f"nav_tool_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()


def render(logo_b64):
    """Dibuja la navbar (marca + 5 pestañas principales + herramientas + TikTok + temporada)
    en una sola fila y devuelve la temporada elegida."""
    if "page" not in st.session_state:
        st.session_state.page = DEFAULT_PAGE

    nav_l, nav_c, nav_t, nav_tt, nav_r = st.columns(
        [2.05, 5.75, 0.85, 0.4, 0.85], vertical_alignment="center")
    with nav_l:
        st.markdown(
            f'<div class="nav-brand"><img src="data:image/png;base64,{logo_b64}"/>'
            f'EL PLAYBOOK <span class="nfl">NFL</span></div>', unsafe_allow_html=True)
    with nav_c:
        _nav_row(PAGES_PRIMARY)
    with nav_t:
        _tools_menu()
    with nav_tt:
        st.link_button("🎵", TIKTOK_URL, use_container_width=True, help="Síguenos en TikTok")
    with nav_r:
        season = st.selectbox("Temporada", SEASON_RANGE, index=0, label_visibility="collapsed")

    return season


def go_to(page, **extra_state):
    """Navega a otra pagina desde codigo (p.ej. al pulsar un jugador en la plantilla de un equipo)."""
    st.session_state.page = page
    for k, v in extra_state.items():
        st.session_state[k] = v
    st.rerun()
