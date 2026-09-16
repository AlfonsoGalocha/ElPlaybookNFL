"""components/hero.py — carrusel superior (masthead): marca, líderes, duelo de la semana, jugador
destacado y noticias, más la tarjeta de noticias de un equipo.

Los slides que representan equipos/jugadores usan un layout de dos columnas
(texto a la izquierda, imagen grande a la derecha, ~35-38% del ancho) para
que el logo/foto sea protagonista sin deformarse (siempre object-fit:contain).
"""

import nfl_graficos as G

ACCENT, ACCENT2 = G.ACCENT, G.ACCENT2

HERO_GRADIENTS = [
    f"linear-gradient(135deg,{ACCENT}dd,#1a0a12 70%)",
    f"linear-gradient(135deg,{ACCENT2}dd,#08131f 70%)",
    "linear-gradient(135deg,#7a1130dd,#171B24 70%)",
    "linear-gradient(135deg,#0e5f9add,#171B24 70%)",
    "linear-gradient(135deg,#3a0d1add,#171B24 70%)",
]

FALLBACK_NEWS = [
    ("Rankings, clasificación y equipos en un solo lugar", "#"),
    ("Sigue a tus jugadores favoritos jornada a jornada", "#"),
    ("Compara stats y genera tu propia tarjeta descargable", "#"),
    ("Datos oficiales de nflverse, actualizados cada semana", "#"),
]


def _slide(i, text_html, tag="", cta="", href="#", visual_html=None):
    tag_html = f'<div class="hc-tag">{tag}</div>' if tag else ""
    cta_html = f'<div class="hc-cta">{cta}</div>' if cta else ""
    text_block = f'<div class="hc-text">{tag_html}{text_html}{cta_html}</div>'
    visual_block = f'<div class="hc-visual">{visual_html}</div>' if visual_html else ""
    slide_cls = "hc-slide hc-slide-visual" if visual_html else "hc-slide"
    return (
        f'<a class="{slide_cls}" href="{href}" target="_blank" rel="noopener" '
        f'style="animation-delay:-{i * 5}s; background:{HERO_GRADIENTS[i % len(HERO_GRADIENTS)]}">'
        f'{text_block}{visual_block}</a>'
    )


def brand_slide(logo_b64, i=0):
    text = '<div class="hc-title">EL PLAYBOOK NFL</div>'
    visual = f'<img class="hc-visual-logo" src="data:image/png;base64,{logo_b64}"/>'
    return _slide(i, text, tag="🏈 BIENVENIDO", cta="Entiende la NFL. No solo la sigas.", visual_html=visual)


def top_teams_slide(top3, i=1):
    """top3: lista de (abbr, name, logo_url), ya ordenada por clasificación."""
    text = '<div class="hc-title" style="font-size:1.7rem">Líderes de la temporada</div>'
    logos = "".join(f'<img class="hc-visual-mini-logo" src="{logo}" title="{abbr}"/>'
                    for abbr, _name, logo in top3)
    visual = f'<div class="hc-visual-team-row">{logos}</div>'
    return _slide(i, text, tag="🏆 CLASIFICACIÓN", cta="Ver clasificación completa →", visual_html=visual)


def duel_slide(week, away, home, i=2):
    """away/home: dict con 'abbr' y 'logo'."""
    text = f'<div class="hc-title">{away["abbr"]} @ {home["abbr"]}</div>'
    visual = (f'<div class="hc-visual-vs-row">'
              f'<img class="hc-visual-duel-logo" src="{away["logo"]}" title="{away["abbr"]}"/>'
              f'<span class="hc-visual-vs-text">VS</span>'
              f'<img class="hc-visual-duel-logo" src="{home["logo"]}" title="{home["abbr"]}"/>'
              f'</div>')
    return _slide(i, text, tag=f"⚔️ SEMANA {week} · DUELO CLAVE", cta="Ver el matchup completo →",
                  visual_html=visual)


def player_slide(name, headshot, stat_label, stat_value, i=3):
    text = (f'<div class="hc-title" style="font-size:1.6rem">{name}</div>'
            f'<div class="hc-cta" style="margin-top:2px">{stat_label}: {stat_value}</div>')
    visual = f'<img class="hc-visual-photo" src="{headshot}"/>' if headshot else ""
    return _slide(i, text, tag="🔥 DESTACADO DE LA TEMPORADA", visual_html=visual)


def news_slide(title, link, i):
    text = f'<div class="hc-title">{title}</div>'
    return _slide(i, text, tag="🏈 NFL · ÚLTIMA HORA", cta="Leer más →", href=link)


def hero_html(feature_slides, news_items=None):
    """feature_slides: lista de slides ya renderizados (brand_slide, top_teams_slide...).
    Se completa hasta 5 con noticias reales (o de respaldo)."""
    slides = list(feature_slides)
    news = list(news_items or []) or FALLBACK_NEWS
    i, n = len(slides), 0
    while len(slides) < 5:
        title, link = news[n % len(news)]
        slides.append(news_slide(title, link, i))
        i += 1
        n += 1
    slides = slides[:5]
    dots = "".join(f'<span class="hc-dot" style="animation-delay:-{i * 5}s"></span>' for i in range(5))
    return f'<div class="hero-carousel">{"".join(slides)}<div class="hc-dots">{dots}</div></div>'


def team_news_html(meta):
    grad = f"linear-gradient(150deg,{meta['color']}66,#171B24 80%)"
    return (
        f'<div class="team-news-card" style="background:{grad}">'
        f'<div class="tn-tag">📰 NOTICIAS · {meta["name"].upper()}</div>'
        f'<div class="tn-title">Próximamente</div>'
        f'<div class="tn-sub">Aquí aparecerán las últimas noticias sobre este equipo.</div>'
        f'</div>'
    )
