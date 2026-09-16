"""Prueba del endpoint con una transcripcion real leida desde archivo.

Evita el problema de pegar texto multilinea a mano en Swagger: json.dumps
escapa los saltos de linea correctamente.
"""

import json
import urllib.request
from pathlib import Path

texto = Path("transcripcion_reunion.txt").read_text(encoding="utf-8")
print(f"Transcripcion: {len(texto)} caracteres")

payload = json.dumps({"transcription": texto}).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/estimate",
    data=payload,
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(req, timeout=300) as respuesta:
    data = json.load(respuesta)

print("\n" + data["estimation"])
print("\n---")
costo = data["cost_usd"]
costo_texto = f"USD {costo:.4f}" if costo is not None else "sin precio conocido"
print(
    f"modelo: {data['model']} | tokens entrada: {data['input_tokens']} "
    f"| salida: {data['output_tokens']} | costo: {costo_texto}"
)