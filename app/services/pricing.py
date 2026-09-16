"""Calculo del costo de una llamada, indexado por modelo.

Precios en USD por millon de tokens. Verificados el 16/09/2026 en
platform.claude.com/docs/en/about-claude/pricing

Si el modelo no esta en la tabla, devuelve None: es preferible informar
"no se" a informar un numero calculado con los precios de otro modelo.
"""

MODEL_PRICING = {
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0},
    "claude-sonnet-5": {"input": 2.0, "output": 10.0},
    "claude-opus-5": {"input": 5.0, "output": 25.0},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    precios = MODEL_PRICING.get(model)
    if precios is None:
        return None
    costo = (
        input_tokens / 1_000_000 * precios["input"]
        + output_tokens / 1_000_000 * precios["output"]
    )
    return round(costo, 6)