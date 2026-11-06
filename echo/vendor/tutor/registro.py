"""Registro de analítica: una línea JSON por turno en datos/sesiones/<sesion>.jsonl.

No se piden nombres ni documentos. El id de sesión es una etiqueta anónima (por defecto aleatoria);
el texto del aprendiz se guarda tal cual lo escribió (si escribe su nombre, queda: ver README).

Campo `verificacion_humana`: queda en null; un docente lo llena después con
{"correccion": "buena"|"parcial"|"mala", "pregunta": "buena"|"mala", "nota": str, "docente": <código>}
(usar `python -m tutor.registro --verificar <sesion>`).
"""
import argparse
import datetime as _dt
import json
import re
import secrets
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "datos" / "sesiones"
_ID_OK = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
ESQUEMA_VERSION = 1


def nuevo_id() -> str:
    return "s-" + secrets.token_hex(4)


def ruta(sesion: str) -> Path:
    if not _ID_OK.match(sesion or ""):
        raise ValueError("id de sesión inválido: sólo letras, números, _ y - (máx. 40); sin nombres de personas")
    return DIR / f"{sesion}.jsonl"


def turnos(sesion: str) -> list:
    p = ruta(sesion)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def anotar(sesion: str, texto_aprendiz: str, salida: dict, contexto: dict | None = None,
           extra: dict | None = None) -> dict:
    """Anota un turno. `salida` es lo que devolvió responder() o responder_detallado()."""
    p = ruta(sesion)
    p.parent.mkdir(parents=True, exist_ok=True)
    n = len(turnos(sesion)) + 1
    contexto = contexto or {}
    fila = {
        "esquema": ESQUEMA_VERSION,
        "marca_tiempo": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "sesion": sesion,
        "turno": n,
        "texto_aprendiz": texto_aprendiz,
        "errores": salida.get("errores", []),
        "n_errores": len(salida.get("errores", [])),
        "frase_corregida": salida.get("frase_corregida", ""),
        "pregunta_siguiente": salida.get("pregunta_siguiente", ""),
        "latencia_s": salida.get("latencia_s"),
        "tokens": salida.get("tokens"),
        "verificacion_humana": None,
        # diagnóstico (si vino de responder_detallado)
        "estado": salida.get("estado"),
        "tokens_prompt": salida.get("tokens_prompt"),
        "llamadas_modelo": salida.get("llamadas"),
        "reintentos": salida.get("reintentos"),
        "version_prompts": salida.get("version_prompts"),
        "ambito": contexto.get("ambito"),
        "nivel": contexto.get("nivel"),
    }
    if extra:
        fila.update(extra)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    return fila


def verificar(sesion: str, docente: str = "docente"):
    """Recorre los turnos sin verificar y pide al docente su juicio (consola). Reescribe el archivo."""
    filas = turnos(sesion)
    cambios = 0
    for f in filas:
        if f.get("verificacion_humana") is not None:
            continue
        print(f"\n[{f['turno']}] aprendiz : {f['texto_aprendiz']}")
        print(f"     corregida: {f['frase_corregida']}")
        for e in f["errores"]:
            print(f"     - {e['original']!r} -> {e['corregido']!r} ({e['tipo']})")
        print(f"     pregunta : {f['pregunta_siguiente']}")
        c = input("  corrección buena/parcial/mala (Enter = saltar, q = salir): ").strip().lower()
        if c == "q":
            break
        if c not in ("buena", "parcial", "mala"):
            continue
        q = input("  pregunta buena/mala: ").strip().lower()
        nota = input("  nota (opcional): ").strip()
        f["verificacion_humana"] = {"correccion": c, "pregunta": q if q in ("buena", "mala") else None,
                                    "nota": nota, "docente": docente,
                                    "marca_tiempo": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")}
        cambios += 1
    if cambios:
        ruta(sesion).write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")
    print(f"{cambios} turnos verificados")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Verificación humana de turnos registrados")
    ap.add_argument("--verificar", required=True, metavar="SESION")
    ap.add_argument("--docente", default="docente", help="código anónimo del docente")
    a = ap.parse_args()
    verificar(a.verificar, a.docente)
