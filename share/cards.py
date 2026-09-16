"""share/cards.py — Share Center: tarjetas verticales (1080x1920) con branding de El Playbook NFL.

Los rankings y las fichas de jugador ya se generan en nfl_graficos.py
(make_ranking / make_card). Aqui ampliamos el mismo patron visual a otros
tipos de contenido compartible: resultado de quiz y resumen de equipo.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import nfl_graficos as G

BG, CARD, FG, MUTED, ACCENT, ACCENT2, CANAL = G.BG, G.CARD, G.FG, G.MUTED, G.ACCENT, G.ACCENT2, G.CANAL


def _base_fig():
    fig, ax = plt.subplots(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    return fig, ax


def _footer(ax):
    ax.add_patch(plt.Rectangle((0, 0.055), 1, 0.006, color=ACCENT, zorder=2))
    ax.text(0.07, 0.03, CANAL, color=FG, fontsize=24, fontweight="bold",
            ha="left", va="center", zorder=3)
    ax.text(0.93, 0.03, "Datos: nflverse", color=MUTED, fontsize=16,
            ha="right", va="center", zorder=3)


def _tiles_grid(ax, tiles, y_top=0.60, y_bot=0.10, ncols=2):
    rows = (len(tiles) + ncols - 1) // ncols
    x0, x1 = 0.07, 0.93
    tw = (x1 - x0 - 0.04 * (ncols - 1)) / ncols
    th = (y_top - y_bot - 0.03 * (rows - 1)) / rows
    for i, (label, value) in enumerate(tiles):
        r, c = divmod(i, ncols)
        bx = x0 + c * (tw + 0.04); by = y_top - th - r * (th + 0.03)
        ax.add_patch(FancyBboxPatch((bx, by), tw, th,
                     boxstyle="round,pad=0.006,rounding_size=0.02",
                     linewidth=0, facecolor=CARD, zorder=2))
        ax.text(bx + tw / 2, by + th * 0.60, str(value), color=FG, fontsize=44,
                fontweight="bold", ha="center", va="center", zorder=3)
        ax.text(bx + tw / 2, by + th * 0.22, label, color=MUTED, fontsize=19,
                fontweight="bold", ha="center", va="center", zorder=3)


def quiz_result_card(level_label, score, total):
    """Tarjeta de resultado de quiz: nivel, nota y un mensaje segun el acierto."""
    fig, ax = _base_fig()
    pct = score / total if total else 0
    color = ACCENT2 if pct >= 0.8 else (ACCENT if pct < 0.4 else "#FFD54A")

    ax.add_patch(plt.Rectangle((0, 0.78), 1, 0.22, color=color, zorder=1))
    ax.text(0.5, 0.965, "RESULTADO DEL QUIZ", color=FG, fontsize=26, fontweight="bold",
            ha="center", va="top", zorder=5)
    ax.text(0.5, 0.90, level_label.upper(), color="#0B0E14", fontsize=40, fontweight="bold",
            ha="center", va="top", zorder=5)

    ax.text(0.5, 0.62, f"{score}/{total}", color=FG, fontsize=140, fontweight="bold",
            ha="center", va="center", zorder=3)
    ax.text(0.5, 0.47, "RESPUESTAS CORRECTAS", color=MUTED, fontsize=22, fontweight="bold",
            ha="center", va="center", zorder=3)

    msg = ("¡Nivel dominado! 🏆" if pct >= 0.8 else
           "Vas por buen camino 👀" if pct >= 0.4 else "A seguir aprendiendo 📚")
    ax.add_patch(FancyBboxPatch((0.15, 0.30), 0.70, 0.10,
                 boxstyle="round,pad=0.01,rounding_size=0.03",
                 linewidth=0, facecolor=CARD, zorder=2))
    ax.text(0.5, 0.35, msg, color=FG, fontsize=26, fontweight="bold",
            ha="center", va="center", zorder=3)

    ax.text(0.5, 0.20, "EL PLAYBOOK NFL", color=ACCENT, fontsize=24, fontweight="bold",
            ha="center", va="center", zorder=3)
    ax.text(0.5, 0.16, "FOOTBALL IQ · QUIZ", color=MUTED, fontsize=16,
            ha="center", va="center", zorder=3)
    _footer(ax)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return G.fig_a_png(fig)


def team_summary_card(team_name, team_meta_row, season, tiles):
    """Tarjeta de resumen de equipo (record + stats clave), con el color del equipo."""
    fig, ax = _base_fig()
    color = team_meta_row.get("color", ACCENT)
    ax.add_patch(plt.Rectangle((0, 0.80), 1, 0.20, color=color, zorder=1))
    ax.text(0.5, 0.965, f"{team_meta_row.get('conf','')} · {team_meta_row.get('div','')}".strip(" ·"),
            color=FG, fontsize=22, fontweight="bold", ha="center", va="top", zorder=5)
    ax.text(0.5, 0.90, team_name.upper(), color=FG, fontsize=44, fontweight="bold",
            ha="center", va="top", zorder=5)
    ax.text(0.5, 0.75, f"TEMPORADA {season}", color=ACCENT, fontsize=24, fontweight="bold",
            ha="center", va="top", zorder=5)

    _tiles_grid(ax, tiles, y_top=0.66, y_bot=0.10, ncols=2)
    _footer(ax)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return G.fig_a_png(fig)
