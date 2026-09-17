# Estimador CAG

Servicio que recibe la transcripción de una reunión con un cliente y devuelve una
estimación de esfuerzo y costo generada por un LLM.

Entrega de la **Sesión 2 — Arquitectura CAG** del Máster en AI Engineering (LIDR).

---

## Qué es CAG y por qué acá

**CAG** (Cache-Augmented Generation) inyecta todo el conocimiento del sistema
directamente en el prompt, en cada llamada. No hay base de datos, ni búsqueda
semántica, ni recuperación dinámica: el contexto es estático y vive en el código.

El conocimiento de este sistema son dos cosas distintas, deliberadamente separadas:

- **`context/examples.py`** — estimaciones previas completas. Enseñan **formato**:
  estructura del desglose, nivel de detalle, qué secciones debe tener una estimación
  defendible.
- **`context/rates.py`** — catálogo cerrado de roles y tarifas. Fija **datos**.

La separación no es cosmética. En la primera prueba, con solo los ejemplos, el modelo
reutilizó las tarifas de un caso en otro distinto e inventó roles que no existen.
El catálogo con instrucción explícita de no salirse de él es la contramedida.

**El trade-off que CAG impone:** el contexto completo (~2.800 tokens entre ejemplos y
catálogo) se paga en cada llamada, aunque la transcripción sea de tres líneas. A cambio,
cero infraestructura de datos y cero latencia de recuperación. Es la decisión correcta
mientras el volumen de ejemplos sea chico y la calidad dependa de iterarlos a mano.

Cuando el número de ejemplos crezca, `context/` es el punto de sustitución limpio hacia
RAG: se reemplaza por un servicio de búsqueda que recupera solo los ejemplos relevantes,
sin tocar el resto del sistema.

---

## Arquitectura

```
estimador-cag/
├── app/
│   ├── main.py              Punto de entrada. Registra el router, expone /health
│   ├── config.py            Configuración con Pydantic BaseSettings
│   ├── routers/
│   │   └── estimations.py   Capa HTTP: recibe, delega, devuelve
│   ├── services/
│   │   ├── llm_service.py   Lógica de negocio: prompt, llamada al modelo, respuesta
│   │   └── pricing.py       Cálculo de costo por modelo
│   ├── schemas/
│   │   └── estimation.py    Contratos de entrada y salida (Pydantic)
│   └── context/
│       ├── examples.py      Estimaciones de referencia (formato)
│       └── rates.py         Catálogo de roles y tarifas (datos)
├── probar.py                Cliente de prueba con transcripción desde archivo
├── transcripcion_reunion.txt
├── .env.example
└── pyproject.toml
```

**Responsabilidades, y qué NO hace cada capa:**

| Capa | Responsabilidad | Lo que no hace |
|------|-----------------|----------------|
| `routers/` | Comunicación HTTP | No construye prompts ni llama al LLM |
| `services/` | Prompt, llamada al modelo, procesamiento | No sabe nada de HTTP |
| `schemas/` | Validación y contrato de la API | No contiene lógica |
| `context/` | Datos estáticos a inyectar | No decide cómo se usan |

Cambiar de modelo, de proveedor o de estrategia de prompt no toca `routers/`.
Reemplazar CAG por RAG no toca `services/` más allá del origen de los ejemplos.

---

## Puesta en marcha

