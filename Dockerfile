# syntax=docker/dockerfile:1

# El Playbook NFL — imagen de produccion (Streamlit).
#
# Build:  docker build -t elplaybooknfl .
# Run:    docker run -p 8501:8501 elplaybooknfl
# Ver DEPLOY.md para instrucciones completas (build/run/healthcheck/produccion).

# mirror.gcr.io es el mirror publico de Docker Hub de Google: misma imagen
# oficial, pero evita los limites de pull anonimo de Docker Hub en CI/build
# automatizados. Cambia a "python:3.12-slim" sin problema si prefieres tirar
# directo de Docker Hub.
FROM mirror.gcr.io/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Copiar solo requirements.txt primero: mientras no cambien las dependencias,
# Docker reutiliza esta capa en builds sucesivos y no reinstala nada.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Resto del codigo de la app (ver .dockerignore para lo que se excluye).
COPY . .

# No ejecutar como root dentro del contenedor.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Puerto por defecto/documental — en produccion manda $PORT (ver CMD).
EXPOSE 8501

# Streamlit expone un endpoint de salud propio (sin tocar la app):
# https://docs.streamlit.io/develop/api-reference/utilities/st.health
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "\
import os, sys, urllib.request; \
port = os.environ.get('PORT', '8501'); \
urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=3)" || exit 1

# Forma shell para que ${PORT:-8501} se resuelva en tiempo de arranque: la
# mayoria de hostings basados en contenedores (Cloud Run y similares)
# inyectan $PORT y esperan que el proceso escuche exactamente ahi.
CMD ["sh", "-c", "streamlit run panel_nfl.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
