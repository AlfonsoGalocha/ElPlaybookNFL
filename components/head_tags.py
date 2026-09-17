"""components/head_tags.py — inyeccion opcional de Analytics/Search Console/AdSense.

Streamlit no expone el <head> real del documento: lo que se inyecta aqui aterriza en
el DOM de la app, no en un <head> HTML tradicional. Para una <meta> (Search Console)
eso da igual — no necesita "ejecutarse", con que exista en el DOM basta. Pero para
scripts (gtag.js de Analytics, el loader de AdSense) SI importa, y de una forma nada
obvia:

Un <script> insertado via st.markdown(unsafe_allow_html=True) usa
dangerouslySetInnerHTML por debajo, y el HTML Standard dice explicitamente que los
<script> metidos asi (via innerHTML) NUNCA se ejecutan — quedan "inertes" en el DOM,
visibles pero sin efecto. Esto se confirmo probandolo en vivo: el script se veia en
el DOM pero window.dataLayer nunca se creaba y el navegador nunca pedia gtag.js.

La unica forma de ejecutar JS de verdad desde Streamlit es un iframe real
(streamlit.components.v1.html) — un iframe SI ejecuta su contenido, y al ser
same-origin con la app puede escribir en `window.parent` (la pagina real, no el
iframe). Por eso `inject_head_scripts()` usa components.html() en vez de
st.markdown(), y por eso escribe siempre en `window.parent.dataLayer`, nunca en
`window.dataLayer` a secas (ese seria el dataLayer del iframe, que nadie lee).

Todo lo de aqui es no-op mientras las variables de entorno correspondientes no esten
definidas: sin configuracion no se inyecta nada ni se crea ningun iframe.
"""

import streamlit.components.v1 as components

import env


def head_injection_html():
    """Metaetiquetas puras (sin <script>) para pasar a st.markdown(). No necesitan
    ejecutarse — con estar presentes en el DOM basta (ver docstring del modulo)."""
    parts = []
    if env.GOOGLE_SITE_VERIFICATION:
        parts.append(
            f'<meta name="google-site-verification" content="{env.GOOGLE_SITE_VERIFICATION}">'
        )
    return "\n".join(parts)


def inject_head_scripts():
    """Carga gtag.js (Analytics) y/o el loader de AdSense, si estan configurados.
    Renderiza un iframe invisible (height=0) con streamlit.components.v1.html — ver
    el docstring del modulo para por que hace falta un iframe y no basta con
    st.markdown(). Debe llamarse una vez por rerun, cerca del principio de la app."""
    if not (env.ANALYTICS_ENABLED or env.ADSENSE_ENABLED):
        return

    script = ""

    if env.ANALYTICS_ENABLED:
        # TODO(consentimiento): esto activa GA4 en cuanto GOOGLE_ANALYTICS_ID esta
        # configurado, sin pedir consentimiento de cookies analiticas al usuario. Hoy
        # el proyecto no tiene ningun banner/gestor de consentimiento (ver DEPLOY.md,
        # seccion "Analytics (Google Analytics 4)") — no actives esta variable en
        # produccion con trafico real de la UE hasta que exista uno. Cuando lo haya,
        # esta condicion debe pasar a ser
        # `if (env.ANALYTICS_ENABLED or env.ADSENSE_ENABLED) and user_has_consented():`.
        gid = env.GOOGLE_ANALYTICS_ID
        script += f"""
        (function() {{
          var d = window.parent.document;
          window.parent.dataLayer = window.parent.dataLayer || [];
          if (!d.querySelector('script[data-ga4-loaded]')) {{
            var s = d.createElement('script');
            s.async = true;
            s.src = 'https://www.googletagmanager.com/gtag/js?id={gid}';
            s.setAttribute('data-ga4-loaded', '1');
            d.head.appendChild(s);
            // send_page_view:false — el page_view "de verdad" para esta app lo manda
            // components/tracking.py::track_page_view en cada cambio de pagina, ya
            // que Streamlit no cambia la URL del navegador al navegar entre
            // secciones (el automatico de gtag siempre reportaria la misma
            // page_path: "/"). Empujamos directo al dataLayer (en vez de esperar a
            // que exista window.gtag) porque este es el patron de cola que gtag.js
            // procesa en cuanto termina de cargar, sin depender de en que orden
            // ejecuten los distintos iframes de esta pagina.
            window.parent.dataLayer.push(['js', new Date()]);
            window.parent.dataLayer.push(['config', '{gid}', {{ send_page_view: false }}]);
          }}
        }})();
        """

    if env.ADSENSE_ENABLED:
        script += f"""
        (function() {{
          var d = window.parent.document;
          if (!d.querySelector('script[data-adsense-loaded]')) {{
            var s = d.createElement('script');
            s.async = true;
            s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
                    + '?client={env.GOOGLE_ADSENSE_PUBLISHER_ID}';
            s.crossOrigin = 'anonymous';
            s.setAttribute('data-adsense-loaded', '1');
            d.head.appendChild(s);
          }}
        }})();
        """

    components.html(f"<script>{script}</script>", height=0)