**Requisitos:** Python 3.11+, [uv](https://docs.astral.sh/uv/), y una API key de
Anthropic con crédito disponible.

```bash
uv sync
cp .env.example .env     # completar ANTHROPIC_API_KEY
uv run uvicorn app.main:app --reload --reload-dir app
```

> `--reload-dir app` limita el vigilante de cambios al código propio. Sin eso, uvicorn
> vigila también `.venv` y se reinicia en bucle.

Documentación interactiva en `http://127.0.0.1:8000/docs`.

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Verificación de estado |
| POST | `/api/v1/estimate` | Recibe una transcripción, devuelve la estimación |

**Ejemplo de respuesta:**

```json
{
  "estimation": "## Estimación: ...",
  "model": "claude-haiku-4-5",
  "provider": "anthropic",
  "input_tokens": 15857,
  "output_tokens": 2000,
  "cost_usd": 0.025857,
  "latency_ms": 18420
}
```

### Prueba con una transcripción larga

```bash
uv run python probar.py
```

Lee `transcripcion_reunion.txt` y arma el JSON con `json.dumps`, que escapa los saltos
de línea. Pegar una transcripción multilínea a mano en Swagger produce un 422: JSON no
admite caracteres de control literales dentro de una cadena.

---

## Decisiones de diseño

**Configuración que falla al arrancar.** `ANTHROPIC_API_KEY` se declara obligatoria en
`Settings`. Si falta, la aplicación no levanta — en vez de fallar en la primera petición
de un usuario.

**El system prompt como contrato, no como sugerencia.** El prompt declara el catálogo de
roles como única fuente válida y prohíbe explícitamente inventar roles o tarifas. También
instruye a declarar un supuesto explícito cuando la transcripción no alcanza, en lugar de
completar con invención.

**Precios indexados por modelo, no configurables.** `pricing.py` mantiene una tabla por
modelo y devuelve `None` si el modelo no está registrado. Un precio es un hecho del
proveedor, no una preferencia: ponerlo en el `.env` invita a que quede desincronizado del
modelo en uso y a informar un costo falso con apariencia de exacto. Preferimos informar
"no sé".

**Tres métricas en cada respuesta.** Tokens de entrada y salida (medidos, no estimados),
costo en USD y latencia en milisegundos. Son los tres ejes del trade-off que CAG obliga a
gobernar.

**Latencia medida solo sobre la llamada al LLM**, con `time.perf_counter()` — contador
monótono, no el reloj del sistema. Armar el prompt tarda microsegundos y mezclarlo
ensuciaría el dato.

---

## Limitaciones conocidas

**Sin manejo de errores del proveedor.** Cualquier fallo de la API —modelo inválido,
sin crédito, rate limit, timeout— sale como un 500 genérico sin información útil. Es la
carencia más seria para un uso real.

**La restricción del catálogo es blanda.** Está expresada en el prompt, y un prompt es
una instrucción, no una garantía. La restricción dura requiere validar la salida en
código contra la lista de roles: verificar que todo rol mencionado exista y que su tarifa
coincida. No implementado.

**Sin prompt caching.** El prefijo del prompt es perfectamente estable y la cola
(transcripción) es lo único volátil: es el caso de libro para caching, que reduce el
costo del contexto repetido a una décima parte. Pendiente de evaluar contra el volumen
real.

**Acoplado a Anthropic.** El servicio usa el SDK de Anthropic directamente. Una capa
agregadora (LiteLLM u OpenRouter) permitiría comparar proveedores con el mismo prompt.
Las variables de OpenAI están declaradas en la configuración pero no se usan.

**Sin evaluación automática de la calidad** de las estimaciones generadas.

**Sin pipeline de integración continua.** El enunciado lo pedía como extra.

---

## Sobre los datos

Los ejemplos de `context/examples.py` derivan de propuestas comerciales reales,
**anonimizadas**: nombres de cliente reemplazados, estructura y cifras conservadas.

`transcripcion_reunion.txt` es una transcripción real de una reunión de 53 minutos, con
nombres de participantes y del cliente reemplazados por identificadores genéricos.

---

## Observaciones sobre el material del curso

Dos puntos detectados al implementar, que pueden servir al equipo:

- El SDK de Anthropic (versión 1.6.0) **no acepta el parámetro `temperature`** en
  `messages.create()`. Es un parámetro estándar en la API de OpenAI y su ausencia acá
  rompe la llamada con `TypeError`.
- El ejemplo de `config.py` de la lección de arquitectura usa `class Config:` para el
  `env_file`. Es la sintaxis de Pydantic v1; en pydantic-settings 2.x corresponde
  `model_config = SettingsConfigDict(...)`. La forma vieja todavía funciona, pero está
  deprecada.

Además, la lección define `build_system_prompt()` llamando a una función `format_examples()`
que nunca declara, y marca `generate_estimation` como `async` mientras usa un cliente
síncrono. Acá se usa `AsyncAnthropic` con `await`, coherente con el argumento de la propia
lección sobre por qué FastAPI para cargas con LLM.
