"""Director del bucle: Claude Haiku + alefast (memoria por consecuencia, JUACO-EXO) eligen en qué gastar cada vuelta.

Aprendizaje activo (EXO-5: alefast sirve cuando etiquetar cuesta):
- acciones = los tipos de error que se pueden generar;
- situación = en qué fase va el bucle y cuál es el tipo más débil en validación;
- resultado = cuánto subió la detección en validación de ese tipo tras generarlo (de -1 a 1).
Haiku lee el contexto de alefast más la tabla por tipo y devuelve 3 tipos con un enfoque corto para cada uno.
Si Haiku falla, usa la recomendación de alefast más el azar.
"""
import json
import os
import random
import sys
from typing import List

from pydantic import BaseModel

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("ALEFAST_DIR", os.path.join(AQUI, "alefast_pkg")))
from alefast import Exo  # noqa: E402
from alefast import persistencia as P  # noqa: E402

MODELO_DIRECTOR = "claude-haiku-5-5"
RUTA_MEM = os.path.join(AQUI, "director_mem.json")


class Eleccion(BaseModel):
    tipo: str
    enfoque: str


class Decision(BaseModel):
    elecciones: List[Eleccion]
    razon: str


def _fase(n):
    return "inicio" if n < 1500 else ("medio" if n < 6000 else "mucho")


class Director:
    def __init__(self, tipos):
        self.tipos = list(tipos)
        if os.path.exists(RUTA_MEM):
            self.mem, _ = P.carga(RUTA_MEM)
        else:
            self.mem = Exo(acciones=self.tipos, presupuesto_chars=600, semilla=0)
        self.prev = None  # (situación, tipos, validación por tipo antes)

    def situacion(self, res):
        vt = res.get("validacion_por_tipo", {})
        peor = min(vt, key=vt.get) if vt else "ninguno"
        return {"fase": _fase(res.get("n_pares", 0)), "peor": peor}

    def observa(self, res):
        if not self.prev:
            return
        sit, tipos, antes = self.prev
        despues = res.get("validacion_por_tipo", {})
        for t in tipos:
            if t in despues and t in antes:
                r = max(-1.0, min(1.0, (despues[t] - antes[t]) * 10))
            elif t in despues:
                r = 0.3  # primera medida de ese tipo: algo de valor
            else:
                r = 0.0
            self.mem.observe(sit, t, r)
        P.guarda(self.mem, RUTA_MEM, meta={"uso": "director del bucle CHROMEBOOK-CANDY"})

    def elige(self, client, res, n=3, gasto_cb=None):
        sit = self.situacion(res) if res else {"fase": "inicio", "peor": "ninguno"}
        ctx = self.mem.context(sit)
        tabla = json.dumps({"validacion_por_tipo": res.get("validacion_por_tipo", {}) if res else {},
                            "n_validacion_por_tipo": res.get("n_validacion_por_tipo", {}) if res else {},
                            "validacion": res.get("validacion") if res else None,
                            "sonda_estructura": res.get("sonda_estructura") if res else None}, ensure_ascii=False)
        pedido = (f"Eres el director de un bucle que genera datos para entrenar un etiquetador de errores de inglés de "
                  f"aprendices hispanohablantes A1-A2. Tipos posibles: {self.tipos}.\n"
                  f"Memoria por consecuencia (alefast):\n{ctx}\n\nMétricas de la última vuelta:\n{tabla}\n\n"
                  f"Elige {n} tipos distintos para la siguiente tanda: prioriza los débiles o con pocos datos y los que "
                  f"la memoria dice que rinden. Para cada uno da un 'enfoque' de una línea (qué variantes generar para que "
                  f"el etiquetador aprenda lo que hoy falla, por ejemplo sujeto lejos del verbo o preguntas).")
        try:
            r = client.beta.messages.parse(model=MODELO_DIRECTOR, max_tokens=1500,
                                           messages=[{"role": "user", "content": pedido}], output_format=Decision,
                                           betas=["server-side-fallback-2026-07-01"], fallbacks="default")
            if gasto_cb:
                gasto_cb(r.usage, "director")
            d = r.parsed_output
            elecc = [(e.tipo, e.enfoque) for e in d.elecciones if e.tipo in self.tipos][:n]
            razon = d.razon
        except Exception as ex:  # noqa: BLE001
            elecc, razon = [], f"director falló: {type(ex).__name__}"
        usados = {t for t, _ in elecc}
        if len(elecc) < n:
            rec = self.mem.recomienda(sit)
            if rec in self.tipos and rec not in usados:
                elecc.append((rec, ""))
                usados.add(rec)
            resto = [t for t in self.tipos if t not in usados]
            random.shuffle(resto)
            elecc += [(t, "") for t in resto[: n - len(elecc)]]
        self.prev = (sit, [t for t, _ in elecc], dict(res.get("validacion_por_tipo", {})) if res else {})
        return elecc, razon, sit
