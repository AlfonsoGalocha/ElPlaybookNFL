"""pages_app/quiz.py — quiz de NFL por nivel: preguntas, explicacion, puntuacion y compartir."""

import streamlit as st

from content.quiz_bank import LEVEL_LABELS, QUESTIONS
from share.cards import quiz_result_card


def _reset(level):
    st.session_state.quiz_level = level
    st.session_state.quiz_idx = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = {}


def _level_picker():
    st.markdown('<div class="sect-sub">Elige un nivel para empezar.</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, key in zip(cols, ["rookie", "aficionado", "avanzado"]):
        with col:
            if st.button(LEVEL_LABELS[key], key=f"quizlvl_{key}", use_container_width=True, type="primary"):
                _reset(key)
                st.rerun()


def render(ctx):
    st.markdown('<div class="sect-title">Quiz</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Pon a prueba lo que sabes de la NFL.</div>', unsafe_allow_html=True)

    if "quiz_level" not in st.session_state or st.session_state.quiz_level not in QUESTIONS:
        _level_picker()
        return

    level = st.session_state.quiz_level
    questions = QUESTIONS[level]
    idx = st.session_state.get("quiz_idx", 0)

    if idx >= len(questions):
        score = st.session_state.get("quiz_score", 0)
        total = len(questions)
        st.markdown(f"""
          <div class="quiz-card" style="text-align:center">
            <div class="conf-h" style="margin-top:0">{LEVEL_LABELS[level]}</div>
            <div class="quiz-score">{score}/{total}</div>
            <div class="sect-sub">respuestas correctas</div>
          </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        if c1.button("🔁 Repetir", use_container_width=True):
            _reset(level)
            st.rerun()
        if c2.button("⬆️ Cambiar de nivel", use_container_width=True):
            for k in ("quiz_level", "quiz_idx", "quiz_score", "quiz_answers"):
                st.session_state.pop(k, None)
            st.rerun()
        with c3:
            if st.button("📤 Generar imagen para compartir", use_container_width=True, type="primary"):
                with st.spinner("Generando..."):
                    png = quiz_result_card(LEVEL_LABELS[level], score, total)
                st.image(png, width=280)
                st.download_button("⬇️ Descargar PNG", png,
                                   file_name=f"quiz_{level}_{score}de{total}.png", mime="image/png")
        return

    q = questions[idx]
    answered = idx in st.session_state.get("quiz_answers", {})

    st.markdown(f'<span class="iq-level-tag iq-{"rookie" if level == "rookie" else level}">'
                f'{LEVEL_LABELS[level].upper()} · PREGUNTA {idx + 1}/{len(questions)}</span>',
                unsafe_allow_html=True)
    st.markdown(f"### {q['q']}")

    choice = st.radio("Opciones", q["options"], index=None, key=f"quiz_choice_{level}_{idx}",
                       label_visibility="collapsed", disabled=answered)

    if not answered:
        if st.button("Responder", type="primary", disabled=choice is None):
            chosen_idx = q["options"].index(choice)
            correct = chosen_idx == q["correct"]
            st.session_state.setdefault("quiz_answers", {})[idx] = chosen_idx
            if correct:
                st.session_state.quiz_score = st.session_state.get("quiz_score", 0) + 1
            st.rerun()
    else:
        chosen_idx = st.session_state.quiz_answers[idx]
        if chosen_idx == q["correct"]:
            st.success(f"✅ ¡Correcto! {q['explain']}")
        else:
            st.error(f"❌ La respuesta correcta era **{q['options'][q['correct']]}**. {q['explain']}")
        if st.button("Siguiente →", type="primary"):
            st.session_state.quiz_idx = idx + 1
            st.rerun()
