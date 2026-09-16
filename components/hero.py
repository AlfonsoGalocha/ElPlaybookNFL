"""components/hero.py — carrusel de noticias (masthead) y tarjeta de noticias de un equipo."""

import nfl_graficos as G

ACCENT, ACCENT2 = G.ACCENT, G.ACCENT2

HERO_GRADIENTS = [
    f"linear-gradient(135deg,{ACCENT}dd,#1a0a12 70%)",
    f"linear-gradient(135deg,{ACCENT2}dd,#08131f 70%)",
    "linear-gradient(135deg,#7a1130dd,#0B0E14 70%)",
    "linear-gradient(135deg,#0e5f9add,#0B0E14 70%)",
    "linear-gradient(135deg,#3a0d1add,#0B0E14 70%)",
]

FALLBACK_NEWS = [
    ("Bienvenido a El Playbook NFL", "#"),
    ("Rankings, clasificación y equipos en un solo lugar", "#"),
    ("Sigue a tus jugadores favoritos jornada a jornada", "#"),
    ("Compara stats y genera tu propia tarjeta descargable", "#"),
    ("Datos oficiales de nflverse, actualizados cada semana", "#"),
]


def hero_html(items):
    src = list(items or FALLBACK_NEWS)[:5]
    if not src:
        src = FALLBACK_NEWS
    while len(src) < 5:
        src = src + src
    src = src[:5]
    slides = []
    for i, (title, link) in enumerate(src):
        slides.append(
            f'<a class="hc-slide" href="{link}" target="_blank" rel="noopener" '
            f'style="animation-delay:-{i * 5}s; background:{HERO_GRADIENTS[i % len(HERO_GRADIENTS)]}">'
            f'<div class="hc-tag">🏈 NFL · ÚLTIMA HORA</div>'
            f'<div class="hc-title">{title}</div>'
            f'<div class="hc-cta">Leer más →</div></a>'
        )
    dots = "".join(f'<span class="hc-dot" style="animation-delay:-{i * 5}s"></span>' for i in range(5))
    return f'<div class="hero-carousel">{"".join(slides)}<div class="hc-dots">{dots}</div></div>'


def team_news_html(meta):
    grad = f"linear-gradient(150deg,{meta['color']}66,#0B0E14 80%)"
    return (
        f'<div class="team-news-card" style="background:{grad}">'
        f'<div class="tn-tag">📰 NOTICIAS · {meta["name"].upper()}</div>'
        f'<div class="tn-title">Próximamente</div>'
        f'<div class="tn-sub">Aquí aparecerán las últimas noticias sobre este equipo.</div>'
        f'</div>'
    )
