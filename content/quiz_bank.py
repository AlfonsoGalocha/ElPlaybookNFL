"""content/quiz_bank.py — banco de preguntas del Quiz, por nivel.

Cada pregunta: texto, lista de opciones, indice de la correcta, explicacion
que se muestra despues de responder.
"""

QUESTIONS = {
    "rookie": [
        {"q": "¿Cuántas yardas hay que avanzar para conseguir un first down?",
         "options": ["5 yardas", "10 yardas", "15 yardas", "20 yardas"],
         "correct": 1,
         "explain": "Un equipo tiene 4 downs para avanzar 10 yardas. Si lo consigue, obtiene un nuevo "
                     "first down y otros 4 intentos."},
        {"q": "¿Cuántos puntos vale un touchdown, sin contar el punto/conversión extra?",
         "options": ["3 puntos", "5 puntos", "6 puntos", "7 puntos"],
         "correct": 2,
         "explain": "El touchdown vale 6 puntos. Después se añade 1 punto (extra point) o 2 (conversión "
                     "de 2 puntos) según lo que intente el equipo."},
        {"q": "¿Qué jugador dirige el ataque y decide si pasa, corre o entrega el balón?",
         "options": ["El center", "El quarterback (QB)", "El safety", "El kicker"],
         "correct": 1,
         "explain": "El quarterback recibe el balón en cada jugada y toma la decisión clave del ataque."},
        {"q": "¿Qué es un turnover?",
         "options": ["Un cambio de cuarto", "Una pérdida de balón (intercepción o fumble)",
                     "Un cambio de entrenador", "Un timeout"],
         "correct": 1,
         "explain": "Un turnover es perder la posesión del balón antes de anotar: por intercepción "
                     "(pase capturado por la defensa) o por fumble (balón suelto que recupera el rival)."},
        {"q": "¿Cuántos puntos vale un field goal?",
         "options": ["1 punto", "2 puntos", "3 puntos", "6 puntos"],
         "correct": 2,
         "explain": "El field goal (patear el balón entre los postes) vale 3 puntos."},
    ],
    "aficionado": [
        {"q": "¿Qué es un 'blitz'?",
         "options": ["Una jugada de carrera rápida", "Enviar más defensores de lo normal a presionar al QB",
                     "Un tipo de bloqueo ofensivo", "Un cambio de formación en ataque"],
         "correct": 1,
         "explain": "En un blitz, la defensa manda jugadores extra a por el QB, arriesgando cobertura "
                     "a cambio de presión rápida."},
        {"q": "¿Qué busca conseguir un 'play action'?",
         "options": ["Que la defensa muerda el amago de carrera y se abra el pase",
                     "Ganar tiempo cuando va perdiendo", "Evitar un field goal", "Forzar un cambio de posesión"],
         "correct": 0,
         "explain": "El QB finge una entrega de balón para que la defensa reaccione a la carrera, "
                     "dejando más espacio para el pase."},
        {"q": "En un RPO (Run-Pass Option), ¿quién decide si es carrera o pase?",
         "options": ["El entrenador, antes de la jugada", "El QB, leyendo a un defensor tras el snap",
                     "El center", "Se decide siempre en el huddle"],
         "correct": 1,
         "explain": "En el RPO, el QB ya tiene el balón y decide sobre la marcha según cómo reacciona "
                     "un defensor clave."},
        {"q": "¿Qué es la 'zona roja' (red zone)?",
         "options": ["Las últimas 20 yardas antes de la end zone rival", "El área detrás del QB",
                     "La zona donde se calienta el banquillo", "Las primeras 10 yardas del campo propio"],
         "correct": 0,
         "explain": "La zona roja son las últimas 20 yardas antes de anotar: el campo se hace pequeño "
                     "y suele ser más difícil convertir en touchdown."},
        {"q": "¿Por qué es tan importante el tercer down (3rd down)?",
         "options": ["Porque ahí siempre hay touchdown", "Porque si no se convierte, casi siempre toca "
                     "despejar o intentar field goal", "Porque dura más tiempo", "Porque no se puede pasar"],
         "correct": 1,
         "explain": "El 3er down suele ser la última oportunidad razonable de mantener la posesión: "
                     "fallar ahí normalmente significa entregar el balón al rival."},
    ],
    "avanzado": [
        {"q": "¿Qué mide el EPA (Expected Points Added)?",
         "options": ["Los puntos totales del partido", "Cuánto suma o resta una jugada respecto a lo "
                     "esperado en esa situación", "El tiempo de posesión", "El número de yardas por partido"],
         "correct": 1,
         "explain": "El EPA compara el resultado real de una jugada con los puntos esperados según down, "
                     "distancia y posición en el campo antes de esa jugada."},
        {"q": "¿Qué indica un CPOE alto en un quarterback?",
         "options": ["Que lanza muy lejos siempre", "Que completa más pases de lo esperado según la "
                     "dificultad de cada uno", "Que corre mucho", "Que nunca es interceptado"],
         "correct": 1,
         "explain": "El CPOE compara el % de acierto real con el % esperado según la dificultad de cada "
                     "pase (distancia, presión, cobertura...), así que mide precisión real, no solo volumen."},
        {"q": "¿Qué son los 'Air Yards' de un pase?",
         "options": ["Las yardas totales de la jugada", "Las yardas que recorre el balón en el aire "
                     "hasta el punto de recepción", "Las yardas después de la recepción", "El tiempo en el aire"],
         "correct": 1,
         "explain": "Air Yards mide solo el vuelo del balón; lo que el receptor avanza después se llama "
                     "YAC (Yards After Catch)."},
        {"q": "¿Qué mide el 'Success Rate' (% de éxito) de una jugada?",
         "options": ["Si terminó en touchdown", "Si la jugada cumplió el umbral de yardas esperado "
                     "según el down", "El número de defensores en la jugada", "Si hubo penalización"],
         "correct": 1,
         "explain": "Una jugada 'exitosa' suele definirse como ganar el 40% de las yardas necesarias en "
                     "1er down, el 60% en 2º, o el 100% en 3º/4º."},
    ],
}

LEVEL_LABELS = {"rookie": "Rookie", "aficionado": "Aficionado", "avanzado": "Avanzado"}
