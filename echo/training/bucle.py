"""Bucle nocturno «la API entrena al modelo» (PREREGISTRO_bucle.md). Pensado para el servidor de casa (Linux).

    python bucle.py --tope-usd 15 [--vueltas 999] [--por-llamada 40]

Cada vuelta: 3 tipos de error -> Claude genera pares (mal, bien, tipo) + correctas -> filtros (ERG, <=3 palabras,
duplicados, solape con bancos SOLO como puntaje) -> datos/pares.jsonl -> reentrena el etiquetador -> registro.jsonl.
Reanudable: los datos y el gasto se acumulan en disco. Nunca imprime frases de los bancos.
"""
import argparse
import difflib
import json
import os
import random
import re
import sys
import time
from typing import List

import anthropic
from pydantic import BaseModel

AQUI = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(os.path.dirname(AQUI), "core")  # Echo: core/ reemplaza a biblioteca/
sys.path.insert(0, BIB)
sys.path.insert(0, os.path.join(BIB, "erg"))
import erg  # noqa: E402
import etiquetador as ET  # noqa: E402

MODELO = os.environ.get("BUCLE_MODELO", "claude-sonnet-5-5")  # 4-nov: Christiam pidió Sonnet/Haiku, en línea con alefast
# Precio CONSERVADOR: se cuenta a tarifa de Opus 5.5 (Sonnet y Haiku cuestan menos), así el tope nunca se pasa.
PRECIO_IN, PRECIO_OUT = 4.00 / 1e6, 20.00 / 1e6
DATOS = os.path.join(AQUI, "datos")
TIPOS = {
    "edad_have": "edad con have en vez de be (I have 20 years)",
    "concordancia_3sg": "falta la -s de 3.ª persona o sobra con plural, incluso con el sujeto lejos del verbo",
    "pasado": "verbo en presente con marcador de pasado (yesterday, last week, ago, in 2019)",
    "do_negacion": "negación sin do/does/did (I not like)",
    "sujeto_omitido": "falta el sujeto 'it' o 'there' (Is raining, Is a big farm)",
    "articulo_a_an": "a/an mal elegido",
    "articulo_omitido": "falta artículo (I am nurse, I have car)",
    "orden_adjetivo": "adjetivo después del sustantivo (a horse white)",
    "people_plural": "people con verbo en singular (people is/was/has)",
    "falso_cognado": "falso amigo del español: actually/currently, assist/attend, career/degree, library/bookstore, "
                     "sensible/sensitive, embarrassed/pregnant, realize/carry out, constipated/have a cold, etc.",
    "para_infinitivo": "for + verbo para propósito (for buy)",
    "make_do": "make y do confundidos (make the homework, do a cake)",
    "preposicion": "preposición calcada del español (married with, depends of, in the morning/at night, arrive to)",
    "plural_sustantivo": "plural mal formado o adjetivo en plural (two childs, informations, reds cars)",
}
CONTEXTOS = ["finca cafetera", "ganadería", "cocina de restaurante", "turismo rural", "taller de mecánica",
             "tienda de la vereda", "puesto de salud", "sala de sistemas del SENA", "panadería", "plaza de mercado",
             "transporte en bus", "familia y casa", "clima y cosechas", "piscicultura", "artesanías"]


class Par(BaseModel):
    mal: str
    bien: str


class Lote(BaseModel):
    pares: List[Par]
    correctas: List[str]


SISTEMA = """Eres lingüista experto en errores de aprendices hispanohablantes de inglés (A1–A2, adultos de zonas rurales de Colombia).
Escribes frases como las que de verdad escriben esos aprendices: cortas o medianas, vocabulario sencillo, contextos reales.
Para cada frase con error das su corrección MÍNIMA: cambias sólo lo necesario para ese error y nada más.
Cada frase con error tiene EXACTAMENTE un error, del tipo pedido. Varía sujetos, tiempos, longitudes y vocabulario; nada de nombres de personas reales.
Las frases correctas usan las mismas palabras trampa pero bien usadas, sin ningún error."""


