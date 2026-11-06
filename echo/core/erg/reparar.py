"""La ERG educ como DIAGNÓSTICO CON UBICACIÓN; la reparación es pequeña y por tipo de regla.

reparar(texto) -> (texto_corregido, [(regla, original, corregido), ...])

Sólo actúa con reglas de error gramatical de una lista blanca (se ignoran las de mayúsculas y puntuación).
La ubicación sale de los desplazamientos de carácter <a:b> de la MRS y de los tokens del árbol.
El número y la persona del sujeto salen de la MRS (ARG1 del verbo), no de adivinar.
Ante la duda no toca nada: si la palabra no está en el léxico verbal, si el sujeto no va antes del verbo, etc.
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))
import erg  # noqa: E402
import detectores as D  # noqa: E402

CONCORDANCIA = {"third_sg_fin_v_ilr_rbst", "non_third_sg_fin_v_olr_rbst", "be_c_is_rbst", "be_c_was_rbst",
                "be_c_are_rbst", "be_c_were_rbst", "be_c_am_rbst", "have_fin_aux_rbst", "do_fin_aux_rbst"}
TIEMPO = {"yesterday_np_rbst", "last_det_rbst", "ago_rbst", "tomorrow_np_rbst"}
NEGACION = {"not_mv_adv1_rbst"}
_EP = re.compile(r"\[ (?P<pred>\S+?)<(?P<a>\d+):(?P<b>\d+)> LBL: \S+ ARG0: (?P<arg0>[a-z]\d+)(?P<resto>.*?)\]  ", re.S)
_NODO = re.compile(r"\((\d+) ([\w\-+]+) (-?[\d.]+) (\d+) (\d+)")


def _props(mrs):
    """variable -> dict de propiedades (aparecen en la primera mención: x3 [ x PERS: 3 NUM: sg ... ])."""
    p = {}
    for m in re.finditer(r"\b([xei]\d+) \[ [xei] ([^\]]*)\]", mrs):
        p[m.group(1)] = dict(re.findall(r"([A-Z]+): (\S+)", m.group(2)))
    return p


def _eps(mrs):
    out = []
    for m in _EP.finditer(mrs + "  "):
        args = dict(re.findall(r"(ARG\d|BODY|RSTR): ([a-z]\d+)", m["resto"]))
        out.append({"pred": m["pred"], "a": int(m["a"]), "b": int(m["b"]), "arg0": m["arg0"], **args})
    return out


def _analiza(texto):
    out = erg._ace(["-g", erg.EDUC, "-1"], texto.strip() + "\n")
    for linea in out.splitlines():
        partes = re.split(r"(?<=\])\s*;\s*\(", linea, maxsplit=1)
        if linea.startswith("[") and len(partes) == 2:
            return partes[0], "(" + partes[1]
    return None, None


def _palabra_en(texto, a, b):
    """La palabra completa que contiene el tramo de caracteres [a, b)."""
    i, j = a, b
    while i > 0 and texto[i - 1].isalpha():
        i -= 1
    while j < len(texto) and (texto[j].isalpha() or texto[j] == "'"):
        j += 1
    return i, j, texto[i:j]


def _verbo_base(w):
    wl = w.lower()
    if wl in D.VERBOS:
        return wl
    if wl in D.TERCERA:
        return D.TERCERA[wl]
    return None


def _sujeto(eps, props, ep_verbo):
    """(pers, num, empieza_antes) del ARG1 del verbo."""
    x = ep_verbo.get("ARG1")
    if not x or not x.startswith("x"):
        return None
    pr = props.get(x, {})
    pos = [e["a"] for e in eps if e["arg0"] == x and not e["pred"].endswith("_q")]
    antes = bool(pos) and min(pos) < ep_verbo["a"]
    return pr.get("PERS"), pr.get("NUM"), antes


def reparar(texto):
    t = " ".join(str(texto).split())
    mrs, arbol = _analiza(t)
    if not mrs:
        return t, []
    reglas = {n for _, n, _, _, _ in _NODO.findall(arbol) if "rbst" in n}
    activas = reglas & (CONCORDANCIA | TIEMPO | NEGACION)
    if not activas:
        return t, []
    eps, props = _eps(mrs), _props(mrs)
    verbos = [e for e in eps if re.search(r"_v_|^_be_v|_have_v|^_do_v", e["pred"])]
    cambios = []  # (i, j, nuevo, regla, viejo)

    if activas & CONCORDANCIA:
        # cópula con adjetivo o lugar ("the people in my village is kind"): "is" no tiene predicado propio en la MRS;
        # se ubica por el token de la regla en el árbol y el sujeto es el ARG1 del predicado que le sigue
        for m in re.finditer(r"\(\d+ (be_c_(?:is|was|are|were|am)_rbst) .*?\+FROM \\\"(\d+)\\\" \+TO \\\"(\d+)\\\"", arbol):
            i, j, w = _palabra_en(t, int(m.group(2)), int(m.group(3)))
            sig = [e for e in eps if e["a"] >= j and e.get("ARG1", "").startswith("x")]
            if not sig:
                continue
            pr = props.get(sig[0]["ARG1"], {})
            pres = w.lower() in ("is", "are", "am")
            if pr.get("PERS") == "1" and pr.get("NUM") == "sg":
                nuevo = "am" if pres else "was"
            elif pr.get("NUM") == "pl" or pr.get("PERS") == "2":
                nuevo = "are" if pres else "were"
            else:
                nuevo = "is" if pres else "was"
            if nuevo != w.lower():
                cambios.append((i, j, nuevo, "concordancia", w))
        for ev in verbos:
            i, j, w = _palabra_en(t, ev["a"], ev["b"])
            if re.search(r"\b(not|no|don't|doesn't|didn't|do|does|did|to|can|will|could|would|should)\s+$", t[:i]):
                continue  # verbo tras negación/auxiliar/to: lo arregla la negación o ya está en base
            if any(c[0] == i for c in cambios):
                continue
            suj = _sujeto(eps, props, ev)
            if not suj or not suj[2]:
                continue  # sin sujeto antes del verbo (imperativo, pregunta): no se toca
            pers, num, _ = suj
            tres = pers == "3" and num == "sg"
            wl = w.lower()
            nuevo = None
            if wl in ("is", "are", "was", "were", "am"):
                pres = wl in ("is", "are", "am")
                if num == "pl":
                    nuevo = "are" if pres else "were"
                elif tres:
                    nuevo = "is" if pres else "was"
            else:
                base = _verbo_base(w)
                tension = props.get(ev["arg0"], {}).get("TENSE")
                if base and tension == "pres" and base != "be":
                    nuevo = D.VERBOS[base][0] if tres else base
            if nuevo and nuevo != wl:
                cambios.append((i, j, nuevo, "concordancia", w))

    if activas & TIEMPO:
        for ev in verbos:
            i, j, w = _palabra_en(t, ev["a"], ev["b"])
            base = _verbo_base(w)
            if not base or w.lower() in D.PASADOS or props.get(ev["arg0"], {}).get("TENSE") not in ("pres", None):
                continue
            if any(c[0] == i for c in cambios):
                cambios = [c for c in cambios if c[0] != i]
            if base == "be":
                suj = _sujeto(eps, props, ev)
                nuevo = "were" if suj and suj[1] == "pl" or w.lower() == "are" else "was"
            else:
                nuevo = D.VERBOS[base][1]
            cambios.append((i, j, nuevo, "pasado", w))

    if activas & NEGACION:
        for m in re.finditer(r"\b(not|no) (\w+)", t):
            base = _verbo_base(m.group(2))
            if not base or base == "be":
                continue
            ev = next((e for e in verbos if e["a"] <= m.start(2) < e["b"] + 1), None)
            suj = _sujeto(eps, props, ev) if ev else None
            pasado = bool(D._PASADO_MARCA.search(t))
            aux = "didn't" if pasado else ("doesn't" if suj and suj[0] == "3" and suj[1] == "sg" else "don't")
            cambios.append((m.start(), m.end(), f"{aux} {base}", "negacion", m.group(0)))

    if not cambios:
        return t, []
    for i, j, nuevo, regla, viejo in sorted(cambios, key=lambda c: -c[0]):
        if viejo[:1].isupper():
            nuevo = nuevo[:1].upper() + nuevo[1:]
        t = t[:i] + nuevo + t[j:]
    return t, [(r, v, n) for i, j, n, r, v in sorted(cambios)]


if __name__ == "__main__":
    for s in sys.argv[1:] or ["The people in my village is very kind.", "Yesterday I plant corn and sell it.",
                              "My father have two cows.", "My sister not like the city.", "Ok, imagine I am a tourist.",
                              "The cows in the field eats grass every day."]:
        print(s, "->", reparar(s))
