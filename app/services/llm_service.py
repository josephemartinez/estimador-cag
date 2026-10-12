from app.services.llm_wrapper import LLMWrapper
from app.context.examples import ESTIMATION_EXAMPLES
from app.context.rates import format_roles

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

def generate_estimation(wrapper: LLMWrapper, transcription: str) -> dict:
    return wrapper.complete(system_prompt=build_system_prompt(), user_message=transcription)