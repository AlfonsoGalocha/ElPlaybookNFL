"""components/hero.py — piezas HTML de las diapositivas del hero slider (badge + widget
dinamico) y tarjeta de noticias de un equipo. panel_nfl.py controla el slide activo via
st.session_state y arma cada diapositiva con estas piezas; aqui solo vive el marcado, sin
logica de negocio — cada widget muestra unicamente datos ya calculados por
analytics.games/analytics.matchups/analytics.standings/analytics.totals, nunca texto inventado.
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


def player_widget_html(tag, name, headshot, team, position, tiles):
    """tiles: lista de (etiqueta, valor) — normalmente G._tiles(...) recortada a 2-3 stats."""
    photo = f'<img class="hw-player-photo" src="{headshot}"/>' if headshot else ""
    stats_html = "".join(
        f'<div class="hw-stat"><div class="hw-stat-value">{val}</div>'
        f'<div class="hw-stat-label">{lbl}</div></div>'
        for lbl, val in tiles
    )
    return (
        f'<div class="hero-widget-card hero-widget-player">'
        f'<div class="hw-tag">{tag}</div>'
        f'<div class="hw-player-row">{photo}'
        f'<div><div class="hw-player-name">{name}</div>'
        f'<div class="hw-player-meta">{position} · {team}</div></div></div>'
        f'<div class="hw-stat-row">{stats_html}</div>'
        f'</div>'
    )


def news_widget_html(tag, title, link):
    return (
        f'<a class="hero-widget-card hero-widget-link" href="{link}" target="_blank" rel="noopener">'
        f'<div class="hw-tag">{tag}</div>'
        f'<div class="hw-news-title">{title}</div>'
        f'<div class="hw-news-cta">Leer más →</div>'
        f'</a>'
    )


def top_teams_widget_html(teams):
    """teams: lista de hasta 3 dicts con 'rank', 'logo', 'name' y 'record' — los lideres
    actuales de la clasificacion, a tamaño grande (mismo ancho que la imagen de un slide)."""
    cards = "".join(
        f'<div class="hero-top3-team">'
        f'<div class="hero-top3-rank">#{t["rank"]}</div>'
        f'<img src="{t["logo"]}"/>'
        f'<div class="hero-top3-name">{t["name"]}</div>'
        f'<div class="hero-top3-record">{t["record"]}</div>'
        f'</div>'
        for t in teams
    )
    return f'<div class="hero-top3-row">{cards}</div>'


def team_news_html(meta):
    grad = f"linear-gradient(150deg,{meta['color']}66,#171B24 80%)"
    return (
        f'<div class="team-news-card" style="background:{grad}">'
        f'<div class="tn-tag">📰 NOTICIAS · {meta["name"].upper()}</div>'
        f'<div class="tn-title">Próximamente</div>'
        f'<div class="tn-sub">Aquí aparecerán las últimas noticias sobre este equipo.</div>'
        f'</div>'
    )
