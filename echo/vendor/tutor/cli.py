"""Conversación por consola, sin internet.

    python -m tutor.cli --sesion demo [--ambito agricola|tecnico] [--nivel A1|A2] [--hilos 4]

Escribe frases en inglés; 'salir' para terminar. Cada turno queda en datos/sesiones/<sesion>.jsonl.
"""
import argparse
import sys

from . import registro
from . import tutor as T
from .servidor import Servidor, salud, URL


def mostrar(d):
    if d["estado"] == "fallo_extraccion" or not d["frase_corregida"]:
        print("  (no se pudo analizar la frase; no se afirma que esté bien)")
    elif d["errores"]:
        print(f"  Corrección: {d['frase_corregida']}")
        for e in d["errores"]:
            print(f"    - \"{e['original']}\" -> \"{e['corregido']}\"  ({e['tipo'].replace('_', ' ')})")
    else:
        print("  Sin errores detectados.")
    print(f"  Tutor: {d['pregunta_siguiente']}")
    print(f"  [{d['latencia_s']} s, {d['tokens']} tokens]")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tutor de inglés local (consola)")
    ap.add_argument("--sesion", default=None, help="id anónimo (letras, números, _ -); por defecto aleatorio")
    ap.add_argument("--ambito", default="agricola", choices=list(T.AMBITOS))
    ap.add_argument("--nivel", default="A1-A2")
    ap.add_argument("--hilos", type=int, default=4)
    a = ap.parse_args(argv)
    sesion = a.sesion or registro.nuevo_id()
    registro.ruta(sesion)  # valida el id
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    srv = None
    if not salud(URL):
        print("arrancando el modelo local...", flush=True)
        srv = Servidor(hilos=a.hilos).iniciar()
    contexto = {"ambito": a.ambito, "nivel": a.nivel, "historial": []}
    print(f"Sesión {sesion}. Escribe en inglés ('salir' para terminar).")
    print("Tutor: Hello! Tell me about your work today.")
    try:
        while True:
            try:
                texto = input("> ").strip()
            except EOFError:
                break
            if texto.lower() in ("salir", "exit", "quit"):
                break
            if not texto:
                continue
            d = T.responder_detallado(texto, contexto)
            mostrar(d)
            registro.anotar(sesion, texto, d, contexto)
            contexto["historial"].append({"aprendiz": d["frase_corregida"] or texto,
                                          "pregunta": d["pregunta_siguiente"]})
    finally:
        if srv:
            srv.detener()
    print(f"Registro: {registro.ruta(sesion)}")


if __name__ == "__main__":
    main()
