"""Etiquetador de errores chico: regresión logística sobre rasgos de cada palabra (cabe en el Chromebook, pesa KB).

Etiqueta por palabra: "O" o el tipo de error. Una frase se marca "con error" si alguna palabra sale distinta de "O"
con probabilidad > 0,5. Las etiquetas salen de alinear (mal -> bien) palabra a palabra.
"""
import difflib
import json
import os
import re
import sys
import zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(os.path.dirname(AQUI), "core")  # Echo: core/ reemplaza a biblioteca/
sys.path.insert(0, BIB)
sys.path.insert(0, os.path.join(BIB, "erg"))
import detectores as D  # noqa: E402

_PRON = {"i", "you", "he", "she", "it", "we", "they", "people"}


def toks(t):
    return re.findall(r"[A-Za-z0-9']+", t)


def etiquetas(mal, bien, tipo):
    a, b = [w.lower() for w in toks(mal)], [w.lower() for w in toks(bien)]
    lab = ["O"] * len(a)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if i1 == i2:  # inserción: se marca la palabra donde falta algo
            k = min(i1, len(a) - 1)
            if k >= 0:
                lab[k] = tipo
        for k in range(i1, i2):
            lab[k] = tipo
    return lab


def rasgos(ws):
    low = [w.lower() for w in ws]
    pasado = bool(D._PASADO_MARCA.search(" ".join(ws)))
    out = []
    for i, w in enumerate(low):
        p1 = low[i - 1] if i > 0 else "<s>"
        p2 = low[i - 2] if i > 1 else "<s>"
        n1 = low[i + 1] if i + 1 < len(low) else "</s>"
        n2 = low[i + 2] if i + 2 < len(low) else "</s>"
        f = {"w=" + w: 1, "p1=" + p1: 1, "n1=" + n1: 1, "p2=" + p2: 1, "n2=" + n2: 1,
             "p1w=" + p1 + "_" + w: 1, "wn1=" + w + "_" + n1: 1, "suf3=" + w[-3:]: 1, "suf2=" + w[-2:]: 1,
             "pre1=" + w[:1]: 1, "cap": int(ws[i][:1].isupper() and i > 0), "inicio": int(i == 0),
             "vbase": int(w in D.VERBOS), "v3sg": int(w in D.TERCERA), "vpas": int(w in D.PASADOS),
             "pron_antes": int(p1 in _PRON), "adj": int(w in D._ADJ), "adj_antes": int(p1 in D._ADJ),
             "adj_despues": int(n1 in D._ADJ), "pasado_frase": int(pasado),
             "pasado_x_vbase": int(pasado and w in D.VERBOS), "vocal_sig": int(n1[:1] in "aeiou"),
             "p1_" + ("pron" if p1 in _PRON else "x") + "_v3sg": int(w in D.TERCERA),
             "p1_" + ("pron" if p1 in _PRON else "x") + "_vbase": int(w in D.VERBOS)}
        out.append(f)
    return out


def _es_validacion(frase):
    return zlib.crc32(" ".join(toks(frase.lower())).encode()) % 100 < 15


def _lee(datos):
    pares = [json.loads(l) for l in open(os.path.join(datos, "pares.jsonl"), encoding="utf-8")] \
        if os.path.exists(os.path.join(datos, "pares.jsonl")) else []
    corr = [json.loads(l) for l in open(os.path.join(datos, "correctas.jsonl"), encoding="utf-8")] \
        if os.path.exists(os.path.join(datos, "correctas.jsonl")) else []
    return pares, corr


def marca(modelo, vec, frase):
    ws = toks(frase)
    if not ws:
        return False
    import numpy as np
    pr = modelo.predict_proba(vec.transform(rasgos(ws)))
    io = list(modelo.classes_).index("O")
    return bool(np.any(pr[:, io] < 0.5))


def _tasas(modelo, vec, con_error, correctas):
    d = sum(marca(modelo, vec, s) for s in con_error)
    f = sum(marca(modelo, vec, s) for s in correctas)
    return {"det": f"{d}/{len(con_error)}", "det_pct": round(d / max(1, len(con_error)), 3),
            "falsas": f"{f}/{len(correctas)}", "falsas_pct": round(f / max(1, len(correctas)), 3)}


def entrena_y_evalua(datos, salida):
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    import joblib
    pares, corr = _lee(datos)
    X, y = [], []
    for p in pares:
        if _es_validacion(p["mal"]):
            continue
        ws = toks(p["mal"])
        X += rasgos(ws)
        y += etiquetas(p["mal"], p["bien"], p["tipo"])
        wb = toks(p["bien"])
        X += rasgos(wb)
        y += ["O"] * len(wb)
    for c in corr:
        if _es_validacion(c["frase"]):
            continue
        ws = toks(c["frase"])
        X += rasgos(ws)
        y += ["O"] * len(ws)
    if len(set(y)) < 2:
        return {"n_pares": len(pares), "n_correctas": len(corr), "nota": "pocos datos"}
    vec = DictVectorizer()
    Xv = vec.fit_transform(X)
    modelo = LogisticRegression(max_iter=2000, C=1.0)
    modelo.fit(Xv, y)
    os.makedirs(salida, exist_ok=True)
    joblib.dump((vec, modelo), os.path.join(salida, "etiquetador.joblib"))
    val_err = [p["mal"] for p in pares if _es_validacion(p["mal"])]
    val_ok = [p["bien"] for p in pares if _es_validacion(p["mal"])] + [c["frase"] for c in corr if _es_validacion(c["frase"])]
    res = {"n_pares": len(pares), "n_correctas": len(corr), "n_palabras_entreno": len(y),
           "validacion": _tasas(modelo, vec, val_err, val_ok)}
    por_tipo = {}
    for p in pares:
        if _es_validacion(p["mal"]):
            t = por_tipo.setdefault(p["tipo"], [0, 0])
            t[1] += 1
            t[0] += marca(modelo, vec, p["mal"])
    res["validacion_por_tipo"] = {k: round(d / n, 3) for k, (d, n) in por_tipo.items() if n}
    res["n_validacion_por_tipo"] = {k: n for k, (d, n) in por_tipo.items()}
    try:  # desarrollo: biblioteca y sondas propias (nunca bancos)
        import recuperar as R
        import dev_detectores as DD
        import sonda_estructura as SE
        res["biblioteca"] = _tasas(modelo, vec, [p["mal"] for p in R.pares()], DD.negativos())
        res["sonda_estructura"] = _tasas(modelo, vec, [m for m, _ in SE.CON_ERROR], SE.CORRECTAS)
    except Exception as e:  # noqa: BLE001
        res["dev_error"] = f"{type(e).__name__}: {e}"
    return res


if __name__ == "__main__":
    print(json.dumps(entrena_y_evalua(os.path.join(AQUI, "datos"), os.path.join(AQUI, "modelo")), indent=1))
