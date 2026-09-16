"""Catalogo cerrado de roles y tarifas.

Segunda pieza de la capa de contexto, separada de los ejemplos a proposito:
los ejemplos ensenan FORMATO, este catalogo fija DATOS.

El system prompt lo inyecta con instruccion explicita de no inventar roles ni
tarifas fuera de esta lista. Es la contramedida al problema detectado en la
primera prueba: el modelo imitaba las tarifas de un ejemplo y creaba roles
inexistentes.

Tarifas en ARS por hora. Fuente: propuestas comerciales de agosto 2026.
Revisar la vigencia antes de usar en produccion.
"""

ROLE_CATALOG = [
    {
        "codigo": "DIR",
        "rol": "Director de Tecnologia & IA",
        "perfil": "Direccion de proyecto y de solucion. Interlocucion ejecutiva con el cliente.",
        "tarifa_ars_hora": 196000,
    },
    {
        "codigo": "CPN",
        "rol": "Consultor/a de Procesos y Eficiencia",
        "perfil": "Relevamiento, GEMBA, mapeo de flujo, Lean/TOC, matriz de priorizacion, diseno del proceso.",
        "tarifa_ars_hora": 110000,
    },
    {
        "codigo": "ARQ",
        "rol": "Arquitecto/a de IA",
        "perfil": "Diseno tecnico de la solucion, decisiones de modelos y control de costos de operacion de IA.",
        "tarifa_ars_hora": 175000,
    },
    {
        "codigo": "ING",
        "rol": "Ingeniero/a de IA",
        "perfil": "Desarrollo de los pipelines y automatizaciones; soporte tecnico a tableros.",
        "tarifa_ars_hora": 196000,
    },
    {
        "codigo": "DAT",
        "rol": "Analista de Datos",
        "perfil": "Linea de base, indicadores y tableros construidos con IA sobre los datos disponibles.",
        "tarifa_ars_hora": 196000,
    },
    {
        "codigo": "QAV",
        "rol": "Analista QA / Validacion",
        "perfil": "Plan de validacion, pruebas por reproceso y revision en produccion.",
        "tarifa_ars_hora": 110000,
    },
    {
        "codigo": "GDC",
        "rol": "Especialista en Gestion del Cambio",
        "perfil": "Coordinacion, formacion y aseguramiento de la adopcion con los equipos del cliente.",
        "tarifa_ars_hora": 130000,
    },
]


def format_roles(catalog: list[dict] = ROLE_CATALOG) -> str:
    """Devuelve el catalogo como tabla markdown para inyectar en el system prompt."""
    filas = [
        "| Codigo | Rol | Perfil | Tarifa (ARS/h) |",
        "|--------|-----|--------|----------------|",
    ]
    for r in catalog:
        # Formato de miles con punto, aplicado SOLO al numero.
        tarifa = f"{r['tarifa_ars_hora']:,}".replace(",", ".")
        filas.append(f"| {r['codigo']} | {r['rol']} | {r['perfil']} | {tarifa} |")
    return "\n".join(filas)
