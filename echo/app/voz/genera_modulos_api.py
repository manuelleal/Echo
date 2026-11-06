"""Genera módulos de clase nuevos con la API (en el servidor), en el formato de modulos.json, y los valida.

    python genera_modulos_api.py --base modulos.json --santander SANTANDER_palabras.md --salida modulos_nuevos.json
Cada paso: meta, tutor (inglés A1-A2, una pregunta), ayuda_es (con "Ej.: ..."), espera (regex en minúsculas), opciones.
Validación: el JSON carga, cada `espera` compila y acepta sus opciones; si un módulo falla, se descarta.
"""
import argparse
import json
import os
import re
import time
from typing import List

import anthropic
from pydantic import BaseModel

MODELO = os.environ.get("MODULOS_MODELO", "claude-sonnet-5-5")


class Vocab(BaseModel):
    en: str
    es: str


class Paso(BaseModel):
    meta: str
    tutor: str
    ayuda_es: str
    espera: str
    opciones: List[str]


class Modulo(BaseModel):
    id: str
    titulo: str
    rol_tutor: str
    meta_es: str
    vocabulario: List[Vocab]
    objetivo_regla: str
    meta_final_es: str
    pasos: List[Paso]


class Lote(BaseModel):
    modulos: List[Modulo]


REGLAS = ["edad_have", "concordancia_3sg", "pasado_irregular", "do_negacion", "sujeto_omitido", "articulo_a_an",
          "orden_adjetivo", "people_plural", "falso_cognado", "para_infinitivo"]
TEMAS = [
    ("santander", "Un módulo ambientado en Santander (Bucaramanga, Barichara, Chicamocha, San Gil, Málaga) donde el tutor es "
                  "un guía o vecino santandereano; usa en las AYUDAS en español 2-3 expresiones tradicionales santandereanas "
                  "verificadas del documento de investigación, apropiadas para el aula, y en inglés explica la cultura (comida, "
                  "fiestas, oficios). Regla objetivo: people_plural."),
    ("salud", "Puesto de salud de la vereda: el aprendiz explica síntomas a una enfermera. Regla: sujeto_omitido."),
    ("cocina", "Cocina de restaurante: el aprendiz es cocinero y explica un plato típico (arepa, mute, pepitoria). Regla: falso_cognado."),
    ("cafe", "Finca cafetera: el aprendiz explica el proceso del café a un comprador extranjero. Regla: pasado_irregular."),
    ("redes", "Soporte de redes y WiFi para ADSO: el aprendiz ayuda a conectar una escuela rural. Regla: concordancia_3sg."),
    ("transporte", "En el bus de Málaga a Bucaramanga: comprar tiquete, horarios y equipaje. Regla: articulo_a_an."),
    ("emprendimiento", "Feria SENA Emprende: el aprendiz vende su producto (artesanía, lana, software). Regla: para_infinitivo."),
]

SISTEMA = """Eres diseñador de módulos de práctica de inglés A1-A2 para aprendices adultos del SENA en Santander, Colombia.
Pedagogía: tarea con meta clara (antes: vocabulario; durante: conversación; después: logro), el aprendiz hace un papel real,
escalera de ayuda (opciones -> modelo), corrección poca. Las líneas del tutor van en inglés muy sencillo, cortas, con UNA sola
pregunta al final. `espera` es una expresión regular de Python en minúsculas, amplia y tolerante, que acepta respuestas válidas
del paso (y SIEMPRE acepta sus `opciones`). `ayuda_es` en español termina con "Ej.: <primera opción en inglés>".
6 a 8 pasos por módulo, 6 a 8 palabras de vocabulario. Nada de nombres de personas reales salvo personajes inventados."""


def valida(m):
    if not (6 <= len(m["pasos"]) <= 9) or m["objetivo_regla"] not in REGLAS:
        return False
    for p in m["pasos"]:
        try:
            rx = re.compile(p["espera"])
        except re.error:
            return False
        if not p["opciones"] or not all(rx.search(o.lower()) for o in p["opciones"]):
            return False
        if p["tutor"].count("?") > 1:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--santander", default=None)
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    clave = os.environ.get("ANTHROPIC_API_KEY") or open(os.path.expanduser("~/.claves/anthropic.txt")).read().strip()
    client = anthropic.Anthropic(api_key=clave)
    ejemplo = json.load(open(a.base, encoding="utf-8"))[0]
    santander = open(a.santander, encoding="utf-8").read()[:12000] if a.santander and os.path.exists(a.santander) else ""
    hechos = json.load(open(a.salida, encoding="utf-8")) if os.path.exists(a.salida) else []
    ids = {m["id"] for m in hechos}
    for tid, tema in TEMAS:
        if tid in ids:
            continue
        pedido = (f"Ejemplo de formato (un módulo ya aprobado):\n{json.dumps(ejemplo, ensure_ascii=False)[:5000]}\n\n"
                  f"Crea 1 módulo nuevo con id \"{tid}\". Tema: {tema}"
                  + (f"\n\nInvestigación verificada sobre palabras santandereanas (usa sólo las marcadas como apropiadas):\n{santander}"
                     if tid == "santander" and santander else ""))
        for intento in range(3):
            try:
                r = client.beta.messages.parse(model=MODELO, max_tokens=8000, system=SISTEMA,
                                               messages=[{"role": "user", "content": pedido}], output_format=Lote,
                                               betas=["server-side-fallback-2026-07-01"], fallbacks="default")
            except anthropic.APIStatusError as e:
                print("error de API", tid, e.status_code, flush=True)
                time.sleep(20)
                continue
            u = r.usage
            with open(os.path.join(os.path.dirname(a.salida) or ".", "gasto_modulos.jsonl"), "a") as g:
                g.write(json.dumps({"t": int(time.time()), "id": tid, "in": u.input_tokens, "out": u.output_tokens,
                                    "usd_tarifa_opus": round(u.input_tokens * 4e-6 + u.output_tokens * 20e-6, 4)}) + "\n")
            if r.parsed_output and r.parsed_output.modulos:
                m = r.parsed_output.modulos[0].model_dump()
                m["id"] = tid
                if valida(m):
                    hechos.append(m)
                    json.dump(hechos, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    print(f"módulo {tid}: OK ({len(m['pasos'])} pasos)", flush=True)
                    break
                print(f"módulo {tid}: no pasó la validación (intento {intento + 1})", flush=True)
    print(f"total módulos nuevos: {len(hechos)}", flush=True)


if __name__ == "__main__":
    main()
