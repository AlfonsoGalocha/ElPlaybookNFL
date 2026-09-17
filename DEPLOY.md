# Despliegue — El Playbook NFL

Esta guía cubre desarrollo local, Docker y el camino conceptual hacia producción
con dominio propio. La app sigue siendo 100% Streamlit — no hay build de
frontend aparte ni backend separado.

## Desarrollo local

Requisitos: Python 3.12 (el proyecto fija `3.12` en `.python-version`; también
funciona en 3.11+).

```bash
pip install -r requirements.txt
streamlit run panel_nfl.py
```

Abre `http://localhost:8501`. Los datos de la NFL se descargan la primera vez
(nflreadpy) y quedan cacheados en memoria durante la sesión del proceso.

### Variables de entorno (opcionales)

Copia `.env.example` a `.env` y rellena solo lo que necesites — la app arranca
y funciona igual sin ningún `.env`. Ahora mismo controlan integraciones
todavía desactivadas (Analytics, Search Console, AdSense) y datos de contacto
para las páginas legales. Streamlit no carga `.env` automáticamente: si usas
uno, expórtalo antes de arrancar (`export $(cat .env | xargs)` en local, o
`--env-file .env` con Docker).

## Docker

### 1. Construir la imagen

```bash
docker build -t elplaybooknfl .
```

La imagen parte de `mirror.gcr.io/library/python:3.12-slim` (mismo Python
oficial, vía el mirror público de Google para evitar los límites de pull
anónimo de Docker Hub en CI). Si prefieres tirar directo de Docker Hub, cambia
la línea `FROM` por `python:3.12-slim`.

### 2. Ejecutarla en local

```bash
docker run -p 8501:8501 elplaybooknfl
```

Abre `http://localhost:8501`.

Para probar el arranque dinámico de puerto (como hacen Cloud Run y hostings
similares, que inyectan `$PORT`):

```bash
docker run -e PORT=9000 -p 8501:9000 elplaybooknfl
```

### 3. Comprobar que funciona

```bash
curl http://localhost:8501/_stcore/health
# -> ok
```

`docker ps` también debería mostrar el contenedor como `(healthy)` pasados
unos ~20 segundos (el `HEALTHCHECK` del Dockerfile usa ese mismo endpoint,
propio de Streamlit — no se ha tocado la app para esto).

### 4. Detenerla

```bash
docker ps                 # localizar el CONTAINER ID o nombre
docker stop <id-o-nombre>
```

## Producción (conceptual)

```
GitHub (código)
   ↓
Docker (build de la imagen, este Dockerfile)
   ↓
Hosting compatible con contenedores (Cloud Run, Render, Fly.io, un VPS
   con Docker, etc. — a elegir; no se asume ninguno)
   ↓
Reverse proxy / HTTPS (lo gestiona el propio hosting, o nginx/Caddy si es
   un VPS — certificado TLS, terminación de WebSocket)
   ↓
Dominio propio (elplaybooknfl.com / www.elplaybooknfl.com, vía DNS)
   ↓
El Playbook NFL
```

### Notas para quien configure el reverse proxy / hosting

- **Puerto:** el contenedor escucha en `$PORT` (por defecto 8501) y en
  `0.0.0.0` — ya preparado para cualquier proxy/orquestador que lo invoque.
- **WebSocket:** Streamlit necesita una conexión WebSocket persistente entre
  el navegador y el servidor. La mayoría de proxies modernos (Cloud Run,
  nginx, Caddy, Traefik) lo soportan, pero nginx concretamente requiere
  las cabeceras `Upgrade`/`Connection` explícitas:
  ```nginx
  location / {
      proxy_pass http://127.0.0.1:8501;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
  }
  ```
- **CORS / XSRF:** `.streamlit/config.toml` deja ambos en su valor seguro por
  defecto (`true`). Si el proxy reenvía las peticiones de forma transparente
  (el navegador solo ve el dominio público), no hace falta tocar nada. Si tras
  poner el proxy delante ves errores de conexión del WebSocket o de subida de
  archivos, revisa que el proxy no esté reescribiendo las cabeceras
  `Origin`/`Host` — desactivar `enableCORS` desactiva también `enableXsrfProtection`
  en Streamlit, así que solo tocarlo como último recurso.
- **`allowedHosts`:** vacío por defecto (acepta cualquier Host header), a
  propósito mientras el dominio final no esté listo — así puedes probar el
  despliegue por la URL temporal del hosting. Una vez `elplaybooknfl.com` y
  `www.elplaybooknfl.com` estén en DNS y sean el único punto de acceso, puedes
  endurecerlo en `.streamlit/config.toml`:
  ```toml
  allowedHosts = ["elplaybooknfl.com", "www.elplaybooknfl.com"]
  ```
- **`ads.txt` y verificación de dominio por archivo:** Streamlit no sirve
  archivos estáticos en la raíz del dominio (`/ads.txt`,
  `/googleXXXX.html`). Estos deben servirse desde el reverse proxy o el
  hosting (por ejemplo, una regla de nginx que devuelva el contenido de
  `ads.txt` directamente, o un bucket estático delante del proxy). La
  verificación de Search Console por meta-tag y el script de AdSense/Analytics
  sí puede inyectarlos la propia app — ver `components/head_tags.py` y las
  variables `GOOGLE_SITE_VERIFICATION` / `GOOGLE_ANALYTICS_ID` /
  `GOOGLE_ADSENSE_PUBLISHER_ID` en `.env.example`.
- **`www` vs raíz:** decide un dominio canónico (normalmente
  `www.elplaybooknfl.com` → `elplaybooknfl.com`, o al revés) y haz que el
  hosting/proxy redirija 301 el que no uses hacia el canónico. Streamlit no
  necesita saber cuál es — es puramente configuración de DNS/proxy.

## Próximo paso recomendado

Para quien quiera desplegar ya mismo sin decidir infraestructura desde cero,
la ruta más simple con este `Dockerfile` tal cual es un hosting que construya
y ejecute contenedores directamente desde el repositorio (p. ej. Google Cloud
Run, Render, Railway o Fly.io):

1. Conectar el repositorio de GitHub al hosting elegido.
2. Confirmar que detecta el `Dockerfile` (todos los mencionados lo hacen
   automáticamente) o apuntarlo explícitamente.
3. Configurar la variable `PORT` si el hosting no la inyecta ya (Cloud Run,
   Render y Railway lo hacen solos).
4. Desplegar y verificar `/_stcore/health` desde la URL temporal que dé el
   hosting.
5. Apuntar `elplaybooknfl.com`/`www.elplaybooknfl.com` (comprados aparte) al
   hosting siguiendo sus instrucciones de dominio propio — la mayoría
   gestionan el certificado HTTPS automáticamente en cuanto el DNS resuelve.
6. Solo entonces, revisar `allowedHosts` (sección anterior) y las páginas
   legales (`pages_app/legal.py`) antes de solicitar Google Search Console /
   AdSense.

No se ha ejecutado ningún despliegue real — esto es la guía para que el
propietario del proyecto lo haga cuando decida el proveedor.