def _pal(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def cambiadas(a, b):
    ops = difflib.SequenceMatcher(None, _pal(a), _pal(b), autojunk=False).get_opcodes()
    return sum(max(i2 - i1, j2 - j1) for t, i1, i2, j1, j2 in ops if t != "equal")


def limpia_erg(frase):
    """True si la ERG la analiza sin reglas de error GRAMATICAL (se toleran las de mayúscula/puntuación)."""
    reglas, mrs = erg.analizar(frase)
    if mrs is None:
        return False
    graves = [r for r in reglas if not re.search(r"cap|cma|runon|punct|frg", r)]
    return not graves


def carga_bancos():
    ruta = os.path.join(AQUI, "bancos_palabras.json")  # lista de conjuntos de palabras; nunca se imprime
    return [set(x) for x in json.load(open(ruta, encoding="utf-8"))] if os.path.exists(ruta) else []


def solapa(frase, bancos):
    p = set(_pal(frase))
    return any(len(p & b) / max(1, len(p | b)) >= 0.6 for b in bancos if len(b) >= 3)


def gasto(ruta):
    return sum(json.loads(l)["usd"] for l in open(ruta, encoding="utf-8")) if os.path.exists(ruta) else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tope-usd", type=float, default=15.0)
    ap.add_argument("--vueltas", type=int, default=999)
    ap.add_argument("--por-llamada", type=int, default=40)
    ap.add_argument("--tipos-por-vuelta", type=int, default=3)
    ap.add_argument("--pausa-min", type=float, default=0.0, help="espera entre vueltas, para repartir el tope")
    ap.add_argument("--hasta", default=None, help="fecha y hora límite ISO, p. ej. 2026-11-08T23:59")
    ap.add_argument("--sin-director", action="store_true")
    a = ap.parse_args()
    import datetime
    limite = datetime.datetime.fromisoformat(a.hasta) if a.hasta else None
    os.makedirs(DATOS, exist_ok=True)
    clave = os.environ.get("ANTHROPIC_API_KEY") or open(os.path.expanduser("~/.claves/anthropic.txt")).read().strip()
    client = anthropic.Anthropic(api_key=clave)
    f_gasto, f_pares, f_corr = (os.path.join(DATOS, n) for n in ("gasto.jsonl", "pares.jsonl", "correctas.jsonl"))
    vistos = set()
    for f in (f_pares, f_corr):
        if os.path.exists(f):
            for l in open(f, encoding="utf-8"):
                d = json.loads(l)
                vistos.add(" ".join(_pal(d.get("mal") or d.get("frase"))))
    bancos = carga_bancos()
    print(f"bancos cargados (sólo conjuntos): {len(bancos)}; ya vistos: {len(vistos)}", flush=True)
    rng = random.Random(int(time.time()))
    tipos = list(TIPOS)

    def anota_gasto(u, quien, extra=None):
        # precio conservador: todo se cuenta a tarifa de Opus 5.5 (Haiku cuesta menos), así el tope nunca se pasa
        usd = u.input_tokens * PRECIO_IN + u.output_tokens * PRECIO_OUT
        with open(f_gasto, "a", encoding="utf-8") as g:
            g.write(json.dumps({"t": int(time.time()), "quien": quien, "in": u.input_tokens, "out": u.output_tokens,
                                "usd": round(usd, 4), **(extra or {})}) + "\n")
        return usd

    director = None
    if not a.sin_director:
        try:
            import director as DR
            director = DR.Director(tipos)
        except Exception as ex:  # noqa: BLE001
            print("sin director:", type(ex).__name__, ex, flush=True)
    ultimo = None
    if os.path.exists(os.path.join(AQUI, "registro.jsonl")):
        lineas = open(os.path.join(AQUI, "registro.jsonl"), encoding="utf-8").read().strip().splitlines()
        ultimo = json.loads(lineas[-1]) if lineas else None
    for v in range(a.vueltas):
        if gasto(f_gasto) >= a.tope_usd * 0.95:
            print(f"tope alcanzado: {gasto(f_gasto):.2f} USD", flush=True)
            break
        if limite and datetime.datetime.now() >= limite:
            print("fecha límite alcanzada", flush=True)
            break
        vuelta = int(time.time())
        if director:
            elecc, razon, sit = director.elige(client, ultimo or {}, a.tipos_por_vuelta,
                                               gasto_cb=lambda u, q: anota_gasto(u, q))
            print(f"[director] {sit} -> {[t for t, _ in elecc]} | {razon[:160]}", flush=True)
        else:
            elecc = [(t, "") for t in rng.sample(tipos, a.tipos_por_vuelta)]
        for tipo, enfoque in elecc:
            ctx = rng.sample(CONTEXTOS, 3)
            pedido = (f"Tipo de error: {tipo} = {TIPOS[tipo]}.\nContextos para esta tanda: {', '.join(ctx)}.\n"
                      + (f"Enfoque pedido por el director: {enfoque}\n" if enfoque else "")
                      + f"Escribe {a.por_llamada} pares distintos (mal con UN error de este tipo -> bien con corrección mínima) "
                      f"y {a.por_llamada // 3} frases correctas con las mismas trampas bien usadas.")
            t0 = time.time()
            try:
                # misma llamada ya probada en biblioteca/generar_ejemplos.py (0,71 USD el 4-nov)
                r = client.beta.messages.parse(model=MODELO, max_tokens=12000, system=SISTEMA,
                                               messages=[{"role": "user", "content": pedido}],
                                               output_config={"effort": "medium"}, output_format=Lote,
                                               betas=["server-side-fallback-2026-07-01"], fallbacks="default")
            except anthropic.APIStatusError as e:
                print("error de API", tipo, e.status_code, flush=True)
                time.sleep(30)
                continue
            u = r.usage
            usd = u.input_tokens * PRECIO_IN + u.output_tokens * PRECIO_OUT
            with open(f_gasto, "a", encoding="utf-8") as g:
                g.write(json.dumps({"t": vuelta, "tipo": tipo, "in": u.input_tokens, "out": u.output_tokens,
                                    "usd": round(usd, 4), "s": round(time.time() - t0, 1)}) + "\n")
            lote = r.parsed_output
            if lote is None:
                continue
            ok = desc = 0
            with open(f_pares, "a", encoding="utf-8") as fp:
                for p in lote.pares:
                    k = " ".join(_pal(p.mal))
                    if (k in vistos or _pal(p.mal) == _pal(p.bien) or cambiadas(p.mal, p.bien) > 3
                            or solapa(p.mal, bancos) or solapa(p.bien, bancos) or not limpia_erg(p.bien)):
                        desc += 1
                        continue
                    vistos.add(k)
                    fp.write(json.dumps({"mal": p.mal, "bien": p.bien, "tipo": tipo, "vuelta": vuelta}, ensure_ascii=False) + "\n")
                    ok += 1
            with open(f_corr, "a", encoding="utf-8") as fc:
                for s in lote.correctas:
                    k = " ".join(_pal(s))
                    if k in vistos or solapa(s, bancos) or not limpia_erg(s):
                        desc += 1
                        continue
                    vistos.add(k)
                    fc.write(json.dumps({"frase": s, "tipo": tipo, "vuelta": vuelta}, ensure_ascii=False) + "\n")
                    ok += 1
            print(f"[v{v}] {tipo}: {ok} guardadas, {desc} descartadas, {usd:.3f} USD (acum {gasto(f_gasto):.2f})", flush=True)
        res = ET.entrena_y_evalua(DATOS, os.path.join(AQUI, "modelo"))
        res.update({"vuelta": v, "t": vuelta, "usd_acum": round(gasto(f_gasto), 2),
                    "tipos": [t for t, _ in elecc]})
        with open(os.path.join(AQUI, "registro.jsonl"), "a", encoding="utf-8") as fr:
            fr.write(json.dumps(res) + "\n")
        print("[eval]", json.dumps(res), flush=True)
        if director:
            director.observa(res)
        ultimo = res
        if a.pausa_min:
            time.sleep(a.pausa_min * 60)


if __name__ == "__main__":
    main()
