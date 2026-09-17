"""pages_app/football_iq.py — glosario educativo por niveles (Rookie / Aficionado / Avanzado)."""

import streamlit as st

from components.tracking import track_football_iq_viewed
from content.football_iq_data import LEVEL_ORDER, LEVELS


def _term_card(t, i):
    return (
        f'<div class="term-card fade-up d{min(i, 9)}">'
        f'<div class="tc-term">{t["term"]}</div>'
        f'<div class="tc-def">{t["def"]}</div>'
        f'<div class="tc-example">💡 {t["example"]}</div>'
        f'</div>'
    )


def render(ctx):
    st.markdown('<div class="sect-title">Football IQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Entiende la NFL de verdad, no solo la sigas. Elige tu nivel.</div>',
                unsafe_allow_html=True)
    track_football_iq_viewed()

    if "iq_level" not in st.session_state:
        st.session_state.iq_level = "rookie"

    cols = st.columns(len(LEVEL_ORDER))
    for col, key in zip(cols, LEVEL_ORDER):
        with col:
            active = st.session_state.iq_level == key
            if st.button(LEVELS[key]["title"], key=f"iq_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.iq_level = key
                st.rerun()

    level = LEVELS[st.session_state.iq_level]
    st.markdown(f'<span class="iq-level-tag {level["css"]}">{level["title"].upper()}</span>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="sect-sub" style="margin-top:-.4rem">{level["tagline"]}</div>',
                unsafe_allow_html=True)

    cols = st.columns(2)
    for i, term in enumerate(level["terms"]):
        with cols[i % 2]:
            st.markdown(_term_card(term, i), unsafe_allow_html=True)

    if st.session_state.iq_level == "avanzado":
        st.info("Estas métricas son las mismas que usamos en 🔬 Laboratorio, calculadas con datos "
                "reales de la temporada. Ve para allá y verás los números detrás de cada una.")

    st.markdown("#### 🧠 ¿Quieres ponerte a prueba?")
    if st.button("Ir al Quiz de este nivel", type="primary"):
        st.session_state.quiz_level = st.session_state.iq_level
        st.session_state.page = "quiz"
        st.rerun()
