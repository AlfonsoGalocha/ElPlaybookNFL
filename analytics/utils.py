"""analytics/utils.py — helpers puros compartidos entre modulos de analytics.

Nada de aqui importa streamlit: son funciones de dataframe a dataframe/dict,
para poder testearlas sin levantar la app.
"""


def mode(s):
    m = s.mode()
    return m.iloc[0] if len(m) else ""


def headshot_of(pdf, name):
    s = pdf[pdf.player_display_name == name]["headshot_url"].dropna()
    return s.iloc[0] if s.size else ""
