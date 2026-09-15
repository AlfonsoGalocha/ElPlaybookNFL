#!/usr/bin/env python3
"""
dato_jornada.py — Genera un grafico vertical (1080x1920) tipo "ranking"
con datos REALES de la NFL, listo para subir a TikTok / Reels / Shorts.

Datos: nflverse (gratis y abierto) via la libreria nflreadpy.
Autor base: esqueleto para el formato "firma" del canal.

Uso rapido:
    python3 dato_jornada.py                      # top pasadores 2025 (por defecto)
    python3 dato_jornada.py --stat rushing_yards # top corredores
    python3 dato_jornada.py --season 2025 --week 10 --stat receiving_yards
    python3 dato_jornada.py --stat passing_tds --top 8

Cambia CANAL abajo por el @ de tu amigo y ya tienes tu plantilla.
"""

import argparse
import nflreadpy as nfl
import polars as pl
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------------------------------------------------------------------------
# CONFIG DE MARCA  (cambia esto una vez y todo sale con vuestra identidad)
# ---------------------------------------------------------------------------
CANAL      = "@tu_canal_nfl"          # el @ de tu amigo
BG         = "#0B0E14"                 # fondo
FG         = "#FFFFFF"                 # texto principal
MUTED      = "#8A93A6"                 # texto secundario
ACCENT     = "#00E5A0"                 # color de acento de la marca

# Catalogo de metricas disponibles: clave CLI -> (columna, titulo, sufijo, decimales)
STATS = {
    "passing_yards":   ("passing_yards",   "YARDAS DE PASE",        "yds", 0),
    "passing_tds":     ("passing_tds",     "TOUCHDOWNS DE PASE",    "TD",  0),
    "rushing_yards":   ("rushing_yards",   "YARDAS POR TIERRA",     "yds", 0),
    "rushing_tds":     ("rushing_tds",     "TDs POR TIERRA",        "TD",  0),
    "receiving_yards": ("receiving_yards", "YARDAS DE RECEPCION",   "yds", 0),
    "receiving_tds":   ("receiving_tds",   "TDs DE RECEPCION",      "TD",  0),
    "passing_epa":     ("passing_epa",     "EPA DE PASE (avanzada)", "EPA", 1),
}


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _ensure_visible(hex_color):
    """Si el color del equipo es demasiado oscuro para el fondo, lo aclara
    manteniendo el tono, para que la barra siempre se vea."""
    try:
        r, g, b = _hex_to_rgb(hex_color)
    except Exception:
        return ACCENT
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum < 0.22:                      # muy oscuro -> mezclar hacia blanco
        mix = 0.45
        r, g, b = (c + (1 - c) * mix for c in (r, g, b))
    return (r, g, b)


def team_color_map():
    """Diccionario team_abbr -> color primario del equipo (con contraste asegurado)."""
    t = nfl.load_teams()
    return {r["team_abbr"]: _ensure_visible(r["team_color"]) for r in t.iter_rows(named=True)}


def get_ranking(season, week, stat_col, top_n):
    """Devuelve (nombre, equipo, valor) del top N para la metrica pedida."""
    df = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    if week is not None:
        df = df.filter(pl.col("week") == week)

    # Equipo mas frecuente del jugador (por si cambio de equipo en el ano)
    agg = (
        df.group_by("player_display_name")
          .agg([
              pl.col(stat_col).sum().alias("val"),
              pl.col("team").mode().first().alias("team"),
          ])
          .filter(pl.col("val") > 0)
          .sort("val", descending=True)
          .head(top_n)
    )
    return agg


def make_graphic(agg, title, subtitle, suffix, decimals, out_path):
    colors = team_color_map()
    names  = agg["player_display_name"].to_list()[::-1]   # invertido: mayor arriba
    vals   = agg["val"].to_list()[::-1]
    teams  = agg["team"].to_list()[::-1]
    bar_colors = [colors.get(tm, ACCENT) for tm in teams]

    # Lienzo vertical 1080x1920 (9:16). 1080/100=10.8 in, 1920/100=19.2 in a 100 dpi
    fig, ax = plt.subplots(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    y = range(len(names))
    ax.barh(y, vals, color=bar_colors, height=0.62, zorder=3,
            edgecolor="#FFFFFF", linewidth=0.8)

    # Etiquetas: nombre encima de la barra, valor al final
    maxv = max(vals)
    for i, (n, v, c) in enumerate(zip(names, vals, bar_colors)):
        ax.text(0, i + 0.42, n.upper(), color=FG, fontsize=21,
                fontweight="bold", va="bottom", ha="left", zorder=4)
        label = f"{v:,.{decimals}f}".replace(",", ".")
        ax.text(v + maxv * 0.015, i, f"{label} {suffix}", color=FG,
                fontsize=19, fontweight="bold", va="center", ha="left", zorder=4)

    # Limpieza de ejes
    ax.set_xlim(0, maxv * 1.28)
    ax.set_ylim(-0.6, len(names) - 0.1)
    ax.axis("off")

    # Titular grande arriba + barra de acento
    fig.text(0.07, 0.955, title, color=FG, fontsize=52, fontweight="bold",
             ha="left", va="top")
    fig.text(0.07, 0.905, subtitle, color=ACCENT, fontsize=27,
             fontweight="bold", ha="left", va="top")
    fig.add_artist(plt.Line2D([0.07, 0.30], [0.878, 0.878],
                   color=ACCENT, lw=4, transform=fig.transFigure))

    # Pie: marca + fuente
    fig.text(0.07, 0.045, CANAL, color=FG, fontsize=26, fontweight="bold",
             ha="left", va="center")
    fig.text(0.93, 0.045, "Datos: nflverse", color=MUTED, fontsize=17,
             ha="right", va="center")

    plt.subplots_adjust(left=0.07, right=0.97, top=0.86, bottom=0.09)
    fig.savefig(out_path, facecolor=BG, bbox_inches=None)
    plt.close(fig)
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--season", type=int, default=2025)
    p.add_argument("--week", type=int, default=None, help="omite = temporada completa")
    p.add_argument("--stat", choices=STATS.keys(), default="passing_yards")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--out", default="dato_jornada.png")
    args = p.parse_args()

    col, stat_title, suffix, dec = STATS[args.stat]
    agg = get_ranking(args.season, args.week, col, args.top)

    if args.week:
        subtitle = f"TEMPORADA {args.season} · JORNADA {args.week}"
    else:
        subtitle = f"TEMPORADA {args.season} · TOTAL"

    make_graphic(agg, stat_title, subtitle, suffix, dec, args.out)
    print(f"Listo -> {args.out}")


if __name__ == "__main__":
    main()