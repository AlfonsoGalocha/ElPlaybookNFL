"""pages_app/legal.py — paginas informativas (legal, privacidad, cookies, contacto,
sobre nosotros). Contenido real donde ya lo tenemos (que es la web, contacto publico
existente); el resto son placeholders claramente marcados para completar mas adelante
— no se inventa ningun dato legal/personal.
"""

import streamlit as st

import env
from components.footer import REDES

SECTIONS = [
    ("aviso", "Aviso legal"),
    ("privacidad", "Privacidad"),
    ("cookies", "Cookies"),
    ("contacto", "Contacto"),
    ("sobre", "Sobre nosotros"),
]

PLACEHOLDER = "⚠️ *[Pendiente de completar — placeholder, no es información real todavía]*"


def _aviso():
    st.markdown(f"""
#### 1. Titularidad del sitio
{PLACEHOLDER}

- **Titular / razón social:** [completar]
- **NIF / CIF:** [completar]
- **Domicilio:** [completar]
- **Email de contacto:** {env.CONTACT_EMAIL}

#### 2. Objeto
{env.SITE_NAME} ({env.SITE_URL}) es un sitio editorial e informativo sobre la NFL
(clasificaciones, estadísticas, análisis de partidos y contenido educativo). No ofrece
apuestas, pronósticos, fantasy ni servicios financieros.

#### 3. Propiedad intelectual
Los textos, el diseño y el código de {env.SITE_NAME} son propiedad de su titular salvo
que se indique lo contrario. Los datos estadísticos de la NFL provienen de
[nflverse](https://github.com/nflverse) (nflreadpy), un proyecto de datos abiertos.
Los nombres, logos y marcas de la NFL y sus equipos pertenecen a sus respectivos titulares.

#### 4. Responsabilidad
El contenido tiene fines informativos y educativos. {env.SITE_NAME} no garantiza la
exactitud absoluta de los datos (dependen de terceros) ni se hace responsable del uso
que se haga de la información publicada.

#### 5. Legislación aplicable
{PLACEHOLDER}
""")


def _privacidad():
    st.markdown(f"""
#### Responsable del tratamiento
{PLACEHOLDER}

- **Responsable:** [completar]
- **Contacto:** {env.CONTACT_EMAIL}

#### Qué datos tratamos
- **Navegación:** si Google Analytics está activo, se recogen datos de uso agregados y
  anonimizados (páginas vistas, duración de la sesión, país aproximado).
- **Contacto:** si nos escribes por email, tratamos los datos que nos facilites
  únicamente para responder a tu consulta.
- {env.SITE_NAME} no requiere registro ni cuenta de usuario para navegar.

#### Con quién compartimos datos
Si están activos, usamos servicios de terceros para medir el uso del sitio o mostrar
publicidad (Google Analytics, Google AdSense). Estos servicios pueden tratar datos según
sus propias políticas de privacidad.

#### Tus derechos
Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación y
portabilidad escribiendo a {env.CONTACT_EMAIL}.

{PLACEHOLDER} *(completar con base legal, plazos de conservación y autoridad de control
cuando el sitio esté operativo con tratamiento real de datos).*
""")


def _cookies():
    analytics_row = ("✅ Activas" if env.ANALYTICS_ENABLED else
                      "⬜ No activas actualmente")
    adsense_row = ("✅ Activas" if env.ADSENSE_ENABLED else
                   "⬜ No activas actualmente")
    st.markdown(f"""
#### ¿Qué son las cookies?
Pequeños archivos que un sitio web guarda en tu navegador para recordar información
sobre tu visita.

#### Cookies que usa {env.SITE_NAME}

| Tipo | Finalidad | Estado |
|---|---|---|
| Técnicas | Funcionamiento básico de la aplicación (navegación entre secciones) | ✅ Siempre activas |
| Analíticas (Google Analytics) | Medir visitas y uso del sitio de forma agregada | {analytics_row} |
| Publicitarias (Google AdSense) | Personalización de anuncios | {adsense_row} |

#### Cómo desactivarlas
Puedes bloquear o eliminar las cookies desde la configuración de tu navegador. Bloquear
las cookies técnicas puede afectar al funcionamiento normal de la aplicación.

{PLACEHOLDER}
""")


def _contacto():
    st.markdown(f"#### Escríbenos\n\n📧 [{env.CONTACT_EMAIL}](mailto:{env.CONTACT_EMAIL})\n")
    st.markdown("#### Síguenos")
    for nombre, url in REDES.items():
        if nombre != "Contacto":
            st.markdown(f"- [{nombre}]({url})")


def _sobre():
    st.markdown(f"""
#### ¿Qué es {env.SITE_NAME}?

{env.SITE_NAME} es un proyecto editorial en español sobre la NFL: clasificación y
resultados actualizados, rankings de líderes estadísticos en todas las posiciones,
análisis de equipos y partidos basado en métricas avanzadas (EPA, eficiencia
ofensiva/defensiva), fichas de jugador con contexto real dentro de su posición, y una
sección de Football IQ para aprender los conceptos del juego desde cero.

**Entiende la NFL. No solo la sigas.**

Los datos provienen de [nflverse](https://github.com/nflverse), un proyecto de datos
abiertos de la comunidad NFL en Python/R.

{PLACEHOLDER} *(completar con la historia/equipo detrás del proyecto cuando se quiera
publicar esa información).*
""")


_RENDERERS = {
    "aviso": _aviso, "privacidad": _privacidad, "cookies": _cookies,
    "contacto": _contacto, "sobre": _sobre,
}


def render(ctx):
    st.markdown('<div class="sect-title">Información legal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sect-sub">Aviso legal, privacidad, cookies y contacto de '
                f'{env.SITE_NAME}.</div>', unsafe_allow_html=True)

    if "legal_section" not in st.session_state or st.session_state.legal_section not in _RENDERERS:
        st.session_state.legal_section = "aviso"

    cols = st.columns(len(SECTIONS))
    for col, (key, label) in zip(cols, SECTIONS):
        with col:
            active = st.session_state.legal_section == key
            if st.button(label, key=f"legal_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.legal_section = key
                st.rerun()

    st.markdown("---")
    _RENDERERS[st.session_state.legal_section]()
