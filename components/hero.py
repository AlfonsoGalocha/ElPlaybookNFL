"""components/hero.py — carrusel superior (masthead): marca, líderes, duelo de la semana, jugador
destacado y noticias, más la tarjeta de noticias de un equipo.
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


def _slide(i, body_html, tag="", cta="", href="#"):
    tag_html = f'<div class="hc-tag">{tag}</div>' if tag else ""
    cta_html = f'<div class="hc-cta">{cta}</div>' if cta else ""
    return (
        f'<a class="hc-slide" href="{href}" target="_blank" rel="noopener" '
        f'style="animation-delay:-{i * 5}s; background:{HERO_GRADIENTS[i % len(HERO_GRADIENTS)]}">'
        f'{tag_html}{body_html}{cta_html}</a>'
    )


def brand_slide(logo_b64, i=0):
    body = (f'<div class="hc-brand-row"><img class="hc-logo" src="data:image/png;base64,{logo_b64}"/>'
            f'<div class="hc-title">EL PLAYBOOK NFL</div></div>')
    return _slide(i, body, tag="🏈 BIENVENIDO", cta="Entiende la NFL. No solo la sigas.")


def top_teams_slide(top3, i=1):
    """top3: lista de (abbr, name, logo_url), ya ordenada por clasificación."""
    row = "".join(f'<div class="hc-team"><img src="{logo}"/><div>{abbr}</div></div>'
                  for abbr, _name, logo in top3)
    body = f'<div class="hc-teams-row">{row}</div><div class="hc-title" style="font-size:1.6rem">Líderes de la temporada</div>'
    return _slide(i, body, tag="🏆 CLASIFICACIÓN", cta="Ver clasificación completa →")


def duel_slide(week, away, home, i=2):
    """away/home: dict con 'abbr' y 'logo'."""
    body = (f'<div class="hc-vs-row"><img class="hc-vs-logo" src="{away["logo"]}"/>'
            f'<div class="hc-vs-text">VS</div><img class="hc-vs-logo" src="{home["logo"]}"/></div>'
            f'<div class="hc-title" style="font-size:1.5rem">{away["abbr"]} @ {home["abbr"]}</div>')
    return _slide(i, body, tag=f"⚔️ SEMANA {week} · DUELO CLAVE", cta="Ver el matchup completo →")


def player_slide(name, headshot, stat_label, stat_value, i=3):
    body = (f'<div class="hc-player-row"><img class="hc-player-photo" src="{headshot}"/>'
            f'<div><div class="hc-title" style="font-size:1.6rem">{name}</div>'
            f'<div class="hc-cta" style="margin-top:2px">{stat_label}: {stat_value}</div></div></div>')
    return _slide(i, body, tag="🔥 DESTACADO DE LA TEMPORADA")


def news_slide(title, link, i):
    body = f'<div class="hc-title">{title}</div>'
    return _slide(i, body, tag="🏈 NFL · ÚLTIMA HORA", cta="Leer más →", href=link)


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
