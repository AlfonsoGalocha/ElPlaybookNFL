"""components/explanation.py — bloque "¿Por qué?" reutilizable: desglose deterministico de
una métrica en sus componentes dentro de un expander de Streamlit. No hace nada si no hay
datos suficientes (breakdown None) — nunca inventa un desglose.
"""

import streamlit as st


def why_expander(breakdown, insight, decimals=2, label="¿Por qué?"):
    if breakdown is None:
        return
    with st.expander(f"🔍 {label}"):
        total_row = (f'<div class="why-row" style="font-weight:600">'
                     f'<span class="why-label">EPA/jugada total (pase + carrera)</span>'
                     f'<span class="why-value">{breakdown["total"]:+.{decimals}f}</span></div>')
        rows = "".join(
            f'<div class="why-row"><span class="why-label">{lbl}</span>'
            f'<span class="why-value">{val:+.{decimals}f}</span></div>'
            for lbl, val in breakdown["components"]
        )
        insight_html = f'<div class="sxc-insight" style="margin-top:8px">🧠 {insight}</div>' if insight else ""
        st.markdown(f'<div class="why-box">{total_row}{rows}{insight_html}</div>', unsafe_allow_html=True)
