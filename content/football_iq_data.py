"""content/football_iq_data.py — glosario y lecciones de Football IQ.

Contenido puro (listas/diccionarios), sin logica de UI, para poder ampliarlo
sin tocar pages_app/football_iq.py.
"""

LEVELS = {
    "rookie": {
        "title": "Rookie",
        "css": "iq-rookie",
        "tagline": "Si vienes del fútbol y quieres entender qué está pasando en el campo.",
        "terms": [
            {"term": "Down", "def": "Cada uno de los 4 intentos que tiene un equipo para avanzar "
             "10 yardas. Si lo consigue, obtiene un 'first down' y otros 4 intentos. Si no, pierde el balón.",
             "example": "1er down y 10 significa: primer intento, faltan 10 yardas para el first down."},
            {"term": "First down", "def": "Avanzar al menos 10 yardas dentro de los 4 downs disponibles. "
             "Es el objetivo constante del ataque, equivalente a 'mantener la posesión avanzando'.",
             "example": "Si en 3 downs el equipo ya ha avanzado 10 yardas, consigue first down y downs nuevos."},
            {"term": "Touchdown", "def": "Llevar el balón a la end zone rival (o recibirlo/interceptarlo ahí). "
             "Vale 6 puntos, más el intento de punto extra (1) o de conversión de 2 puntos (2).",
             "example": "Equivalente a un gol, pero vale 6-8 puntos según cómo se complete después."},
            {"term": "Quarterback (QB)", "def": "El jugador que dirige el ataque: recibe el balón del "
             "center en cada jugada y decide si pasa, corre o entrega el balón.",
             "example": "Es la posición más determinante del equipo, similar al '10' en el fútbol."},
            {"term": "Running Back (RB)", "def": "Jugador especializado en correr con el balón tras "
             "recibirlo del QB, y también en bloquear o recibir pases cortos.",
             "example": "El equivalente más cercano sería un delantero muy físico que también defiende."},
            {"term": "Wide Receiver (WR) / Tight End (TE)", "def": "Jugadores que se alinean abiertos "
             "(WR) o cerca de la línea (TE) para recibir pases del QB.",
             "example": "Los TE también bloquean, como un extremo que a veces hace de lateral."},
            {"term": "Línea ofensiva / defensiva", "def": "Los jugadores más grandes, en el centro del "
             "campo, que bloquean (ataque) o intentan atrapar al QB (defensa) en cada jugada.",
             "example": "Nadie ve el balón, pero sin ellos no hay jugada: son el trabajo invisible."},
            {"term": "Cuartos y reloj", "def": "El partido dura 4 cuartos de 15 minutos. El reloj se "
             "para en incompletos, fuera de banda, penaltis y algunas situaciones más.",
             "example": "Por eso un partido de '60 minutos' dura en TV más de 3 horas."},
            {"term": "Field goal", "def": "Patear el balón entre los postes para anotar 3 puntos, "
             "normalmente cuando el ataque no llega a touchdown pero está cerca.",
             "example": "La alternativa 'segura' a seguir intentando el touchdown en 4º down."},
            {"term": "Turnover (pérdida de balón)", "def": "El ataque pierde el balón antes de anotar, "
             "por intercepción (pase capturado por la defensa) o fumble (balón que se cae y recupera el rival).",
             "example": "El equivalente a perder el balón en campo propio: cambia el partido de golpe."},
        ],
    },
    "aficionado": {
        "title": "Aficionado",
        "css": "iq-aficionado",
        "tagline": "Ya entiendes lo básico. Ahora, las decisiones tácticas detrás de cada jugada.",
        "terms": [
            {"term": "Blitz", "def": "La defensa envía más jugadores de lo habitual a presionar al QB, "
             "arriesgando cobertura a cambio de generar una jugada rápida en su contra.",
             "example": "Un 'todos al ataque' defensivo: alta recompensa, pero deja huecos si el QB escapa."},
            {"term": "Cover 2", "def": "Esquema de cobertura con 2 safeties que dividen el campo profundo "
             "en dos mitades, y el resto de la defensa cubre zonas más cortas.",
             "example": "Fuerte contra pases largos por el centro, más vulnerable en las bandas profundas."},
            {"term": "Cover 3", "def": "Esquema de cobertura con 3 defensores cubriendo el campo profundo "
             "en tres tercios (dos esquinas y un safety), dejando más apoyo cerca de la línea.",
             "example": "Muy usado para frenar el juego terrestre sin renunciar a cobertura profunda."},
            {"term": "Play action", "def": "El QB finge una entrega de balón (como si fuera a correr) "
             "antes de pasar, para que la defensa 'muerda' el amago y se abran huecos en el pase.",
             "example": "Un engaño clásico: si la defensa respeta la carrera, el pase queda más libre."},
            {"term": "RPO (Run-Pass Option)", "def": "Jugada donde el QB decide, ya con el balón en la "
             "mano y leyendo a un defensor clave, si entrega el balón para correr o pasa.",
             "example": "Combina las dos amenazas en una sola jugada, muy común en el fútbol americano moderno."},
            {"term": "Pocket", "def": "El espacio protegido que forma la línea ofensiva alrededor del QB "
             "para darle tiempo a pasar sin que lo derriben.",
             "example": "'Salir del pocket' significa que el QB tiene que moverse porque ese espacio se rompió."},
            {"term": "Zona roja (Red zone)", "def": "Las últimas 20 yardas antes de la end zone rival. "
             "El campo se hace más pequeño y es más difícil anotar touchdown (y más fácil defenderlo).",
             "example": "El '% de touchdown en zona roja' mide cuántas veces el ataque remata sus acercamientos."},
            {"term": "Tercer down (3rd down)", "def": "El down más decisivo: si el ataque no consigue "
             "el first down, casi siempre tiene que despejar (punt) o intentar un field goal.",
             "example": "El '% de acierto en 3ª down' es uno de los indicadores más citados de un ataque."},
            {"term": "Screen pass", "def": "Pase corto y rápido a un receptor o corredor que tiene "
             "bloqueadores esperándolo delante, pensado para ganar yardas después de la recepción.",
             "example": "Sirve también para castigar a una defensa que presiona demasiado (blitz)."},
            {"term": "No huddle", "def": "El ataque no se junta a decidir la jugada entre jugada y jugada: "
             "va directo a la línea para jugar rápido y no dar tiempo a la defensa a ajustarse.",
             "example": "Se usa mucho al final del partido con prisa, pero también como ritmo constante."},
        ],
    },
    "avanzado": {
        "title": "Avanzado",
        "css": "iq-avanzado",
        "tagline": "Las métricas que usamos en el Laboratorio, explicadas con datos reales de esta temporada.",
        "terms": [
            {"term": "EPA (Expected Points Added)", "def": "Cuántos puntos esperados gana o pierde un "
             "equipo con una jugada concreta, comparado con lo esperado en esa situación (down, distancia, "
             "campo). Es la métrica base para medir eficiencia jugada a jugada.",
             "example": "Un EPA/jugada positivo en ataque significa que, de media, cada jugada suma valor."},
            {"term": "CPOE (Completion % Over Expected)", "def": "Cuánto mejor (o peor) completa un QB "
             "sus pases comparado con lo que se esperaría según la dificultad de cada pase (distancia, "
             "presión, cobertura).",
             "example": "Un CPOE alto indica precisión real, no solo pases fáciles y cortos."},
            {"term": "Success Rate (% de éxito)", "def": "Porcentaje de jugadas consideradas 'exitosas' "
             "según el down: normalmente, ganar el 40% de las yardas necesarias en 1er down, el 60% en "
             "2º, y el 100% (first down) en 3º y 4º.",
             "example": "Complementa al EPA: muestra consistencia, no solo jugadas explosivas puntuales."},
            {"term": "Air Yards", "def": "Yardas que recorre el balón en el aire hasta donde se completa "
             "(o falla) el pase, sin contar lo que el receptor avanza después (YAC).",
             "example": "Un QB con muchos air yards de media tira más profundo que uno que juega corto."},
            {"term": "YAC (Yards After Catch)", "def": "Yardas que gana el receptor después de atrapar "
             "el balón, corriendo con él.",
             "example": "Mide el aporte del propio jugador más allá de la precisión del pase."},
            {"term": "Pressure Rate", "def": "Porcentaje de jugadas de pase en las que el QB sufre presión "
             "(placaje, golpe o forzado a moverse) antes de soltar el balón, según el charting de PFR.",
             "example": "Un pass rush que genera mucha presión no siempre acaba en sacks, pero rompe el ritmo."},
            {"term": "WPA (Win Probability Added)", "def": "Cuánto cambia la probabilidad de ganar el "
             "partido con una jugada concreta, teniendo en cuenta marcador, tiempo restante y situación.",
             "example": "Una jugada con poco EPA puede tener mucho WPA si pasa en un momento decisivo."},
        ],
    },
}

LEVEL_ORDER = ["rookie", "aficionado", "avanzado"]
