#!/usr/bin/env python3
"""Análisis del piloto del tutor de inglés offline. Sólo biblioteca estándar.

Uso:
  python analiza_piloto.py registro.csv                      # informe + muestra_ciega.csv
  python analiza_piloto.py registro.csv --juicios muestra_ciega.csv   # añade % pertinentes (Wilson 95 %)

Salidas (en --salida, por defecto la carpeta del script):
  muestra_ciega.csv  hasta 60 pares barajados (semilla fija), sin sesión ni hora, con 'juicio_instructor' vacío
  informe_piloto.md  tablas por sesión y total

Sólo medianas, rangos e IQR (no se reportan medias).
"""
import argparse
import csv
import math
import os
import random
import re
import statistics
import unicodedata
from collections import Counter, defaultdict

SEMILLA = 20261105
MAX_MUESTRA = 60
FUENTES = ("ficha", "gramática ERG", "modelo")


def num(x):
    try:
        v = float(str(x).strip().replace(",", "."))
        return v if math.isfinite(v) else None
    except ValueError:
        return None


def resumen(valores):
    """mediana, mín, máx, Q1, Q3 (cuartiles inclusivos) o None si no hay datos."""
    v = sorted(x for x in valores if x is not None)
    if not v:
        return None
    if len(v) >= 2:
        q = statistics.quantiles(v, n=4, method="inclusive")
        q1, q3 = q[0], q[2]
    else:
        q1 = q3 = v[0]
    return dict(n=len(v), med=statistics.median(v), mn=v[0], mx=v[-1], q1=q1, q3=q3)


def fmt(r):
    if r is None:
        return "—"
    return f"{r['med']:.1f} ({r['mn']:.1f}–{r['mx']:.1f}; IQR {r['q1']:.1f}–{r['q3']:.1f}; n={r['n']})"


def fuentes_de(errores):
    """Cuenta errores por fuente desde 'orig → corr [fuente/tipo] | ...'."""
    c = Counter()
    if not errores or not errores.strip():
        return c
    for trozo in errores.split(" | "):
        m = re.search(r"\[([^\]/]+)", trozo)
        c[m.group(1).strip() if m else "sin fuente"] += 1
    return c


def wilson(k, n, z=1.959964):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    mar = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centro - mar), min(1.0, centro + mar)


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def tabla_bloque(filas):
    turnos = len(filas)
    tipos = Counter(r.get("tipo_entrada", "") for r in filas)
    fuentes = Counter()
    for r in filas:
        fuentes.update(fuentes_de(r.get("errores", "")))
    err = sum(1 for r in filas if (r.get("estado", "").strip().lower() == "error"))
    return dict(
        turnos=turnos,
        tipos=tipos,
        fuentes=fuentes,
        seg=resumen([num(r.get("segundos")) for r in filas]),
        seg1=resumen([num(r.get("segundos_primera_respuesta")) for r in filas]),
        fallos=err,
        pct_fallo=(100.0 * err / turnos) if turnos else 0.0,
    )


def hacer_muestra(filas, ruta):
    cand = [
        r for r in filas
        if r.get("estado", "").strip().lower() != "error"
        and (r.get("texto_aprendiz") or "").strip()
        and (r.get("errores") or "").strip()
    ]
    rng = random.Random(SEMILLA)
    rng.shuffle(cand)
    cand = cand[:MAX_MUESTRA]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "texto_aprendiz", "frase_corregida", "errores", "pregunta_tutor", "juicio_instructor"])
        for i, r in enumerate(cand, 1):
            w.writerow([i, r.get("texto_aprendiz", ""), r.get("frase_corregida", ""),
                        r.get("errores", ""), r.get("pregunta_tutor", ""), ""])
    return len(cand), len([1 for r in filas if (r.get("errores") or "").strip()])


def juzgar(ruta):
    cuenta = Counter()
    for r in leer_csv(ruta):
        j = norm(r.get("juicio_instructor", ""))
        if not j:
            continue
        if j.startswith("no pert"):
            cuenta["no pertinente"] += 1
        elif j.startswith("pert"):
            cuenta["pertinente"] += 1
        elif j.startswith("dan"):
            cuenta["dañina"] += 1
        else:
            cuenta["otro/ilegible"] += 1
    return cuenta


