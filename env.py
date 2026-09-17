"""env.py — unico punto de lectura de configuracion por variables de entorno.

Nada de esto es obligatorio: cada variable tiene un valor por defecto
razonable (o vacio) y la app arranca y funciona igual sin ningun .env.
Ver .env.example para la lista completa con comentarios.
"""

import os


def _env(name, default=""):
    return os.environ.get(name, default).strip()


ENVIRONMENT = _env("APP_ENV", "development")

# --- Identidad del sitio (SEO, paginas legales, verificacion de dominio) ---
SITE_NAME = "El Playbook NFL"
SITE_URL = _env("SITE_URL", "https://elplaybooknfl.com")
CONTACT_EMAIL = _env("CONTACT_EMAIL", "elplaybooknfl@gmail.com")

# --- Google Analytics (GA4) ---
# Vacio por defecto: no se inyecta ningun script de analytics hasta que se
# defina GOOGLE_ANALYTICS_ID (formato "G-XXXXXXXXXX").
GOOGLE_ANALYTICS_ID = _env("GOOGLE_ANALYTICS_ID")
ANALYTICS_ENABLED = bool(GOOGLE_ANALYTICS_ID)

# --- Google Search Console (verificacion por meta tag) ---
# Alternativa a subir un archivo HTML de verificacion (ver DEPLOY.md para
# esa opcion, que debe servirla el reverse proxy, no Streamlit).
GOOGLE_SITE_VERIFICATION = _env("GOOGLE_SITE_VERIFICATION")

# --- Google AdSense ---
# Deshabilitado por defecto (cadena vacia). NUNCA se debe poner aqui un ID
# de ejemplo/inventado: hasta que GOOGLE_ADSENSE_PUBLISHER_ID tenga un
# valor real (formato "pub-XXXXXXXXXXXXXXXX"), la app no inyecta ningun
# script ni muestra ningun hueco publicitario.
GOOGLE_ADSENSE_PUBLISHER_ID = _env("GOOGLE_ADSENSE_PUBLISHER_ID")
ADSENSE_ENABLED = bool(GOOGLE_ADSENSE_PUBLISHER_ID)
