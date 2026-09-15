#!/usr/bin/env python3
"""
tarjeta_jugador.py — Genera una TARJETA vertical (1080x1920) de un jugador
de la NFL, con su FOTO oficial, colores de su equipo y sus estadisticas de
la temporada. Lista para TikTok / Reels / Shorts.

Datos y foto: nflverse (gratis y abierto) via nflreadpy.

Uso:
    python3 tarjeta_jugador.py --player "Josh Allen"
    python3 tarjeta_jugador.py --player "Saquon Barkley" --season 2025
    python3 tarjeta_jugador.py --player "Ja'Marr Chase" --dir ~/NFL

Notas:
  - El nombre no tiene que ser exacto: "allen" o "josh allen" valen. Si hay
    varios jugadores que coinciden, coge al que mas jugo esa temporada.
  - Las estadisticas mostradas se adaptan a la posicion (QB, RB, WR/TE...).
  - Si la foto no se pudiera descargar, dibuja un circulo con las iniciales.
"""

import argparse
import os
import io
import urllib.request

import nflreadpy as nfl
import polars as pl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse

# ---------------------------------------------------------------------------
# CONFIG DE MARCA
# ---------------------------------------------------------------------------
CANAL  = "@elplaybooknfl"          # el @ de tu amigo
BG     = "#0B0E14"
FG     = "#FFFFFF"
MUTED  = "#8A93A6"
ACCENT = "#00E5A0"


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
        mix = 0.40
        r, g, b = (c + (1 - c) * mix for c in (r, g, b))
    return (r, g, b)


def team_info():
    """abbr -> (color_visible, nombre_completo)."""
    t = nfl.load_teams()
    return {r["team_abbr"]: (_ensure_visible(r["team_color"]), r["team_name"])
            for r in t.iter_rows(named=True)}


def find_player(df, query):
    """Busca por coincidencia parcial e insensible a mayusculas.
    Si hay varios, devuelve el mas activo (mas jugadas) de la temporada."""
    q = query.lower().strip()
    cand = df.filter(pl.col("player_display_name").str.to_lowercase().str.contains(q))
    if cand.height == 0:
        return None, []
    activity = (cand.group_by("player_display_name")
                    .agg((pl.col("attempts").sum()
                          + pl.col("carries").sum()
                          + pl.col("targets").sum()).alias("act"))
                    .sort("act", descending=True))
    best = activity["player_display_name"][0]
    others = activity["player_display_name"].to_list()[1:]
    return best, others


def season_stats(df, name):
    p = df.filter((pl.col("player_display_name") == name)
                  & (pl.col("season_type") == "REG"))
    agg = p.select([
        pl.col("completions").sum(), pl.col("attempts").sum(),
        pl.col("passing_yards").sum(), pl.col("passing_tds").sum(),
        pl.col("passing_interceptions").sum(),
        pl.col("carries").sum(), pl.col("rushing_yards").sum(),
        pl.col("rushing_tds").sum(),
        pl.col("receptions").sum(), pl.col("targets").sum(),
        pl.col("receiving_yards").sum(), pl.col("receiving_tds").sum(),
        pl.col("week").n_unique().alias("games"),
    ]).to_dicts()[0]
    meta = {
        "position": p["position"].mode().first(),
        "team": p["team"].mode().first(),
        "headshot": p["headshot_url"].drop_nulls()[0] if p["headshot_url"].drop_nulls().len() else None,
    }
    return agg, meta


def _fmt(n, dec=0):
    return f"{n:,.{dec}f}".replace(",", ".")


def tiles_for(pos, s):
    """Devuelve lista de (etiqueta, valor_formateado) segun la posicion."""
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
    # Generico
    return [("YDS PASE", _fmt(s["passing_yards"])), ("YDS TIERRA", _fmt(s["rushing_yards"])),
            ("YDS RECEP.", _fmt(s["receiving_yards"])), ("TD TOTAL",
             _fmt(s["passing_tds"] + s["rushing_tds"] + s["receiving_tds"]))]


def load_headshot(url):
    """Descarga la foto. Devuelve un array de imagen o None si falla."""
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        import matplotlib.image as mpimg
        return mpimg.imread(io.BytesIO(data), format="png")
    except Exception as e:
        print(f"(aviso) no se pudo bajar la foto: {e}")
        return None


