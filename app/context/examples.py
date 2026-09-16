"""Capa de contexto (CAG).

Estos ejemplos se inyectan completos en el system prompt en cada llamada.
Son estimaciones reales de Blecx, resumidas: el modelo imita su formato,
su nivel de desglose y su criterio de tarifas.

Cuando el proyecto evolucione a RAG, esta capa se reemplaza por una
busqueda semantica que recupere solo los ejemplos relevantes.
"""

ESTIMATION_EXAMPLES = [
    {
        "meeting_summary": (
            "Empresa1 - Division Personal Temporario. Procesan entre 6.500 y 7.000 novedades "
            "de nomina por mes de unos 300 clientes, cada uno con su propio formato: planilla "
            "Excel, cuerpo del correo, PDF escaneado, foto de papel o llamada telefonica. "
            "Alrededor de la mitad de los clientes manda un formato distinto cada mes. Toda la "
            "carga se concentra en una ventana de 3 a 4 dias porque la liquidacion cierra el "
            "tercer dia habil. Tres equipos sostienen el proceso: 30 personas en sucursales que "
            "reciben y completan, 4 personas que transforman los 300 formatos al unico Excel que "
            "acepta el sistema, y un equipo de validacion final. El cuello de botella declarado "
            "por el cliente es llegar a ese Excel; una vez armado, el resto del proceso funciona. "
            "No hay linea de base medida ni trazabilidad, y las reglas de cada cliente estan en la "
            "cabeza del equipo. Condiciones: la validacion final debe seguir siendo humana, la "
            "infraestructura es Azure, y el vinculo del cliente con su referente no puede cambiar."
        ),
        "estimation": """## Estimacion: Automatizacion de novedades de nomina (Empresa1)

Estrategia en dos opciones contratables por separado. La Opcion A cierra el alcance
de la B, que se cotiza con rango +/-10% hasta cerrar el discovery.

### Opcion A - Discovery (2 semanas, precio cerrado)

| Rol | Tarifa (ARS/h) | Horas | Subtotal (ARS) |
|-----|----------------|-------|----------------|
| Consultor/a de Procesos | 120.000 | 49 | 5.880.000 |
| Director de Tecnologia & IA | 180.000 | 19 | 3.420.000 |
| Arquitecto/a de IA | 175.000 | 18 | 3.150.000 |
| Ingeniero/a de IA | 120.000 | 4 | 480.000 |
| Analista QA / Validacion | 110.000 | 4 | 440.000 |

**Subtotal A: 94 horas - ARS 13.370.000**

Fases: preparacion y analisis de materiales (F0) / seleccion de la muestra de clientes
con GEMBA y sesion con el equipo (F1) / blueprint, diseno tecnico del pipeline sobre
Azure, plan de validacion y presupuesto cerrado (F2).

### Opcion B - Wave 1 de automatizacion (8 semanas)

| Rol | Tarifa (ARS/h) | Horas | Subtotal (ARS) |
|-----|----------------|-------|----------------|
| Ingeniero/a de IA | 120.000 | 264 | 31.680.000 |
| Arquitecto/a de IA | 175.000 | 42 | 7.350.000 |
| Analista QA / Validacion | 110.000 | 50 | 5.500.000 |
| Director de Tecnologia & IA | 180.000 | 20 | 3.600.000 |
| Especialista en Gestion del Cambio | 130.000 | 20 | 2.600.000 |
| Consultor/a de Procesos | 120.000 | 6 | 720.000 |

**Subtotal B: 402 horas - ARS 51.450.000** (rango -10% / +10%)

Fases: desarrollo del pipeline, extraccion multiformato, motor de reglas por cliente y
deteccion de confianza (F3) / validacion por reproceso contra historia hasta alcanzar los
umbrales acordados (F4) / produccion acompanada con el equipo operando el nuevo flujo (F5).

### Total del programa

**496 horas - ARS 64.820.000**

### Supuestos
- El alcance se acota a una muestra de clientes (cubrir el pareto de nómina de clientes con mas frecuencia) de alto impacto, no a los 300.
- La ingesta la sigue haciendo el equipo; no se construyen bandejas ni paneles en esta etapa.
- El cliente provee historia suficiente para validar por reproceso.
- Infraestructura sobre Azure, ya disponible en el cliente.

### Riesgos
- La variabilidad real de formatos puede exceder lo relevado y estirar la extraccion.
- Sin linea de base medida, la mejora hay que construirla durante el propio proyecto.
- La ventana de 4 dias deja poco margen para probar en produccion: por eso se valida
  primero contra historia (meses anteriores ya procesados).

### Fuera de alcance (etapas posteriores, no cotizadas)
Escala al resto de los clientes, canal unificado con bandejas y panel de supervision,
y sistema multiagente con autogestion.
""",
    },
    {
        "meeting_summary": (
            "Empresa2 - retail de perfumeria con 20 sucursales mas canal web y "
            "Mercado Libre. Unos 40.000 pedidos por mes entre todos los canales y 300.000 clientes "
            "activos en el ultimo ano. La consigna de la Direccion General es explicita: eficiencia, "
            "no recorte, y cada iniciativa tiene que mostrar como se repaga. El flujo de compra a "
            "entrega tiene cinco etapas y nadie mide el recorrido completo: hay pedidos aprobados "
            "que esperan dias sin dueno, stock fragmentado por canal, retiros en sucursal sin aviso "
            "y ventas sin stock que no dejan registro. Toda la informacion depende de pedirle datos "
            "a un equipo de sistemas sin capacidad disponible. El area de CX ya probo que el metodo "
            "funciona: analizando a mano 20 casos detractores por mes y trabajando causa raiz, "
            "subio el NPS de la web de 40 a 68 sin tableros ni herramientas. Piden un programa "
            "modular que se pueda prender y apagar por etapas, sin estructura fija ni compromisos "
            "largos."
        ),
        "estimation": """## Estimacion: Programa de Eficiencia (Empresa2)

Tres modulos independientes. Cada uno se contrata por separado.

### M1 - Entendimiento y tablero (4 semanas, inversion cerrada)

| Rol | Tarifa (ARS/h) | Horas | Subtotal (ARS) |
|-----|----------------|-------|----------------|
| Consultor/a de Procesos y Eficiencia | 110.000 | 46 | 5.060.000 |
| Analista de Datos | 196.000 | 36 | 7.056.000 |
| Director de Tecnologia & IA | 196.000 | 28 | 5.488.000 |
| Ingeniero/a de IA | 196.000 | 8 | 1.568.000 |

**Subtotal M1: 118 horas - ARS 17.968.000**

Entregables: SIPOC y proceso actual documentados, GEMBA grabado y procesado con IA,
tablero kanban y operativo del flujo instalado como activo del cliente, matriz impacto x
esfuerzo y cuello de botella elegido con datos.

### M1 - Mesa de trabajo y ciclo de mejora (por ciclo, 3-4 semanas)

**56 horas - ARS 8.224.000** por ciclo (rango -10% / +10%)

Mesa interdisciplinaria de quick wins e implementacion de la mejora del cuello de botella,
con antes y despues medidos. Cada ciclo financia el siguiente.

### M2 - Automatizacion de atencion

| Fase | Horas | Costo (ARS) |
|------|-------|-------------|
| Correo: clasificacion y respuesta automatica con derivacion (4-5 sem) | 104 | 19.016.000 |
| Redes: contencion inmediata por mensaje directo con alerta (3-4 sem) | 70 | 12.864.000 |

Ambas con rango -10% / +10%. Incluyen presupuesto y alertas de consumo de IA.

### M3 - IA en el metro cuadrado (por grupo, 4 semanas, cerrado)

**38 horas - ARS 5.556.000** por grupo de hasta 7 personas. Relevamiento de los procesos
de los participantes, 3 sesiones de entrenamiento y acompanamiento hasta dejar parte de su
operacion automatizada.

### Total del programa completo (1 ciclo + 1 grupo)

**386 horas - ARS 63.628.000**

### Supuestos
- El tablero se construye con los datos disponibles hoy, sin depender de desarrollos del
  equipo de sistemas ni de accesos que no se pueden priorizar.
- Los rangos se convierten en inversion cerrada antes de iniciar cada ciclo o fase.
- Valores en pesos argentinos, sin impuestos y sin viaticos fuera de AMBA.

### Riesgos
- La calidad de los datos disponibles condiciona la linea de base: si no alcanzan, el
  primer ciclo se usa para instrumentar.
- La mejora vive en las interfaces entre areas: sin referentes de todas las areas en la
  mesa, los quick wins no se sostienen.
- El repago depende de elegir bien el primer cuello de botella.

### Fuera de alcance
Desarrollos sobre los sistemas core del cliente e integraciones con el operador logistico.
""",
    },
]
