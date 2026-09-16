"""components/footer.py — pie de pagina con el contacto del canal."""

import streamlit as st

import nfl_graficos as G

REDES = {
    "TikTok":    "https://www.tiktok.com/@elplaybooknfl",
    "Instagram": "https://www.instagram.com/elplaybooknfl",
    "YouTube":   "https://www.youtube.com/@elplaybooknfl",
    "Contacto":  "mailto:elplaybooknfl@gmail.com",
}


def render(logo_b64):
    links = "".join(f'<a href="{u}" target="_blank">{n}</a>' for n, u in REDES.items())
    st.markdown(f"""
    <div class="site-footer">
      <div class="footer-brand"><img src="data:image/png;base64,{logo_b64}"/><span>EL PLAYBOOK NFL</span></div>
      <div class="footer-links">{links}</div>
      <div class="footer-meta">{G.CANAL} · Datos: nflverse · Hecho con Streamlit</div>
    </div>
    """, unsafe_allow_html=True)
