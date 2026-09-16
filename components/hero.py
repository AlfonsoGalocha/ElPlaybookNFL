"""components/hero.py — hero superior estatico (2 columnas: titular + widget dinamico) y
tarjeta de noticias de un equipo.

El widget de la derecha muestra, por orden de prioridad segun los datos disponibles: el
Partido de la Semana (Duelo Clave), el lider de la clasificacion, o la ultima noticia — nunca
texto inventado, solo lo que ya calculan analytics.games/analytics.matchups/analytics.standings.
"""


def matchup_widget_html(tag, week, away, home):
    """away/home: dict con 'abbr', 'name' y 'logo'."""
    return (
        f'<div class="hero-widget-card">'
        f'<div class="hw-tag">{tag} · SEMANA {week}</div>'
        f'<div class="hw-duel-row">'
        f'<div class="hw-team"><img src="{away["logo"]}"/><span>{away["abbr"]}</span></div>'
        f'<span class="hw-vs">VS</span>'
        f'<div class="hw-team"><img src="{home["logo"]}"/><span>{home["abbr"]}</span></div>'
        f'</div>'
        f'<div class="hw-sub">{away.get("name", "")} @ {home.get("name", "")}</div>'
        f'</div>'
    )


def leader_widget_html(tag, team_name, logo, record):
    return (
        f'<div class="hero-widget-card">'
        f'<div class="hw-tag">{tag}</div>'
        f'<div class="hw-leader-row">'
        f'<img class="hw-leader-logo" src="{logo}"/>'
        f'<div><div class="hw-leader-name">{team_name}</div>'
        f'<div class="hw-leader-record">{record}</div></div>'
        f'</div></div>'
    )


def news_widget_html(tag, title, link):
    return (
        f'<a class="hero-widget-card hero-widget-link" href="{link}" target="_blank" rel="noopener">'
        f'<div class="hw-tag">{tag}</div>'
        f'<div class="hw-news-title">{title}</div>'
        f'<div class="hw-news-cta">Leer más →</div>'
        f'</a>'
    )


def team_news_html(meta):
    grad = f"linear-gradient(150deg,{meta['color']}66,#171B24 80%)"
    return (
        f'<div class="team-news-card" style="background:{grad}">'
        f'<div class="tn-tag">📰 NOTICIAS · {meta["name"].upper()}</div>'
        f'<div class="tn-title">Próximamente</div>'
        f'<div class="tn-sub">Aquí aparecerán las últimas noticias sobre este equipo.</div>'
        f'</div>'
    )