def md_tabla(enc, filas):
    out = ["| " + " | ".join(enc) + " |", "|" + "|".join("---" for _ in enc) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(out)


def informe(filas, juicios_cuenta, info_muestra, ruta_salida):
    por_ses = defaultdict(list)
    for r in filas:
        por_ses[r.get("sesion", "?")].append(r)
    total = tabla_bloque(filas)
    sesiones = sorted(por_ses)
    L = ["# Informe del piloto (generado automáticamente)", "",
         "Sólo medianas, rangos (mín.–máx.) e IQR. Sin medias. Los resultados describen uso, no aprendizaje.", ""]

    L += ["## Totales", "",
          f"- Aprendices (sesiones distintas): **{len(sesiones)}**",
          f"- Turnos: **{total['turnos']}**",
          f"- Turnos por aprendiz (mediana, rango, IQR): {fmt(resumen([len(v) for v in por_ses.values()]))}",
          f"- `segundos`: {fmt(total['seg'])}",
          f"- `segundos_primera_respuesta`: {fmt(total['seg1'])}",
          f"- Turnos con estado = error: **{total['fallos']} de {total['turnos']} ({total['pct_fallo']:.1f} %)**", ""]

    L += ["### Turnos por tipo de entrada", "",
          md_tabla(["tipo_entrada", "turnos"], sorted(total["tipos"].items())), ""]
    claves = list(FUENTES) + sorted(k for k in total["fuentes"] if k not in FUENTES)
    L += ["### Errores marcados por fuente", "",
          md_tabla(["fuente", "errores"], [(k, total["fuentes"].get(k, 0)) for k in claves]), ""]

    L += ["## Por sesión", ""]
    tipos = sorted(total["tipos"])
    enc = ["sesion", "turnos", "fallos (%)", "segundos", "seg. primera resp."] + [f"n {t}" for t in tipos] + [f"err {k}" for k in claves]
    rows = []
    for s in sesiones:
        t = tabla_bloque(por_ses[s])
        rows.append([s, t["turnos"], f"{t['fallos']} ({t['pct_fallo']:.1f} %)", fmt(t["seg"]), fmt(t["seg1"])]
                    + [t["tipos"].get(x, 0) for x in tipos] + [t["fuentes"].get(k, 0) for k in claves])
    L += [md_tabla(enc, rows), ""]

    L += ["## Juicio a ciegas del instructor", ""]
    n_m, n_corr = info_muestra
    L.append(f"Turnos con corrección mostrada: {n_corr}. Pares en la muestra ciega: {n_m} (máx. {MAX_MUESTRA}, semilla {SEMILLA}).")
    L.append("")
    if juicios_cuenta is None:
        L.append("Aún sin juicios. Complete la columna `juicio_instructor` de `muestra_ciega.csv` "
                 "(pertinente / no pertinente / dañina) y vuelva a correr con `--juicios`.")
    else:
        n = sum(juicios_cuenta.values())
        filas_j = []
        for k in ("pertinente", "no pertinente", "dañina", "otro/ilegible"):
            if k in juicios_cuenta or k != "otro/ilegible":
                filas_j.append((k, juicios_cuenta.get(k, 0)))
        L += [md_tabla(["juicio", "pares"], filas_j), ""]
        for etiqueta, k in (("Pertinentes", juicios_cuenta.get("pertinente", 0)),
                            ("Dañinas", juicios_cuenta.get("dañina", 0))):
            w = wilson(k, n)
            if w:
                p, lo, hi = w
                L.append(f"- **{etiqueta}: {k}/{n} = {100*p:.1f} %** (Wilson 95 %: {100*lo:.1f}–{100*hi:.1f} %)")
        if n == 0:
            L.append("El archivo de juicios no tiene filas juzgadas.")
        L.append("")
        L.append("Criterios preregistrados: éxito ≥ 70 % pertinentes y ≤ 5 % dañinas; fracaso < 50 % pertinentes o > 10 % dañinas.")

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="registro.csv descargado de /api/registro.csv")
    ap.add_argument("--juicios", help="muestra_ciega.csv ya juzgado por el instructor")
    ap.add_argument("--salida", default=os.path.dirname(os.path.abspath(__file__)), help="carpeta de salida")
    a = ap.parse_args()

    filas = leer_csv(a.csv)
    if not filas:
        raise SystemExit("El CSV no tiene filas.")
    os.makedirs(a.salida, exist_ok=True)
    ruta_m = os.path.join(a.salida, "muestra_ciega.csv")
    info = None
    if a.juicios:
        # No se regenera la muestra: se respetan los juicios ya hechos.
        n_corr = len([1 for r in filas if (r.get("errores") or "").strip()])
        info = (len(leer_csv(a.juicios)), n_corr)
        jc = juzgar(a.juicios)
    else:
        info = hacer_muestra(filas, ruta_m)
        jc = None
    informe(filas, jc, info, os.path.join(a.salida, "informe_piloto.md"))
    print(f"Listo: {os.path.join(a.salida, 'informe_piloto.md')}")
    if not a.juicios:
        print(f"Muestra ciega: {ruta_m} ({info[0]} pares). Complete 'juicio_instructor'.")


if __name__ == "__main__":
    main()