def make_card(name, s, meta, season, teams, out_path):
    color, team_name = teams.get(meta["team"], (ACCENT, meta["team"]))
    fig, ax = plt.subplots(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # Panel superior con color de equipo
    ax.add_patch(plt.Rectangle((0, 0.62), 1, 0.38, color=color, zorder=1))
    ax.text(0.5, 0.965, f"{meta['position']}  ·  {team_name.upper()}", color=FG,
            fontsize=24, fontweight="bold", ha="center", va="top", zorder=5)

    # --- Foto (circulo perfecto) o respaldo con iniciales ---
    # El lienzo es 1080x1920, asi que para que un circulo NO salga ovalado
    # hay que corregir la altura por la relacion de aspecto.
    aspect = 1080 / 1920                      # 0.5625
    cx, cy, rad = 0.5, 0.78, 0.15

    def add_circle(xy, r, **kw):             # circulo visualmente redondo
        ax.add_patch(Ellipse(xy, width=2 * r, height=2 * r * aspect, **kw))

    add_circle((cx, cy), rad + 0.012, color=FG, zorder=3)   # aro blanco

    img = load_headshot(meta["headshot"])
    if img is not None:
        # Eje cuadrado en pixeles para que el recorte circular sea exacto
        w_frac = 2 * rad                      # ancho en fraccion de figura
        h_frac = w_frac * aspect              # misma medida en px -> cuadrado
        axins = fig.add_axes([cx - w_frac / 2, cy - h_frac / 2, w_frac, h_frac],
                             zorder=4)
        axins.imshow(img, extent=[0, 1, 0, 1])
        axins.set_xlim(0, 1); axins.set_ylim(0, 1); axins.axis("off")
        clip = Circle((0.5, 0.5), 0.5, transform=axins.transData)
        for artist in axins.get_images():
            artist.set_clip_path(clip)
    else:
        add_circle((cx, cy), rad, color=BG, zorder=3.5)
        initials = "".join([p[0] for p in name.split()[:2]]).upper()
        ax.text(cx, cy, initials, color=FG, fontsize=70, fontweight="bold",
                ha="center", va="center", zorder=4)

    # Nombre
    ax.text(0.5, 0.585, name.upper(), color=FG, fontsize=54, fontweight="bold",
            ha="center", va="top", zorder=5)
    ax.text(0.5, 0.545, f"TEMPORADA {season} · TEMPORADA REGULAR", color=ACCENT,
            fontsize=22, fontweight="bold", ha="center", va="top", zorder=5)

    # Rejilla de estadisticas (2 columnas)
    tiles = tiles_for(meta["position"], s)
    cols, rows = 2, (len(tiles) + 1) // 2
    x0, x1 = 0.07, 0.93
    y_top, y_bot = 0.50, 0.10
    tw = (x1 - x0 - 0.04) / cols
    th = (y_top - y_bot - 0.03 * (rows - 1)) / rows
    for i, (label, value) in enumerate(tiles):
        r, c = divmod(i, cols)
        bx = x0 + c * (tw + 0.04)
        by = y_top - th - r * (th + 0.03)
        ax.add_patch(FancyBboxPatch((bx, by), tw, th,
                     boxstyle="round,pad=0.006,rounding_size=0.02",
                     linewidth=0, facecolor="#161B26", zorder=2))
        ax.text(bx + tw / 2, by + th * 0.60, value, color=FG, fontsize=46,
                fontweight="bold", ha="center", va="center", zorder=3)
        ax.text(bx + tw / 2, by + th * 0.22, label, color=MUTED, fontsize=20,
                fontweight="bold", ha="center", va="center", zorder=3)

    # Acento + pie
    ax.add_patch(plt.Rectangle((0, 0.055), 1, 0.006, color=ACCENT, zorder=2))
    ax.text(0.07, 0.03, CANAL, color=FG, fontsize=24, fontweight="bold",
            ha="left", va="center", zorder=3)
    ax.text(0.93, 0.03, "Datos: nflverse", color=MUTED, fontsize=16,
            ha="right", va="center", zorder=3)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(out_path, facecolor=BG)
    plt.close(fig)
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--player", required=True, help='nombre, p.ej. "Josh Allen"')
    p.add_argument("--season", type=int, default=2025)
    p.add_argument("--dir", default=".")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    df = nfl.load_player_stats([args.season])
    name, others = find_player(df, args.player)
    if name is None:
        print(f"No encontre a nadie que coincida con '{args.player}' en {args.season}.")
        return
    if others:
        print(f"(varios coinciden; uso '{name}'. Otros: {', '.join(others[:4])})")

    s, meta = season_stats(df, name)
    teams = team_info()

    fname = args.out or f"tarjeta_{name.lower().replace(' ', '_')}_{args.season}.png"
    os.makedirs(args.dir, exist_ok=True)
    out_path = os.path.join(args.dir, fname)

    make_card(name, s, meta, args.season, teams, out_path)
    print(f"Listo -> {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
