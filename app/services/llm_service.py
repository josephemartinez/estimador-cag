from anthropic import AsyncAnthropic

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES
from app.context.rates import format_roles
from app.services.pricing import calculate_cost


settings = get_settings()
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


def format_examples(examples: list[dict]) -> str:
    """Convierte la lista de ejemplos en el bloque de texto que se inyecta en el prompt."""
    bloques = []
    for i, ejemplo in enumerate(examples, start=1):
        bloques.append(
            f"### Ejemplo {i}\n\n"
            f"**Resumen de la reunion:**\n{ejemplo['meeting_summary']}\n\n"
            f"**Estimacion generada:**\n{ejemplo['estimation']}"
        )
    return "\n\n---\n\n".join(bloques)


def build_system_prompt() -> str:
    examples_text = format_examples(ESTIMATION_EXAMPLES)
    roles_text = format_roles()
    return f"""Eres un estimador experto de proyectos de software y consultoria.

## Catalogo de roles y tarifas (UNICA fuente valida)

{roles_text}

REGLAS SOBRE ESTE CATALOGO, de cumplimiento obligatorio:
- Usa EXCLUSIVAMENTE los roles de la tabla anterior. Esta prohibido inventar
  roles nuevos, aunque el proyecto parezca necesitarlos.
- Usa EXCLUSIVAMENTE las tarifas de la tabla anterior. Esta prohibido inventar
  tarifas o tomarlas de los ejemplos historicos.
- Si el proyecto requiere una capacidad que ningun rol del catalogo cubre,
  NO inventes el rol: asignalo al rol mas cercano y declaralo como supuesto
  explicito en la seccion de supuestos.

## Presupuestos historicos de referencia

Usalos solo como referencia de FORMATO, nivel de desglose y criterio de
estructura. Las tarifas que aparezcan en ellos pueden estar desactualizadas:
prevalece siempre el catalogo de arriba.

{examples_text}

## Tarea

Genera una estimacion detallada para el proyecto descrito por el usuario,
siguiendo la misma estructura: desglose por rol con horas y tarifas, total,
supuestos, riesgos y fuera de alcance. Si la transcripcion no alcanza para
estimar algo, declaralo como supuesto explicito en vez de inventarlo."""


async def generate_estimation(transcription: str) -> dict:
    system_prompt = build_system_prompt()

    response = await client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=settings.LLM_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": transcription}],
    )

    return {
        "estimation": response.content[0].text,
        "model": settings.LLM_MODEL,
        "provider": settings.LLM_PROVIDER,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cost_usd": calculate_cost(
            settings.LLM_MODEL,
            response.usage.input_tokens,
            response.usage.output_tokens,
        ),}