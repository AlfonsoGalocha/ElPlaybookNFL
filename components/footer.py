"""components/footer.py — pie de pagina con el contacto del canal y enlaces legales."""

import streamlit as st

import nfl_graficos as G
from components.navbar import TIKTOK_URL, go_to

REDES = {
    "TikTok":    TIKTOK_URL,
    "Instagram": "https://www.instagram.com/elplaybooknfl",
    "Contacto":  TIKTOK_URL,
}

LEGAL_LINKS = [
    ("aviso", "Aviso legal"),
    ("privacidad", "Privacidad"),
    ("cookies", "Cookies"),
    ("sobre", "Sobre nosotros"),
]


def render(logo_b64):
    links = "".join(f'<a href="{u}" target="_blank">{n}</a>' for n, u in REDES.items())
    st.markdown(f"""
    <div class="site-footer">
      <div class="footer-brand"><img src="data:image/png;base64,{logo_b64}"/><span>EL PLAYBOOK NFL</span></div>
      <div class="footer-links">{links}</div>
      <div class="footer-meta">{G.CANAL} · Datos: nflverse · Hecho con Streamlit</div>
    </div>
    """, unsafe_allow_html=True)

    legal_cols = st.columns(len(LEGAL_LINKS))
    for col, (key, label) in zip(legal_cols, LEGAL_LINKS):
        with col:
            if st.button(label, key=f"footer_legal_{key}", use_container_width=True):
                go_to("legal", legal_section=key)
