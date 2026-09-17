"""components/head_tags.py — inyeccion opcional de Analytics/Search Console/AdSense.

Streamlit no expone el <head> real del documento: lo que se inyecta aqui via
st.markdown(unsafe_allow_html=True) aterriza en el DOM de la app, no en un
<head> HTML tradicional. Para gtag.js (Analytics) y el script de AdSense esto
funciona igual (son scripts que se ejecutan, no dependen de estar en <head>).
Para lo que SI exige estar servido en la raiz del dominio (ads.txt, archivos
HTML de verificacion de Search Console) hace falta el reverse proxy delante
de Streamlit — ver DEPLOY.md.

Todo lo de aqui es no-op mientras las variables de entorno correspondientes
no esten definidas: sin configuracion, esta funcion devuelve "" y no se
inyecta nada.
"""

import env


def head_injection_html():
    parts = []

    if env.GOOGLE_SITE_VERIFICATION:
        parts.append(
            f'<meta name="google-site-verification" content="{env.GOOGLE_SITE_VERIFICATION}">'
        )

    if env.ANALYTICS_ENABLED:
        gid = env.GOOGLE_ANALYTICS_ID
        parts.append(f"""
          <script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>
          <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{ dataLayer.push(arguments); }}
            gtag('js', new Date());
            gtag('config', '{gid}');
          </script>""")

    if env.ADSENSE_ENABLED:
        parts.append(
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={env.GOOGLE_ADSENSE_PUBLISHER_ID}" crossorigin="anonymous"></script>'
        )

    return "\n".join(parts)
