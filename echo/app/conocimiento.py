"""Respuestas de "Pregúntale al tutor" (faq.json) y carga de módulos de clase (modulos.json). Sin modelo de lenguaje:
las respuestas sobre qué es y cómo funciona salen de texto escrito y verificado, no de lo que invente el 0,5B."""
import json
import os
import re
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))


def _norm(t):
    t = unicodedata.normalize("NFD", (t or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


_VACIAS = set("""el la los las un una de del y o que en es por para con a al se te tu me mi lo le como cual
the a an is are do does you your i me my of to in and or what how who""".split())


def _palabras(t):
    return [w for w in re.findall(r"[a-z0-9]+", _norm(t)) if w not in _VACIAS]


class FAQ:
    def __init__(self):
        ruta = os.path.join(AQUI, "faq.json")
        self.items = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else []

    def responde(self, texto):
        q = set(_palabras(texto))
        if not self.items:
            return {"respuesta": "Todavía no tengo mis respuestas cargadas.", "relacionadas": []}
        puntajes = []
        for i, it in enumerate(self.items):
            mejor = 0.0
            for p in it.get("preguntas", []):
                w = set(_palabras(p))
                if w and q:
                    mejor = max(mejor, len(q & w) / len(q | w))
            puntajes.append((mejor, i))
        puntajes.sort(reverse=True)
        s, i = puntajes[0]
        rel = [self.items[j]["preguntas"][0] for _, j in puntajes[1:4]]
        if s < 0.15:
            return {"respuesta": "No estoy seguro de entender tu pregunta. Prueba con una de estas:",
                    "relacionadas": [it["preguntas"][0] for it in self.items[:4]]}
        return {"respuesta": self.items[i]["respuesta"], "relacionadas": rel}


def carga_modulos(escenarios):
    """Suma (o reemplaza por id) los módulos de modulos.json a los escenarios. Devuelve cuántos cargó."""
    n = 0
    # modulos.json: los del diseñador; modulos_extra.json: los que instala el revisor del servidor (ya aprobados)
    for nombre in ("modulos.json", "modulos_extra.json"):
        ruta = os.path.join(AQUI, nombre)
        if not os.path.exists(ruta):
            continue
        for m in json.load(open(ruta, encoding="utf-8")):
            if m.get("id") and len(m.get("pasos", [])) >= 3:
                escenarios[m["id"]] = m
                n += 1
    return n
