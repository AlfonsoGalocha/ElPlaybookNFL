#!/usr/bin/env python3
"""
nfl_graficos.py — Funciones compartidas que construyen las imagenes
(ranking de jornada y tarjeta de jugador) a partir de un DataFrame de pandas.

Lo usan tanto los scripts de linea de comandos como el panel (panel_nfl.py).
Devuelven figuras de matplotlib; usa fig_a_png(fig) para obtener los bytes PNG.
"""

import io
import urllib.request

import numpy as np
import matplotlib
matplotlib.use("Agg")               # sin ventana; ideal para servidor/web
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse

# ---------------------------------------------------------------------------
# MARCA (una sola vez, compartida por todo)
# ---------------------------------------------------------------------------
CANAL  = "@tu_canal_nfl"
BG     = "#0B0E14"
CARD   = "#161B26"
FG     = "#FFFFFF"
MUTED  = "#8A93A6"
ACCENT = "#00E5A0"

STATS = {
    "passing_yards":   ("passing_yards",   "YARDAS DE PASE",        "yds", 0),
    "passing_tds":     ("passing_tds",     "TOUCHDOWNS DE PASE",    "TD",  0),
    "rushing_yards":   ("rushing_yards",   "YARDAS POR TIERRA",     "yds", 0),
    "rushing_tds":     ("rushing_tds",     "TDs POR TIERRA",        "TD",  0),
    "receiving_yards": ("receiving_yards", "YARDAS DE RECEPCION",   "yds", 0),
    "receiving_tds":   ("receiving_tds",   "TDs DE RECEPCION",      "TD",  0),
    "passing_epa":     ("passing_epa",     "EPA DE PASE (avanzada)", "EPA", 1),
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _ensure_visible(hex_color):
    try:
        r, g, b = _hex_to_rgb(hex_color)
    except Exception:
        return ACCENT
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum < 0.20:
        r, g, b = (c + (1 - c) * 0.40 for c in (r, g, b))
    return (r, g, b)


def team_info(teams_df):
    """teams_df (polars) -> dict abbr -> (color_visible, nombre_completo)."""
    return {r["team_abbr"]: (_ensure_visible(r["team_color"]), r["team_name"])
            for r in teams_df.iter_rows(named=True)}


def _mode(s):
    m = s.mode()
    return m.iloc[0] if len(m) else ""


def _fmt(n, dec=0):
    return f"{n:,.{dec}f}".replace(",", ".")


def fig_a_png(fig, dpi=100):
    """Convierte una figura en bytes PNG (para descargar)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 1) RANKING de jornada / temporada
# ---------------------------------------------------------------------------
def make_ranking(pdf, season, week, stat_key, top_n, teams):
    col, title, suffix, dec = STATS[stat_key]
    d = pdf if week is None else pdf[pdf["week"] == week]
    g = (d.groupby("player_display_name")
           .agg(val=(col, "sum"), team=("team", _mode)).reset_index())
    g = g[g["val"] > 0].sort_values("val", ascending=False).head(top_n)

    names = g["player_display_name"].tolist()[::-1]
    vals  = g["val"].tolist()[::-1]
    tcols = [teams.get(t, (ACCENT,))[0] for t in g["team"].tolist()[::-1]]
    subtitle = (f"TEMPORADA {season} · JORNADA {week}" if week
                else f"TEMPORADA {season} · TOTAL")

    fig, ax = plt.subplots(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    y = range(len(names))
    ax.barh(y, vals, color=tcols, height=0.62, zorder=3,
            edgecolor="#FFFFFF", linewidth=0.8)
    maxv = max(vals) if vals else 1
    for i, (n, v) in enumerate(zip(names, vals)):
        ax.text(0, i + 0.42, n.upper(), color=FG, fontsize=21,
                fontweight="bold", va="bottom", ha="left", zorder=4)
        ax.text(v + maxv * 0.015, i, f"{_fmt(v, dec)} {suffix}", color=FG,
                fontsize=19, fontweight="bold", va="center", ha="left", zorder=4)
    ax.set_xlim(0, maxv * 1.28); ax.set_ylim(-0.6, len(names) - 0.1); ax.axis("off")
    fig.text(0.07, 0.955, title, color=FG, fontsize=52, fontweight="bold",
             ha="left", va="top")
    fig.text(0.07, 0.905, subtitle, color=ACCENT, fontsize=27,
             fontweight="bold", ha="left", va="top")
    fig.add_artist(plt.Line2D([0.07, 0.30], [0.878, 0.878], color=ACCENT, lw=4,
                   transform=fig.transFigure))
    fig.text(0.07, 0.045, CANAL, color=FG, fontsize=26, fontweight="bold",
             ha="left", va="center")
    fig.text(0.93, 0.045, "Datos: nflverse", color=MUTED, fontsize=17,
             ha="right", va="center")
    plt.subplots_adjust(left=0.07, right=0.97, top=0.86, bottom=0.09)
    return fig


# ---------------------------------------------------------------------------
# 2) TARJETA de jugador
# ---------------------------------------------------------------------------
def _download_headshot(url):
    if not url:
        return None
    try:
        from PIL import Image
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        im = Image.open(io.BytesIO(data)).convert("RGBA")
        return np.asarray(im).astype(float) / 255.0
    except Exception:
        return None


def _tiles(pos, s):
    comp_pct = (s["completions"] / s["attempts"] * 100) if s["attempts"] else 0
    ypc = (s["rushing_yards"] / s["carries"]) if s["carries"] else 0
    ypr = (s["receiving_yards"] / s["receptions"]) if s["receptions"] else 0
    pos = (pos or "").upper()
    if pos == "QB":
        return [("YDS PASE", _fmt(s["passing_yards"])), ("TD PASE", _fmt(s["passing_tds"])),
                ("INTERCEP.", _fmt(s["passing_interceptions"])), ("% COMP", _fmt(comp_pct, 1)),
                ("YDS TIERRA", _fmt(s["rushing_yards"])), ("TD TIERRA", _fmt(s["rushing_tds"]))]
    if pos in ("RB", "FB"):
        return [("YDS TIERRA", _fmt(s["rushing_yards"])), ("TD TIERRA", _fmt(s["rushing_tds"])),
                ("CARRERAS", _fmt(s["carries"])), ("YDS/CARR.", _fmt(ypc, 1)),
                ("RECEPC.", _fmt(s["receptions"])), ("YDS RECEP.", _fmt(s["receiving_yards"]))]
    if pos in ("WR", "TE"):
        return [("RECEPC.", _fmt(s["receptions"])), ("OBJETIVOS", _fmt(s["targets"])),
                ("YDS RECEP.", _fmt(s["receiving_yards"])), ("TD RECEP.", _fmt(s["receiving_tds"])),
                ("YDS/RECEP.", _fmt(ypr, 1)), ("TD TIERRA", _fmt(s["rushing_tds"]))]
    return [("YDS PASE", _fmt(s["passing_yards"])), ("YDS TIERRA", _fmt(s["rushing_yards"])),
            ("YDS RECEP.", _fmt(s["receiving_yards"])),
            ("TD TOTAL", _fmt(s["passing_tds"] + s["rushing_tds"] + s["receiving_tds"]))]


def make_card(pdf, season, name, teams, modo="circulo", foto_array=None):
    p = pdf[pdf["player_display_name"] == name]
    cols = ["completions", "attempts", "passing_yards", "passing_tds",
            "passing_interceptions", "carries", "rushing_yards", "rushing_tds",
            "receptions", "targets", "receiving_yards", "receiving_tds"]
    s = {c: p[c].sum() for c in cols}
    position = _mode(p["position"])
    team = _mode(p["team"])
    heads = p["headshot_url"].dropna()
    headshot = heads.iloc[0] if len(heads) else None
    color, team_name = teams.get(team, (ACCENT, team))

    fig, ax = plt.subplots(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0.62), 1, 0.38, color=color, zorder=1))
    ax.text(0.5, 0.965, f"{position}  ·  {team_name.upper()}", color=FG,
            fontsize=24, fontweight="bold", ha="center", va="top", zorder=5)

    aspect = 1080 / 1920
    cx, cy, rad = 0.5, 0.78, 0.15
    img = foto_array if foto_array is not None else _download_headshot(headshot)

    if modo == "cuerpo" and img is not None:
        ar = img.shape[1] / img.shape[0]
        h = 0.34; w = h * (1920 / 1080) * ar
        if w > 0.86:
            w = 0.86; h = w * (1080 / 1920) / ar
        axins = fig.add_axes([0.5 - w / 2, 0.62, w, h], zorder=4)
        axins.imshow(img, extent=[0, 1, 0, 1]); axins.axis("off")
    else:
        ax.add_patch(Ellipse((cx, cy), 2 * (rad + 0.012),
                     2 * (rad + 0.012) * aspect, color=FG, zorder=3))
        if img is not None:
            w = 2 * rad; h = w * aspect
            axins = fig.add_axes([cx - w / 2, cy - h / 2, w, h], zorder=4)
            axins.imshow(img, extent=[0, 1, 0, 1])
            axins.set_xlim(0, 1); axins.set_ylim(0, 1); axins.axis("off")
            clip = Circle((0.5, 0.5), 0.5, transform=axins.transData)
            for a in axins.get_images():
                a.set_clip_path(clip)
        else:
            ax.add_patch(Ellipse((cx, cy), 2 * rad, 2 * rad * aspect,
                         color=BG, zorder=3.5))
            initials = "".join([w[0] for w in name.split()[:2]]).upper()
            ax.text(cx, cy, initials, color=FG, fontsize=70, fontweight="bold",
                    ha="center", va="center", zorder=4)

    ax.text(0.5, 0.585, name.upper(), color=FG, fontsize=54, fontweight="bold",
            ha="center", va="top", zorder=5)
    ax.text(0.5, 0.545, f"TEMPORADA {season} · TEMPORADA REGULAR", color=ACCENT,
            fontsize=22, fontweight="bold", ha="center", va="top", zorder=5)

    tiles = _tiles(position, s)
    ncols, rows = 2, (len(tiles) + 1) // 2
    x0, x1 = 0.07, 0.93
    y_top, y_bot = 0.50, 0.10
    tw = (x1 - x0 - 0.04) / ncols
    th = (y_top - y_bot - 0.03 * (rows - 1)) / rows
    for i, (label, value) in enumerate(tiles):
        r, c = divmod(i, ncols)
        bx = x0 + c * (tw + 0.04); by = y_top - th - r * (th + 0.03)
        ax.add_patch(FancyBboxPatch((bx, by), tw, th,
                     boxstyle="round,pad=0.006,rounding_size=0.02",
                     linewidth=0, facecolor=CARD, zorder=2))
        ax.text(bx + tw / 2, by + th * 0.60, value, color=FG, fontsize=46,
                fontweight="bold", ha="center", va="center", zorder=3)
        ax.text(bx + tw / 2, by + th * 0.22, label, color=MUTED, fontsize=20,
                fontweight="bold", ha="center", va="center", zorder=3)

    ax.add_patch(plt.Rectangle((0, 0.055), 1, 0.006, color=ACCENT, zorder=2))
    ax.text(0.07, 0.03, CANAL, color=FG, fontsize=24, fontweight="bold",
            ha="left", va="center", zorder=3)
    ax.text(0.93, 0.03, "Datos: nflverse", color=MUTED, fontsize=16,
            ha="right", va="center", zorder=3)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig
