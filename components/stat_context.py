"""components/stat_context.py — tarjeta "dato + contexto de liga" (DATOS -> CONTEXTO).

Envuelve analytics.context: si no hay contexto fiable (población insuficiente
o métrica no comparable), se muestra solo el valor, nunca un contexto inventado.
"""

from analytics.context import context_insight


def stat_context_html(label, value_str, ctx=None, unit="", decimals=1, subject="Este jugador"):
    """label: nombre de la métrica. value_str: valor ya formateado (ej. "250", "+0.21").
    ctx: dict de analytics.context.stat_context(), o None si no aplica."""
    unit_html = f' <span class="sxc-unit">{unit}</span>' if unit else ""
    if ctx is None:
        return (f'<div class="stat-context-card">'
                f'<div class="sxc-label">{label}</div>'
                f'<div class="sxc-value">{value_str}{unit_html}</div>'
                f'</div>')
    insight = context_insight(ctx, subject=subject)
    avg_str = f"{ctx['avg']:.{decimals}f}"
    return (
        f'<div class="stat-context-card">'
        f'<div class="sxc-label">{label}</div>'
        f'<div class="sxc-value">{value_str}{unit_html}</div>'
        f'<div class="sxc-row">'
        f'<div class="sxc-mini"><div class="sxc-mini-label">{ctx["label"].upper()} · MEDIA</div>'
        f'<div class="sxc-mini-value">{avg_str}{unit_html}</div></div>'
        f'<div class="sxc-mini"><div class="sxc-mini-label">PERCENTIL</div>'
        f'<div class="sxc-mini-value">{ctx["percentile"]:.0f}</div></div>'
        f'</div>'
        f'<div class="sxc-insight">🧠 {insight}</div>'
        f'<div class="sxc-pop">Comparado con {ctx["n"]} {ctx["label"].lower()} esta temporada.</div>'
        f'</div>'
    )
