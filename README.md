# PoC — Servidor MCP de Actividad Comercial CRM

Servidor `FastMCP` que expone la actividad comercial del CRM (Dataverse) a agentes y clientes MCP mediante un endpoint HTTP remoto.

Objetivo:
- Servir datos de citas, llamadas, oportunidades, leads y ofertas filtrados por usuario
- Exponer convocatorias abiertas por sector y subvenciones BDNS por NIF
- Proporcionar resúmenes de noticias por cuenta
- Conectarse a clientes como ChatGPT, Claude o agentes internos mediante una URL MCP remota

Importante:
- El servidor no extrae datos del CRM en tiempo real
- Lee un fichero Excel generado previamente por el proceso de extracción (`scripts/main.py`)
- La superficie principal es MCP remoto por HTTP
- Soporta autenticación opcional por Bearer token

## Estructura

- `__main__.py`
  Arranque equivalente con `python -m poc_mcp`
- `main.py`
  Entrypoint ASGI/uvicorn
- `server.py`
  Servidor FastMCP, herramientas MCP y rutas auxiliares
- `service.py`
  Lectura y filtrado del Excel por email, NIF, sector y cuenta
- `auth.py`
  Middleware de autenticación Bearer token
- `config.py`
  Carga de variables de entorno y validación
- `api.py`
  Aplicación FastAPI auxiliar (si aplica)
- `requirements.txt`
  Dependencias de despliegue
- `.env.example`
  Variables de entorno de referencia
- `scripts/`
  Proceso de extracción que genera el Excel (`scripts/main.py`)
- `output/`
  Excel generado (`citas.xlsx`) que lee el servidor

## Variables de entorno

Copia `.env.example` a `.env` y rellena los valores.

### Dataverse

- `DATAVERSE_URL`
  URL del endpoint de Power Automate para acceso a Dataverse
- `TIMEOUT`
  Timeout en segundos para peticiones HTTP. Default: `60`

### BDNS

- `BDNS_SQL_SERVER`
- `BDNS_SQL_DATABASE`
- `BDNS_SQL_USERNAME`
- `BDNS_SQL_PASSWORD`
- `BDNS_SQL_DRIVER`
  Default: `ODBC Driver 18 for SQL Server`

### GRANTS

- `GRANTS_SQL_SERVER`
- `GRANTS_SQL_DATABASE`
- `GRANTS_SQL_USERNAME`
- `GRANTS_SQL_PASSWORD`
- `GRANTS_SQL_DRIVER`
  Default: `ODBC Driver 18 for SQL Server`

### Servidor

- `SERVER_NAME`
  Default: `CRM_MCP`
- `SERVER_VERSION`
  Default: `0.1.0`
- `HOST`
  Default: `0.0.0.0`
- `PORT`
  Default: `8000`
- `MCP_PATH`
  Default: `/mcp`
- `MCP_TRANSPORT`
  Default: `streamable-http`

### Autenticacion

- `MCP_AUTH_MODE`
  `none` o `bearer`. Default: `none`
- `MCP_BEARER_TOKEN`
  Obligatorio si `MCP_AUTH_MODE=bearer`

### Excel

- `EXCEL_PATH`
  Ruta al Excel generado por el proceso de extraccion. Dejar vacio para usar `output/citas.xlsx`

## Instalacion

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Arranque

### Paso 1 — Generar el Excel de datos

El servidor lee un fichero Excel generado por el script de extraccion. Ejecutarlo antes de arrancar el servidor:

```bash
python scripts/main.py
```

Genera `output/citas.xlsx` con una hoja por cada tipo de dato (citas, llamadas, oportunidades, leads, subvenciones, noticias).

### Paso 2 — Arrancar el servidor MCP

Opcion 1:

```bash
python __main__.py
```

Opcion 2:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Por defecto, el servidor MCP remoto queda expuesto en:

```
http://TU_HOST:8000/mcp
```

Esa es la URL que hay que registrar en el cliente MCP (ChatGPT, Claude, agente interno, etc.).

## Herramientas MCP

Todas las herramientas leen el Excel generado en el Paso 1. No realizan llamadas en tiempo real al CRM.

- `get_citas_semanales(email)` — Citas de la semana actual del usuario
- `get_citas_12_semanas(email)` — Citas de hace 12 semanas
- `get_historico_citas(email)` — Historico de citas de los ultimos 3 anos
- `get_historico_llamadas(email)` — Historico de llamadas de los ultimos 3 anos
- `get_historico_opps(email)` — Historico de servicios y oportunidades
- `get_llamadas_abiertas(email)` — Llamadas abiertas del usuario
- `get_leads_abiertos(email)` — Leads abiertos asignados al usuario
- `get_oportunidades_abiertas(email)` — Oportunidades abiertas del usuario
- `get_ofertas_pendientes(email)` — Ofertas pendientes de las ultimas 12 semanas
- `get_convocatorias_abiertas(sector_grants)` — Convocatorias abiertas por sector GRANTS
- `get_subvenciones_bdns(nif)` — Subvenciones BDNS recibidas por NIF
- `get_resumen_noticias(nombre_cuenta)` — Resumen de noticias por cuenta

## Endpoints auxiliares

- `GET /` — Nombre, version y URLs del servidor
- `GET /health` — Estado del servidor y si el Excel existe
- `GET /v1/capabilities` — Lista de herramientas MCP disponibles

## Autenticacion

Por defecto el servidor no requiere autenticacion (`MCP_AUTH_MODE=none`).

Para activar Bearer token:

```env
MCP_AUTH_MODE=bearer
MCP_BEARER_TOKEN=tu_token_secreto
```

Las rutas `/`, `/health` y `/v1/capabilities` son siempre publicas.
El endpoint `/mcp` queda protegido y requiere el header:

```
Authorization: Bearer tu_token_secreto
```

## Logs

- `logs/`

## Licencia

Interno - FI Group
