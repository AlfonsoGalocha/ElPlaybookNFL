"""analytics/context.py — contexto estadístico (media de liga + percentil) sobre una población
comparable real (misma posición exacta para jugadores, todos los equipos para stats de equipo).

Principio: DATOS -> CONTEXTO. Nunca se inventa un promedio ni un percentil.
Si la población disponible es demasiado pequeña o la columna no existe,
las funciones devuelven None y quien las llama debe simplemente no
mostrar el contexto (nunca rellenar con un valor inventado).
"""

import numpy as np

MIN_POPULATION = 5  # con menos de 5 comparables, un percentil no es fiable


def position_population(totals_df, position):
    """Subconjunto de un DataFrame de totales (full_totals_table) con la misma posición exacta."""
    if totals_df is None or "position" not in totals_df.columns:
        return None
    return totals_df[totals_df.position == position]


def stat_context(population, value_col, target_value, population_label, min_population=MIN_POPULATION):
    """Calcula media y percentil de target_value dentro de population[value_col].

    Devuelve dict(avg, percentile, n, label) o None si no hay población
    suficiente, la columna no existe, o target_value no es un número valido.
    """
    if population is None or value_col not in population.columns:
        return None
    if target_value is None or not np.isfinite(target_value):
        return None
    vals = population[value_col].dropna()
    vals = vals[np.isfinite(vals)]
    if len(vals) < min_population:
        return None
    avg = float(vals.mean())
    percentile = float((vals <= target_value).mean() * 100)
    return {"avg": avg, "percentile": percentile, "n": int(len(vals)),
            "label": population_label, "value": float(target_value)}


def context_insight(ctx, subject="Este jugador"):
    """Frase determinista a partir del percentil ya calculado (nunca inventa el dato, solo lo describe)."""
    if ctx is None:
        return None
    p = ctx["percentile"]
    if p >= 90:
        return f"{subject} está entre lo mejor de la liga en esta métrica."
    if p >= 70:
        return f"{subject} está por encima de la media de la liga."
    if p >= 40:
        return f"{subject} está en línea con la media de la liga."
    if p >= 20:
        return f"{subject} está por debajo de la media de la liga."
    return f"{subject} está entre lo más bajo de la liga en esta métrica."
