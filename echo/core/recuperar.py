"""Biblioteca → pares de corrección (mal, bien) y recuperación BM25 (Python puro, sin dependencias).

Pares (Enmienda 1 de PLAN_BIBLIOTECA.md):
- el ejemplo_mal → ejemplo_bien de cada ficha aprobada;
- de cada conversación aprobada: la frase del aprendiz con error emparejada con su reintento corregido
  (similitud >= 0,5, largo 0,7–1,3, sin español); si no cumple, se descarta.
"""
import difflib
import glob
import json
import math
import os
import random
import re
import zlib

RAIZ = os.path.dirname(os.path.abspath(__file__))
_ES = re.compile(r"[áéíóúñ¿¡]|\b(pero|que|sí|si|es|la|el|ah|ok|jaja|gracias|no sé|entonces|y)\b", re.I)


def _frases(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\s*\.\.\.\s*|\n", t) if len(s.strip().split()) >= 3]


def _pal(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def _sim(a, b):
    return difflib.SequenceMatcher(None, _pal(a), _pal(b), autojunk=False).ratio()


def _cambiadas(a, b):
    ops = difflib.SequenceMatcher(None, _pal(a), _pal(b), autojunk=False).get_opcodes()
    pa, pb = _pal(a), _pal(b)
    borradas = [w for t, i1, i2, j1, j2 in ops if t == "delete" for w in pa[i1:i2]]
    puestas = [w for t, i1, i2, j1, j2 in ops if t in ("insert", "replace") for w in pb[j1:j2]]
    if any(w not in puestas for w in borradas):
        return 99  # borra palabras (no las mueve): enseñaría a recortar la frase del aprendiz
    return sum(max(i2 - i1, j2 - j1) for t, i1, i2, j1, j2 in ops if t != "equal")


def pares():
    out = []
    for f in sorted(glob.glob(os.path.join(RAIZ, "fichas", "*.json"))):
        x = json.load(open(f, encoding="utf-8"))
        if x.get("aprobada_por"):
            out.append({"ficha": x["id"], "mal": x["ejemplo_mal"], "bien": x["ejemplo_bien"], "origen": "ficha"})
    for f in sorted(glob.glob(os.path.join(RAIZ, "ejemplos", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for i, e in enumerate(d["ejemplos"]):
            if e.get("excluido_solape") or not e.get("aprobado"):
                continue
            ap = [t["texto"] for t in e["turnos"] if t["quien"] == "aprendiz"]
            if len(ap) < 2:
                continue
            malas = [s for s in _frases(ap[0]) if not _ES.search(s)]
            mejor = None
            for t in reversed(ap[1:]):  # el último reintento primero (uno anterior puede seguir con error)
                if mejor:
                    break
                for m in malas:
                    for b in [x for x in _frases(t) if not _ES.search(x)]:
                        s = _sim(m, b)
                        r = len(_pal(b)) / max(1, len(_pal(m)))
                        if (s >= 0.5 and 0.7 <= r <= 1.3 and 0 < _cambiadas(m, b) <= 3
                                and (mejor is None or s > mejor[0])):
                            mejor = (s, m, b)
            if mejor:
                m, b = mejor[1], mejor[2]
                if b[-1:] in ("?", "!", ".") and m[-1:] != b[-1:]:  # la puntuación final la pone el aprendiz
                    b = b[:-1] + (m[-1] if m[-1:] in ("?", "!", ".") else "")
                out.append({"ficha": d["ficha_id"], "mal": m, "bien": b, "origen": f"{d['ficha_id']}#{i}"})
    return out


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [_pal(d) for d in docs]
        self.k1, self.b = k1, b
        self.avg = sum(map(len, self.docs)) / max(1, len(self.docs))
        df = {}
        for d in self.docs:
            for w in set(d):
                df[w] = df.get(w, 0) + 1
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def puntajes(self, consulta):
        q = _pal(consulta)
        res = []
        for d in self.docs:
            s = 0.0
            for w in q:
                if w in self.idf:
                    tf = d.count(w)
                    s += self.idf[w] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * len(d) / self.avg))
            res.append(s)
        return res


class Biblioteca:
    def __init__(self):
        self.p = pares()
        self.bm = BM25([x["mal"] for x in self.p])

    def recuperar(self, texto, k=4):
        s = self.bm.puntajes(texto)
        orden = sorted(range(len(self.p)), key=lambda i: (-s[i], i))
        return [self.p[i] for i in orden[:k]]

    def azar(self, texto, k=4):
        """Control (d): k pares al azar de fichas distintas a la del primer par que recuperaría (c)."""
        ficha_c = self.recuperar(texto, 1)[0]["ficha"]
        pool = [x for x in self.p if x["ficha"] != ficha_c]
        return random.Random(zlib.crc32(texto.encode("utf-8"))).sample(pool, k)


if __name__ == "__main__":
    b = Biblioteca()
    print("pares:", len(b.p), "| por origen ficha:", sum(x["origen"] == "ficha" for x in b.p))
    for x in b.p[:12]:
        print(f"  [{x['ficha']}] {x['mal']}  ->  {x['bien']}")
    prueba = "My brother have 25 years and he work in the farm."
    print("\nrecupera para:", prueba)
    for x in b.recuperar(prueba):
        print("  c:", x["ficha"], "|", x["mal"])
    for x in b.azar(prueba):
        print("  d:", x["ficha"], "|", x["mal"])
