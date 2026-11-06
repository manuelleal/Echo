"""Detector y corrector con la ERG 2025 (variante educ, con reglas de error de aprendiz) y ACE 0.9.34, en WSL.

corregir(texto) -> (texto_corregido, reglas_rbst)
  1. Analiza con erg-2025-educ.dat (-1: la mejor lectura). Si su árbol usa alguna regla *_rbst, hay error.
  2. Genera desde la MRS de esa lectura con la ERG estándar. La MRS ya trae el significado "arreglado":
     la regla de error acepta la forma mala pero construye la semántica buena.
  3. De las realizaciones, elige la más parecida a la entrada; si no se parece lo bastante, no corrige.
Ante la duda no toca nada: si no hay análisis, si no hay *_rbst o si la generación no sale, devuelve el texto igual.
"""
import difflib
import re
import subprocess

import os

_DIR = os.environ.get("ERG_DIR", "/home/ddiddimmo/simbolico_ace")
ACE = os.environ.get("ERG_ACE", _DIR + "/ace-0.9.34/ace")
EDUC = _DIR + "/erg-2025-educ.dat"
STD = _DIR + "/erg-2025-x86-64-0.9.34.dat"
_PREFIJO = ["wsl", "-e"] if os.name == "nt" else []  # en Windows por WSL; en Linux (candy) directo
SIM_MIN = 0.75
_NODO = re.compile(r"\(\d+ ([\w\-+]+) -?\d")


def _ace(args, entrada, tope=30):
    r = subprocess.run([*_PREFIJO, ACE, *args], input=entrada.encode("utf-8"), capture_output=True, timeout=tope)
    return r.stdout.decode("utf-8", "replace")


def _pal(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def _sim(a, b):
    return difflib.SequenceMatcher(None, _pal(a), _pal(b), autojunk=False).ratio()


def analizar(texto):
    out = _ace(["-g", EDUC, "-1"], texto.strip() + "\n")
    for linea in out.splitlines():
        partes = re.split(r"(?<=\])\s*;\s*\(", linea, maxsplit=1)
        if linea.startswith("[") and len(partes) == 2:
            mrs, arbol = partes
            reglas = sorted({n for n in _NODO.findall("(" + arbol) if n.endswith("_rbst") or "_rbst_" in n})
            return reglas, mrs
    return None, None  # sin análisis


def generar(mrs):
    out = _ace(["-g", STD, "-e"], mrs.strip() + "\n")
    return [l.strip() for l in out.splitlines() if l.strip() and not l.startswith(("NOTE", "WARNING", "SKIP"))]


def corregir(texto):
    t = " ".join(str(texto).split())
    reglas, mrs = analizar(t)
    if not reglas:
        return t, []
    cands = generar(mrs)
    if not cands:
        return t, reglas
    mejor = max(cands, key=lambda c: _sim(t, c))
    if _sim(t, mejor) < SIM_MIN:
        return t, reglas
    # conservar la puntuación final del aprendiz
    if t[-1:] in ".!?" and mejor[-1:] in ".!?":
        mejor = mejor[:-1] + t[-1]
    elif t[-1:] not in ".!?" and mejor[-1:] in ".!?":
        mejor = mejor[:-1]
    return mejor, reglas


if __name__ == "__main__":
    import sys
    import time
    for s in sys.argv[1:] or ["The people in my village is very kind.", "She work in the store.",
                              "I milk the cows every morning."]:
        t0 = time.time()
        print(s, "->", corregir(s), f"{time.time() - t0:.2f} s")
