"""Demo para eventos: tutor de inglés en el Chromebook, sin internet, con la cadena que ganó en F1c.

    ERG_DIR=~/f2 python3 demo.py --tutor ~/f2/tutor_pkg [--puerto 8080]     -> http://<ip-del-chromebook>:8080/

Cadena por frase: reglas de las fichas -> ERG educ -> LLM v1 (Qwen 0,5B con llama-server en 127.0.0.1:8097).
Pedagogía de las fichas: primero se resalta el error y se da la PISTA en español; el aprendiz reintenta; la corrección
queda detrás de un botón. Se distingue la REGLA VERIFICADA (ficha o ERG) de la SUGERENCIA DEL MODELO.
No guarda nombres; cada turno va a demo_turnos.jsonl (texto, salida, tiempo) para analizar después.
"""
import argparse
import glob
import json
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(os.path.dirname(AQUI), "core")  # Echo: core/ reemplaza a biblioteca/
sys.path.insert(0, BIB)
sys.path.insert(0, os.path.join(BIB, "erg"))
import detectores as D  # noqa: E402
import reparar as G  # noqa: E402

FICHAS = {}
for _f in glob.glob(os.path.join(BIB, "fichas", "*.json")):
    _x = json.load(open(_f, encoding="utf-8"))
    FICHAS[_x["id"]] = _x
_ERG_A_FICHA = {"pasado": "pasado_irregular", "negacion": "do_negacion"}
_candado = threading.Lock()
TT = None


def _ficha_de_cambio(regla, viejo, texto):
    if regla in FICHAS:
        return regla
    if regla == "concordancia":
        return "people_plural" if re.search(r"\bpeople\b", texto, re.I) and viejo.lower() in (
            "is", "was", "has", "does") else "concordancia_3sg"
    return _ERG_A_FICHA.get(regla)


_PREGUNTA = re.compile(r"^\s*(what|where|when|who|why|how|which|is|are|do|does|did|can|could|will|would)\b.*\?\s*$", re.I)


def simbolico(texto):
    t1, c1 = D.corregir(texto)
    if _PREGUNTA.match(texto):
        # 5-nov: en preguntas la ERG confundió "What time the job start?" con un error de -s; ahí no se usa la ERG
        return t1, [{"ficha": _ficha_de_cambio(r, v, texto), "original": v, "corregido": n,
                     "fuente": "ficha" if r in FICHAS else "gramática ERG"} for r, v, n in c1]
    t2, c2 = G.reparar(t1)
    cambios = [{"ficha": _ficha_de_cambio(r, v, texto), "original": v, "corregido": n,
                "fuente": "ficha" if r in FICHAS else "gramática ERG"} for r, v, n in c1 + c2]
    return t2, cambios


REGISTRO = os.path.join(AQUI, "registro_uso.jsonl")
CAMPOS_CSV = ["sesion", "turno", "timestamp", "tipo_entrada", "ambito", "texto_aprendiz", "frase_corregida",
              "n_errores", "n_verificadas", "errores", "pregunta_tutor", "segundos_primera_respuesta", "segundos",
              "estado", "error_sistema"]
_turnos_por_sesion = {}


def _sesion_valida(s):
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{1,24}", s or ""))


def registra(sesion, tipo_entrada, ambito, texto, out=None, error_sistema=""):
    """Registro de uso ANÓNIMO: sólo el código de sesión, nunca nombres. Una línea JSON por turno."""
    n = _turnos_por_sesion[sesion] = _turnos_por_sesion.get(sesion, 0) + 1
    out = out or {}
    errs = out.get("errores", [])
    fila = {"sesion": sesion, "turno": n, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tipo_entrada": tipo_entrada, "ambito": ambito, "texto_aprendiz": texto,
            "frase_corregida": out.get("frase_corregida", ""), "n_errores": len(errs),
            "n_verificadas": sum(1 for e in errs if e.get("verificada")),
            "errores": " | ".join(f"{','.join(m for m in e.get('marcas', []) if m)} → {e.get('corregido') or ''} "
                                  f"[{e.get('fuente')}{'/' + e['tipo'] if e.get('tipo') else ''}]" for e in errs),
            "pregunta_tutor": out.get("pregunta", ""), "segundos": out.get("segundos", ""),
            "segundos_primera_respuesta": _t_rapido.pop((sesion, " ".join(str(texto).split())[:400]), ""),
            "estado": out.get("estado", "error" if error_sistema else ""), "error_sistema": error_sistema}
    with open(REGISTRO, "a", encoding="utf-8") as fl:
        fl.write(json.dumps(fila, ensure_ascii=False) + "\n")


def registro_csv():
    import csv
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CAMPOS_CSV, extrasaction="ignore")
    w.writeheader()
    if os.path.exists(REGISTRO):
        for l in open(REGISTRO, encoding="utf-8"):
            if l.strip():
                w.writerow(json.loads(l))
    return "﻿" + buf.getvalue()  # BOM para que Excel abra bien las tildes


_t_rapido = {}  # (sesion, texto) -> segundos de la primera respuesta, para el registro
ESCENARIOS = {e["id"]: e for e in json.load(open(os.path.join(AQUI, "escenarios.json"), encoding="utf-8"))}
ANIMOS = ["¡Muy bien!"]
import conocimiento as CO  # noqa: E402  (FAQ de "Pregúntale al tutor" y módulos de clase)
FAQ_ = CO.FAQ()
_GR = os.path.join(AQUI, "garcia_rovira.json")  # datos locales de García Rovira (agente Sonnet, 5-nov, con fuentes)
if os.path.exists(_GR):
    _gr = json.load(open(_GR, encoding="utf-8"))
    for _i, _e in enumerate(_gr.get("ideas_escenarios", []), 1):
        _e = dict(_e, id=f"gr{_i}", titulo=_e["titulo"].replace("Guia ", "Guía "))
        if len(_e.get("pasos", [])) >= 3:
            ESCENARIOS[_e["id"]] = _e
    # sólo ánimos con expresiones verificadas (fuera "sumercé", "mana" y "nonos/taitas", marcadas [DUDOSO] para la provincia)
    ANIMOS = [a for a in _gr.get("animos_es", []) if not re.search(r"sumerc|\bmana\b|nonos|taitas", a, re.I)] or ANIMOS
CO.carga_modulos(ESCENARIOS)  # modulos.json (diseñador de módulos) suma o reemplaza escenarios por id
if "mercado" in ESCENARIOS:
    ESCENARIOS.pop("gr1", None)  # el módulo "mercado" mejora al escenario de García Rovira del mismo lugar
_memoria = {}  # sesion -> {"fichas_falladas": {ficha: n}, "logros": [...], "turnos": n}
_USA_REGLA = {  # la frase usa la estructura de la ficha (para celebrar sólo cuando aplica)
    "edad_have": re.compile(r"\byears? old\b", re.I),
    "concordancia_3sg": re.compile(r"\b(he|she|it|my \w+|the \w+)\s+\w+(s|es)\b", re.I),
    "pasado_irregular": D._PASADO_MARCA,
    "do_negacion": re.compile(r"\b(don't|doesn't|didn't|do not|does not|did not)\b", re.I),
    "sujeto_omitido": re.compile(r"\b(it is|it's|there is|there are)\b", re.I),
    "articulo_a_an": re.compile(r"\ban? [a-z]", re.I),
    "orden_adjetivo": re.compile(r"\b(" + "|".join(sorted(D._ADJ)) + r") [a-z]+", re.I),
    "people_plural": re.compile(r"\bpeople (are|were|have|do|don't)\b", re.I),
    "falso_cognado": re.compile(r"\b(currently|attend|degree|bookstore|sensitive)\b", re.I),
    "para_infinitivo": re.compile(r"\bto [a-z]+", re.I),
}
_REACCIONES = ["Nice!", "Great!", "I see.", "Interesting!", "Very good!", "Cool!", "Oh, nice!"]
_ESPERA = {  # qué cuenta como respuesta a cada tipo de paso (si no, el tutor ayuda y no avanza)
    "saludar": r"\b(hello|hi|hey|good|fine|ok|okay|great|well|thank|thanks|morning|afternoon)\b",
    "presentarse": r"\b(name|years|live|from|i am|i'm|old|work|study)\b",
    "pedir": r"\b(need|want|like|give|buy|please|kilo|kilos|pound|some|a bag|rice|eggs|coffee|potato|blanket)\w*",
    "fruta": r"\b(yes|no|please|want|like|some|kilo|thanks|thank)\b",
    "precio": r"\b(how much|price|cost|pesos|thank|thanks|ok|okay|here|money|cheap|expensive|yes)\b",
    "cantidad": r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|half|kilo|kilos|pound|pounds)\b",
    "despedirse": r"\b(bye|goodbye|thank|thanks|see you|nice|good|have a)\b",
    "preguntar": r"\?|\b(what|when|where|how|who|why|can|do|does|is)\b",
}


def _respondio(meta, pregunta, texto, espera=None):
    t = texto.lower()
    if espera:  # el módulo trae su propia expresión de "respuesta válida" para este paso
        try:
            if re.search(espera, t):
                return True
        except re.error:
            pass
    if meta in _ESPERA:
        return bool(re.search(_ESPERA[meta], t))
    if re.match(r"^(do|are|is|can|would|have|did|was|were)\b", pregunta.strip().lower()) and \
            re.search(r"\b(yes|no|sure|of course|not|i do|i am|i can)\b", t):
        return True
    return len(re.findall(r"[a-z']+", t)) >= 3


def _recuerda(mem, texto):
    """Memoria corta de la sesión, por plantillas (no por el modelo): nombre, edad y lugar."""
    m = re.search(r"\b(?i:my name is|i'm called|call me) ([A-Z][a-záéíóúñ]+)", texto) or \
        re.search(r"\bI(?:'m| am) ([A-Z][a-záéíóúñ]+)\b", texto)
    if m and m.group(1) not in ("Fine", "Good", "Ok", "Okay", "From", "Not", "Very", "Happy", "Ready"):
        mem["nombre"] = m.group(1)
    m = re.search(r"\b(\d{1,2}) years\b", texto)
    if m:
        mem["edad"] = m.group(1)
    m = re.search(r"\b(?:live in|from) ([A-Z][a-záéíóúñ]+)", texto)
    if m:
        mem["lugar"] = m.group(1)
DIR_AUDIO = os.path.join(AQUI, "audio")  # frases fijas pregrabadas con Kokoro-82M en el servidor (voz/genera_audio.py)
AUDIOS = set(json.load(open(os.path.join(DIR_AUDIO, "manifiesto.json"), encoding="utf-8"))) \
    if os.path.exists(os.path.join(DIR_AUDIO, "manifiesto.json")) else set()


def aid(texto):
    """id del audio pregrabado de una frase fija, o None (entonces el navegador la lee con su propia voz)."""
    import hashlib
    k = hashlib.sha1((texto or "").strip().encode("utf-8")).hexdigest()[:12]
    return k if k in AUDIOS else None


def voz_partes(*partes):
    """[(texto, idioma, id_audio|None)] para la cola de reproducción del navegador."""
    return [{"texto": t, "lang": l, "audio": aid(t)} for t, l in partes if t]


def _reaccion_valida(reac, texto, turno):
    """Filtro de la reacción del 0,5B (investigación 5-nov: validar y, si falla, usar plantilla)."""
    if not reac or len(reac.split()) > 14 or "?" in reac:  # la reacción no pregunta: la pregunta la pone el guion
        return False
    if turno > 1 and re.search(r"\b(meet you|good morning|good afternoon|hello|goodbye|welcome)\b", reac, re.I):
        return False
    nombres = [w for w in re.findall(r"\b[A-Z][a-z]+\b", reac)[1:] if w not in ("I", "SENA")]
    return all(n.lower() in texto.lower() for n in nombres)


def practica(sesion, esc_id, paso, texto):
    """Un turno de conversación: el tutor reacciona en personaje, repite bien lo que el aprendiz dijo mal
    (recast) y avanza al siguiente paso del guion. La corrección verificada va por debajo, con su pista."""
    esc = ESCENARIOS[esc_id]
    paso = max(0, min(int(paso), len(esc["pasos"]) - 1))
    t0 = time.perf_counter()
    r = rapido(texto)
    mem = _memoria.setdefault(sesion, {"fichas_falladas": {}, "logros": [], "turnos": 0, "ult_fichas": [],
                                       "palabras": 0, "ult_correccion": -99, "pendientes": []})
    mem["turnos"] += 1
    mem["palabras"] += len(re.findall(r"[A-Za-z']+", texto))
    # Política de corrección (investigación 5-nov: Lyster y Saito 2010; Duolingo Video Call): como máximo una corrección
    # en el momento cada 3 turnos; el resto va al resumen final (máximo 3) con "dilo otra vez".
    corrige_ahora = bool(r["errores"]) and (mem["turnos"] - mem["ult_correccion"] >= 3)
    if corrige_ahora:
        mem["ult_correccion"] = mem["turnos"]
    elif r["errores"] and len(mem["pendientes"]) < 3:
        e0 = r["errores"][0]
        mem["pendientes"].append({"dijiste": texto, "mejor": r["frase_corregida"],
                                  "regla": FICHAS[e0["tipo"]]["regla_es"] if e0.get("tipo") in FICHAS else ""})
    fichas_ahora = [e["tipo"] for e in r["errores"] if e.get("tipo")]
    logro = None
    pendientes_logro = []
    for f in mem["ult_fichas"]:
        # sólo se celebra si la frase USA la estructura de la regla y esta vez está bien (5-nov: antes celebraba
        # "no fallaste el pasado" en frases sin pasado); si no la usa, la regla queda pendiente para otro turno
        usa = _USA_REGLA.get(f)
        if f in fichas_ahora or not usa:
            continue
        if usa.search(texto) and not logro:
            import random
            logro = f"{random.choice(ANIMOS)} Esta vez usaste bien: {FICHAS[f]['regla_es']}"
            mem["logros"].append(f)
        else:
            pendientes_logro.append(f)
    for f in fichas_ahora:
        mem["fichas_falladas"][f] = mem["fichas_falladas"].get(f, 0) + 1
    mem["ult_fichas"] = list(dict.fromkeys(fichas_ahora + pendientes_logro))
    lo_que_dijo = r["frase_corregida"] if r["errores"] else texto
    # --- continuidad (5-nov: "sigue hablando sin importar lo que digo"): sólo avanza si respondió el paso;
    # si el aprendiz pregunta, el tutor le responde en su papel; recuerda nombre, edad, lugar y lo que pidió.
    actual = esc["pasos"][paso]
    q_actual = actual["tutor"]
    _recuerda(mem, texto)
    pregunta_aprendiz = texto.strip().endswith("?") and actual.get("meta") not in ("precio", "preguntar")
    respondio = (not pregunta_aprendiz) and _respondio(actual.get("meta", ""), q_actual, texto, actual.get("espera"))
    mem.setdefault("fallos_paso", 0)
    if respondio or mem["fallos_paso"] >= 2:  # tras 2 intentos se avanza igual, para no frustrar
        mem["fallos_paso"] = 0
        corto = False
    else:
        mem["fallos_paso"] += 0 if pregunta_aprendiz else 1
        corto = True
    reaccion = ""
    if pregunta_aprendiz:
        sistema = (f"You are {esc['rol_tutor']}. An English learner (level A1-A2) asks you a question. "
                   "Answer in ONE short, friendly sentence (maximum 14 words), very simple English, in your role. "
                   "Do not ask a question back.")
        mensajes = [{"role": "system", "content": sistema}, {"role": "user", "content": lo_que_dijo}]
    else:
        sistema = (f"You are {esc['rol_tutor']}. You talk with an English learner (level A1-A2). "
                   "Reply with ONE short, warm sentence (maximum 12 words) that responds to the learner's answer, "
                   "using their own words. Very simple English. Do not ask a question. Do not correct grammar.")
        mensajes = [{"role": "system", "content": sistema},
                    {"role": "assistant", "content": q_actual}, {"role": "user", "content": lo_que_dijo}]
    if len(texto.split()) >= 2 or pregunta_aprendiz:
        with _candado:
            try:
                reaccion, _ = TT._chat(mensajes, 40, 0.3)
            except Exception:  # noqa: BLE001
                reaccion = ""
        reaccion = re.split(r"(?<=[.!?])\s", reaccion.strip().strip('"'))[0][:160] if reaccion else ""
        if not _reaccion_valida(reaccion, texto, mem["turnos"]) and not pregunta_aprendiz:
            reaccion = _REACCIONES[mem["turnos"] % len(_REACCIONES)]
    if mem.get("nombre") and actual.get("meta") == "presentarse" and respondio:
        reaccion = f"Nice to meet you, {mem['nombre']}!"
    reaccion_voz = _REACCIONES[mem["turnos"] % len(_REACCIONES)]  # versión pregrabada para la voz
    recast = ""
    if corrige_ahora and lo_que_dijo:
        primera = lo_que_dijo.split()[0]
        cuerpo = lo_que_dijo if primera in ("I", "I'm") or primera[:1].isupper() and primera.lower() not in (
            "my", "the", "last", "yesterday", "we", "she", "he", "it", "they", "you", "a", "an") else \
            lo_que_dijo[0].lower() + lo_que_dijo[1:]
        recast = f"Oh, {cuerpo} Can you say it like that?"
    if pregunta_aprendiz:
        sig = paso
        tutor = "So, " + q_actual[0].lower() + q_actual[1:]
    elif corto:
        sig = paso
        ops = actual.get("opciones") or []
        ej = re.search(r"Ej\.?:\s*(.+)$", actual.get("ayuda_es", ""))
        if ops:  # escalera de ayuda: primero opciones, luego un modelo para repetir
            tutor = (f"For example: \"{ops[0]}\" or \"{ops[1]}\"" if len(ops) > 1 and mem["fallos_paso"] <= 1
                     else f"Let me help you. You can say: \"{ops[0]}\"")
        else:
            tutor = (f"Let me help you. You can say: \"{ej.group(1).strip()}\"" if ej else
                     "Can you tell me a little more? " + q_actual)
    else:
        sig = paso + 1
        tutor = esc["pasos"][sig]["tutor"] if sig < len(esc["pasos"]) else ""
    if reaccion and tutor and tutor.lower().startswith(reaccion.lower().rstrip("!.")):
        reaccion = ""  # evita "Interesting! Interesting! ..."
    fin = sig >= len(esc["pasos"])
    resumen = None
    if fin:
        top = sorted(mem["fichas_falladas"].items(), key=lambda kv: -kv[1])[:2]
        resumen = {"turnos": mem["turnos"], "palabras": mem["palabras"],
                   "a_practicar": [FICHAS[f]["regla_es"] for f, _ in top if f in FICHAS],
                   "logros": [FICHAS[f]["regla_es"] for f in mem["logros"] if f in FICHAS],
                   "dilo_otra_vez": mem["pendientes"]}
    out = {"texto": texto, "errores": r["errores"] if corrige_ahora else [], "corrige_ahora": corrige_ahora,
           "palabras": mem["palabras"], "frase_corregida": r["frase_corregida"], "recast": recast,
           "reaccion": reaccion, "tutor": tutor, "paso_siguiente": sig, "fin": fin, "logro": logro, "resumen": resumen,
           "ayuda_es": esc["pasos"][min(sig, len(esc["pasos"]) - 1)]["ayuda_es"],
           "segundos": round(time.perf_counter() - t0, 1), "estado": "ok",
           "pregunta": " ".join(x for x in (recast, reaccion, tutor) if x)}
    pista_voz = next((e["pista"] for e in out["errores"] if e.get("pista")), None)
    # la voz sólo usa frases pregrabadas (misma voz natural siempre); la reacción libre del modelo queda en texto
    out["voz"] = voz_partes(("Can you say it like that?" if recast else "", "en-US"),
                            (reaccion if aid(reaccion) else (reaccion_voz if not corto else ""), "en-US"),
                            (tutor, "en-US"), (pista_voz, "es-CO"),
                            ("Great job! See you next time." if fin else "", "en-US"))
    return out


def rapido(texto):
    """Primer tiempo (< 1 s): sólo lo verificado (fichas + ERG), sin el modelo de lenguaje."""
    texto = " ".join(str(texto).split())[:400]
    t0 = time.perf_counter()
    fijo, cambios = simbolico(texto)
    agrupados = {}
    for c in cambios:
        f = FICHAS.get(c["ficha"]) if c["ficha"] else None
        k = c["ficha"] or c["original"]
        if k in agrupados:
            agrupados[k]["marcas"].append(c["original"])
            continue
        agrupados[k] = {"original": c["original"], "corregido": c["corregido"], "tipo": c["ficha"], "verificada": True,
                        "fuente": c["fuente"], "marcas": [c["original"]],
                        "regla": f["regla_es"] if f else None, "pista": f["pista_es"] if f else None,
                        "ejemplo": f"{f['ejemplo_mal']} → {f['ejemplo_bien']}" if f else None}
    return {"texto": texto, "frase_corregida": fijo, "errores": list(agrupados.values()),
            "segundos": round(time.perf_counter() - t0, 2)}


def turno(texto, ambito):
    texto = " ".join(str(texto).split())[:400]
    t0 = time.perf_counter()
    fijo, cambios = simbolico(texto)
    orig = TT._corregir

    def _corregir(t, acum, version="v1"):
        partes = t.split("\n(Correct this text", 1)
        cola = ("\n(Correct this text" + partes[1]) if len(partes) > 1 else ""
        r = orig(fijo + cola, acum, "v1")
        return r if r is not None else (fijo if cambios else None)

    with _candado:
        TT._corregir = _corregir
        try:
            d = TT.responder_detallado(texto, {"nivel": "A2", "ambito": ambito, "version": "v1"})
        finally:
            TT._corregir = orig
    errores = []
    for e in d["errores"]:
        o = (e.get("original") or "").lower()
        hit = next((c for c in cambios if c["original"].lower() in o or o in c["original"].lower()), None)
        f = FICHAS.get(hit["ficha"]) if hit and hit["ficha"] else None
        errores.append({"original": e.get("original"), "corregido": e.get("corregido"), "tipo": e.get("tipo"),
                        "verificada": bool(hit), "fuente": hit["fuente"] if hit else "modelo",
                        "regla": f["regla_es"] if f else None, "pista": f["pista_es"] if f else None,
                        "ejemplo": f"{f['ejemplo_mal']} → {f['ejemplo_bien']}" if f else None})
    agrupados = {}  # una pista por ficha (o por tipo, si es sugerencia del modelo); se juntan los trozos marcados
    for e in errores:
        k = e["regla"] or ("modelo:" + str(e["tipo"]))
        if k in agrupados:
            agrupados[k]["marcas"].append(e["original"])
        else:
            agrupados[k] = {**e, "marcas": [e["original"]]}
    out = {"texto": texto, "frase_corregida": d["frase_corregida"], "errores": list(agrupados.values()),
           "pregunta": d["pregunta_siguiente"], "estado": d["estado"], "segundos": round(time.perf_counter() - t0, 1)}
    return out


PAGINA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Tutor de inglés sin internet</title>
<style>
:root{--fondo:#f6f4ee;--tarjeta:#fff;--texto:#1f2a24;--suave:#5f6b64;--verde:#2f6b3f;--rojo:#a23b2a;--ambar:#9a6a00;--borde:#ddd8cc}
*{box-sizing:border-box} body{margin:0;background:var(--fondo);color:var(--texto);font:18px/1.45 system-ui,"Segoe UI",Arial,sans-serif}
header{padding:14px 18px;background:var(--verde);color:#fff} header h1{margin:0;font-size:1.25em} header p{margin:2px 0 0;opacity:.85;font-size:.85em}
main{max-width:860px;margin:0 auto;padding:14px} #chat{display:flex;flex-direction:column;gap:10px;min-height:40vh}
.burbuja{background:var(--tarjeta);border:1px solid var(--borde);border-radius:12px;padding:12px 14px}
.yo{align-self:flex-end;background:#e7efe5;max-width:85%} .tutor{max-width:95%} .meta{color:var(--suave);font-size:.75em;margin-top:6px}
mark{background:#f6d8d2;color:var(--rojo);padding:0 3px;border-radius:4px;font-weight:600}
.pista{margin:8px 0;padding:8px 10px;border-left:4px solid var(--verde);background:#f1f6f0;border-radius:6px}
.pista.modelo{border-color:var(--ambar);background:#fbf5e6} .etq{font-size:.72em;font-weight:700;letter-spacing:.03em;text-transform:uppercase}
.etq.v{color:var(--verde)} .etq.m{color:var(--ambar)} details{margin-top:6px} summary{cursor:pointer;color:var(--verde);font-weight:600}
.ok{color:var(--verde);font-weight:600} form{display:flex;gap:8px;margin-top:14px;position:sticky;bottom:0;background:var(--fondo);padding:10px 0}
input{flex:1;font-size:1em;padding:12px;border:1px solid var(--borde);border-radius:10px} button{font-size:1em;padding:12px 18px;border:0;border-radius:10px;background:var(--verde);color:#fff}
button:disabled{opacity:.5} select{font-size:.9em;padding:6px;border-radius:8px}
</style></head><body>
<header><h1>Tutor de inglés · sin internet</h1><p>Corre en un Chromebook de 2014 (Celeron, 4 GB). Las reglas salen de las fichas del profe.
 · Código de sesión: <b id="ses"></b> (anónimo, sin nombres) · <a href="/api/registro.csv" style="color:#fff">registro CSV</a></p></header>
<main><div id="chat"><div class="burbuja tutor">Hello! Tell me about your work or your town. <span class="meta">(Escribe una frase en inglés)</span></div></div>
<form id="f"><select id="ambito"><option value="agricola">campo</option><option value="tecnico">técnico</option></select>
<input id="t" autocomplete="off" placeholder="Write a sentence in English..." autofocus><button id="b">Enviar</button></form></main>
<script>
const q=new URLSearchParams(location.search);
const sesion=(q.get("sesion")&&/^[A-Za-z0-9_-]{1,24}$/.test(q.get("sesion")))?q.get("sesion"):"S-"+Math.random().toString(16).slice(2,6).toUpperCase();
document.getElementById("ses").textContent=sesion;
const chat=document.getElementById("chat");
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e;}
function resalta(texto, errores){const p=el("div");let resto=texto;
  const trozos=errores.flatMap(e=>e.marcas||[e.original]).filter(Boolean);
  if(!trozos.length){p.textContent=texto;return p;}
  const re=new RegExp("("+trozos.map(s=>s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|")+")","gi");
  texto.split(re).forEach(s=>{ if(trozos.some(t=>t.toLowerCase()===s.toLowerCase())) p.appendChild(el("mark","",s)); else p.appendChild(document.createTextNode(s)); });
  return p;}
function pinta(espera,d,final){espera.textContent="";
    if(d.error){espera.textContent="Error: "+d.error;return;}
    if(final&&!d.frase_corregida){espera.textContent="No logré analizar esa frase. ¿La escribes de otra forma?";return;}
    if(!d.errores.length){ if(final){espera.appendChild(el("div","ok","¡Muy bien! No encontré errores."));} }
    else{espera.appendChild(el("div","","Mira las partes marcadas:")); espera.appendChild(resalta(d.texto,d.errores));
      for(const e of d.errores){const c=el("div","pista"+(e.verificada?"":" modelo"));
        c.appendChild(el("div","etq "+(e.verificada?"v":"m"), e.verificada?"Regla verificada · "+e.fuente:"Sugerencia del modelo · revisar"));
        if(e.pista){c.appendChild(el("div","",(/^pista/i.test(e.pista)?"":"Pista: ")+e.pista));}
        else{c.appendChild(el("div","","Revisa «"+(e.original||"esa parte")+"» ("+(e.tipo||"").replaceAll("_"," ")+")."));}
        if(e.regla){const r2=el("div","meta","Regla: "+e.regla+(e.ejemplo?"  ·  Ej.: "+e.ejemplo:""));c.appendChild(r2);}
        espera.appendChild(c);}
      espera.appendChild(el("div","meta","Intenta escribirla de nuevo abajo."));
      if(final){const det=el("details"); det.appendChild(el("summary","","Ver corrección")); det.appendChild(el("div","",d.frase_corregida)); espera.appendChild(det);}}
    if(!final){espera.appendChild(el("div","meta",(d.errores.length?"Reglas en ":"Revisando… primera mirada en ")+d.segundos+" s · el tutor sigue leyendo tu frase…"));return;}
    if(d.pregunta){espera.appendChild(el("div","","Tutor: "+d.pregunta));}
    espera.appendChild(el("div","meta","primera respuesta "+(espera.dataset.t1||"?")+" s · completa "+d.segundos+" s · sin internet"));}
document.getElementById("f").addEventListener("submit",async ev=>{ev.preventDefault();
  const inp=document.getElementById("t"),texto=inp.value.trim(); if(!texto)return;
  inp.value=""; const b=document.getElementById("b"); b.disabled=true;
  chat.appendChild(el("div","burbuja yo",texto)); const espera=el("div","burbuja tutor","mirando…"); chat.appendChild(espera); espera.scrollIntoView();
  const cuerpo=JSON.stringify({texto,sesion,tipo_entrada:"texto",ambito:document.getElementById("ambito").value});
  const opts={method:"POST",headers:{"Content-Type":"application/json"},body:cuerpo};
  const completo=fetch("/api/turno",opts).then(r=>r.json());
  let listo=false;
  fetch("/api/rapido",opts).then(r=>r.json()).then(d=>{ if(!listo&&!d.error){espera.dataset.t1=d.segundos; pinta(espera,d,false); espera.scrollIntoView();} }).catch(()=>{});
  try{const d=await completo; listo=true; pinta(espera,d,true);
  }catch(e){espera.textContent="Se perdió la conexión con el Chromebook.";}
  b.disabled=false; inp.focus(); espera.scrollIntoView();});
</script></body></html>"""


PAGINA_PRACTICA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Practica inglés conmigo</title>
<style>
:root{--fondo:#f7f1e3;--tarjeta:#fffdf7;--texto:#22291f;--suave:#5d5a4b;--verde:#2d5f3a;--verde2:#3f7d4e;--tierra:#9b5a2f;--tierra2:#c9824a;--sol:#f2b82e;--sol2:#fff1c2;--rojo:#a3321f;--borde:#e0d5ba;--claro:#e3efd9;--sombra:0 4px 14px rgba(60,45,20,.12)}
*{box-sizing:border-box}
html{font-size:18px}
@media(min-width:1200px){html{font-size:20px}}
body{margin:0;background:var(--fondo);background-image:radial-gradient(circle at 100% 0,#f2dfae 0,transparent 40%),radial-gradient(circle at 0 100%,#d9e8cc 0,transparent 40%);background-attachment:fixed;color:var(--texto);font:1rem/1.45 system-ui,"Segoe UI",Roboto,Arial,sans-serif;overflow-x:hidden}
a{color:inherit}
:focus-visible{outline:3px solid var(--sol);outline-offset:2px;box-shadow:0 0 0 5px var(--verde)}
header{padding:8px 14px;background:linear-gradient(90deg,var(--verde),var(--verde2));color:#fff;display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;font-size:.8rem}
header a{color:#fff;font-weight:600} header .nav{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
main{max-width:860px;margin:0 auto;padding:12px 14px 4px}
button{font:inherit;padding:.5em 1em;border:0;border-radius:12px;background:var(--verde);color:#fff;cursor:pointer;min-height:44px;transition:transform .15s,background .15s}
button:hover{background:var(--verde2);transform:translateY(-1px)}
button.sec{background:#fff;color:var(--verde);border:2px solid var(--verde)} button.sec:hover{background:var(--claro)}
header button{min-height:36px;padding:.2em .8em;font-size:.9em;background:rgba(255,255,255,.18);color:#fff;border:1px solid rgba(255,255,255,.6)}
button:disabled{opacity:.5;cursor:default}
.oculto{display:none!important}
.hero{text-align:center;padding:14px 0 8px}
.hero .mont{width:min(320px,70%);height:auto;display:block;margin:0 auto 4px}
.hero h1{margin:0;font-size:2rem;line-height:1.15;color:var(--verde)}
.hero .sub{margin:6px 0 0;color:var(--tierra);font-weight:700;font-size:.95rem}
.hero .intro{margin:10px auto 0;max-width:36em;color:var(--suave);font-size:.95rem}
.grupo{margin:16px 0 6px;font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;color:var(--tierra);font-weight:800;display:flex;align-items:center;gap:8px}
.grupo::after{content:"";flex:1;height:2px;background:var(--borde)}
.esc{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.card{display:flex;gap:12px;align-items:center;text-align:left;width:100%;background:var(--tarjeta);color:var(--texto);border:2px solid var(--borde);border-radius:18px;padding:14px;box-shadow:var(--sombra);min-height:96px}
.card:hover{background:#fff;border-color:var(--verde2);transform:translateY(-3px)}
.card .ic{flex:none;width:58px;height:58px;border-radius:16px;display:grid;place-items:center;font-size:2rem;background:var(--sol2)}
.card h2{margin:0 0 2px;font-size:1.02rem;color:var(--verde);line-height:1.2} .card p{margin:0;color:var(--suave);font-size:.85rem;line-height:1.3}
.cab{position:sticky;top:0;z-index:5;background:var(--fondo);padding:6px 0 4px;border-bottom:2px solid var(--borde)}
.tutorcab{display:flex;align-items:center;gap:12px}
.avatar{position:relative;flex:none;width:68px;height:68px}
.avatar svg{width:100%;height:100%;display:block;position:relative;z-index:1}
.avatar::before,.avatar::after{content:"";position:absolute;inset:0;border-radius:50%;border:3px solid var(--sol);opacity:0}
.avatar.habla::before{animation:onda 1.3s ease-out infinite}
.avatar.habla::after{animation:onda 1.3s ease-out .65s infinite}
.avatar.habla svg{animation:pulso .55s ease-in-out infinite alternate}
.avatar.habla .boca{animation:boca .3s ease-in-out infinite alternate}
.boca{transform-origin:50px 69px}
.avatar.real svg,.avatar.real .boca{animation:none}
.cabeza{transform-origin:50px 90px;animation:ladea 7s ease-in-out infinite}
.avatar.habla .cabeza{animation-duration:3.4s}
@keyframes ladea{0%,100%{transform:rotate(-1.6deg)}50%{transform:rotate(1.8deg)}}
.ojos{transform-origin:50px 49px;transition:transform .07s}
.avatar.parpadea .ojos{transform:scaleY(.08)}
@keyframes onda{0%{transform:scale(.9);opacity:.9}100%{transform:scale(1.55);opacity:0}}
@keyframes pulso{to{transform:scale(1.05)}}
@keyframes boca{to{transform:scaleY(1.9)}}
.quien{min-width:0;flex:1} .quien b{display:block;font-size:1.1rem;color:var(--verde);line-height:1.15} .quien span{font-size:.8rem;color:var(--suave)}
.stats{text-align:right;font-size:.8rem;color:var(--suave)} .stats b{display:inline-block;background:var(--sol2);border:1px solid var(--sol);border-radius:14px;padding:2px 10px;color:var(--texto);font-size:.9rem}
#pasos{display:flex;gap:6px;align-items:center;margin:6px 0 0;flex-wrap:wrap}
.pas{width:26px;height:26px;border-radius:50%;border:2px solid var(--borde);background:#fff;display:grid;place-items:center;font-size:.7rem;font-weight:700;color:var(--suave);transition:all .3s}
.pas.hecho{background:var(--verde);border-color:var(--verde);color:#fff}
.pas.ahora{border-color:var(--tierra2);background:var(--sol2);color:var(--texto);box-shadow:0 0 0 3px rgba(242,184,46,.4)}
.lin{flex:1;min-width:6px;max-width:26px;height:3px;background:var(--borde);border-radius:2px} .lin.hecho{background:var(--verde)}
#chat{display:flex;flex-direction:column;gap:10px;padding:12px 0 8px;min-height:35vh}
.b{border-radius:18px;padding:10px 14px;max-width:88%;animation:entra .35s ease-out both;overflow-wrap:anywhere;box-shadow:0 1px 4px rgba(60,45,20,.1)}
@keyframes entra{from{opacity:0;transform:translateY(10px) scale(.97)}to{opacity:1;transform:none}}
.tutor{background:var(--tarjeta);border:1px solid var(--borde);border-top-left-radius:4px;align-self:flex-start}
.yo{align-self:flex-end;background:var(--claro);border:1px solid #c5dcb5;border-top-right-radius:4px}
.recast{font-style:italic;color:var(--verde);font-weight:600}
.meta{color:var(--suave);font-size:.75rem}
summary{cursor:pointer;color:var(--tierra);font-weight:700;font-size:.85rem;min-height:32px} details[open] summary{margin-bottom:4px}
.pista{margin-top:8px;display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border-radius:14px;background:var(--sol2);border:1px solid #ecd27c;font-size:.9rem}
.pista .ico{flex:none;font-size:1.4rem;line-height:1.2}
.pista.ayuda{align-self:flex-start;max-width:88%;animation:entra .35s ease-out both}
mark{background:#f8d5cb;color:var(--rojo);border-radius:4px;padding:0 3px;font-weight:600}
.logro{align-self:center;display:flex;align-items:center;gap:8px;background:linear-gradient(90deg,#fff3c4,#ffe28a);border:2px solid var(--sol);color:#4a3600;border-radius:30px;padding:6px 16px 6px 10px;font-weight:700;font-size:.9rem;animation:insignia .7s cubic-bezier(.2,1.6,.4,1) both}
.logro .st{font-size:1.5rem;display:inline-block;animation:gira 1.4s ease-in-out .5s 2}
@keyframes insignia{from{opacity:0;transform:scale(.3) rotate(-8deg)}to{opacity:1;transform:none}}
@keyframes gira{50%{transform:rotate(25deg) scale(1.3)}}
.escribe{display:flex;gap:6px;align-items:center;padding:14px 16px} .escribe i{width:10px;height:10px;border-radius:50%;background:var(--tierra2);animation:punto 1.1s ease-in-out infinite}
.escribe i:nth-child(2){animation-delay:.18s}.escribe i:nth-child(3){animation-delay:.36s}
@keyframes punto{0%,70%,100%{transform:translateY(0);opacity:.45}35%{transform:translateY(-7px);opacity:1}}
.fila{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.fila button{font-size:.8rem;min-height:40px;padding:.3em .9em}
.pie{position:sticky;bottom:0;z-index:5;background:var(--fondo);padding:6px 0 10px;border-top:2px solid var(--borde)}
.pie .fila{margin:0 0 6px}
form{display:flex;gap:8px}
input{flex:1;min-width:0;font:inherit;padding:12px 14px;border:2px solid var(--borde);border-radius:14px;background:#fff;color:var(--texto)}
input:focus{border-color:var(--verde)}
form button{padding:.5em 1.3em;font-weight:700;background:var(--tierra)} form button:hover{background:var(--tierra2)}
.resumen{align-self:stretch;background:linear-gradient(180deg,#fff8dc,var(--tarjeta) 45%);border:3px solid var(--sol);border-radius:22px;padding:18px;text-align:center;box-shadow:var(--sombra);animation:entra .5s ease-out both}
.resumen h2{margin:0;color:var(--verde);font-size:1.6rem}
.estrellas{font-size:2.6rem;letter-spacing:6px;margin:4px 0}
.estrellas span{display:inline-block;opacity:0;animation:insignia .6s cubic-bezier(.2,1.6,.4,1) forwards}
.estrellas .off{filter:grayscale(1)}
.cifras{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:8px 0}
.cifras div{background:#fff;border:2px solid var(--borde);border-radius:16px;padding:6px 16px;min-width:110px} .cifras b{display:block;font-size:1.8rem;color:var(--tierra);line-height:1.1} .cifras span{font-size:.75rem;color:var(--suave)}
.resumen .mej{color:var(--verde);font-weight:600;margin:6px 0}
.resumen h3{margin:14px 0 6px;font-size:1.05rem;color:var(--tierra)}
.dilo{text-align:left;background:#fff;border:2px solid var(--borde);border-left:6px solid var(--verde);border-radius:12px;padding:8px 12px;margin:8px 0}
.dilo .d{color:var(--rojo)} .dilo .m{color:var(--verde);font-weight:700}
.btnpreg{background:#fff;color:var(--tierra);border:2px solid var(--tierra2);font-weight:700}
.btnpreg:hover{background:var(--sol2)}
.hero .btnpreg{margin-top:12px;font-size:1rem}
#preg{position:fixed;inset:0;z-index:50;background:rgba(34,41,31,.55);display:flex;align-items:flex-end;justify-content:center}
#preg .caja{background:var(--fondo);width:min(640px,100%);max-height:92vh;display:flex;flex-direction:column;border-radius:20px 20px 0 0;border:3px solid var(--sol);box-shadow:var(--sombra)}
@media(min-height:560px) and (min-width:700px){#preg{align-items:center}#preg .caja{border-radius:20px;max-height:86vh}}
#preg .top{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 14px;border-bottom:2px solid var(--borde)}
#preg .top b{color:var(--verde);font-size:1.05rem}
#pchat{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:10px;padding:12px 14px;min-height:120px}
#prel{padding:0 14px}
#pf{padding:8px 14px 12px}
.resumen>button{margin-top:12px;font-size:1.05rem;padding:.6em 1.6em;background:var(--tierra)}
@media(max-width:480px){html{font-size:17px}.hero h1{font-size:1.65rem}.esc{grid-template-columns:1fr}.avatar{width:56px;height:56px}.b{max-width:94%}.stats{font-size:.7rem}.estrellas{font-size:2.2rem}}
@media(max-height:800px) and (min-width:900px){.hero .mont{width:200px}.hero{padding:4px 0}.card{min-height:84px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition:none!important}}
</style></head><body>
<header><div>Sin internet · sesión <b id="ses"></b> (anónima)</div>
<div class="nav"><button id="voz" type="button" aria-label="Activar o desactivar la voz">🔊 Voz: sí</button> <a href="/corrector">corrector</a> · <a href="/api/registro.csv">CSV</a></div></header>
<main>
<section id="inicio">
<div class="hero">
<svg class="mont" viewBox="0 0 320 110" aria-hidden="true"><circle cx="262" cy="30" r="18" fill="#f2b82e"/><path d="M0 110 L70 36 L112 80 L170 18 L250 110Z" fill="#3f7d4e"/><path d="M120 110 L215 50 L270 95 L320 62 V110Z" fill="#2d5f3a"/><path d="M170 18 L152 40 L166 36 L172 46 L180 34 L190 42Z" fill="#fffdf7"/><path d="M0 110 H320 V100 Q160 84 0 100Z" fill="#9b5a2f"/></svg>
<h1>Practica inglés conmigo</h1>
<p class="sub">Hecho para reducir la brecha educativa · Sin internet · Málaga, Santander</p>
<p class="sub" style="opacity:.8;font-size:.85em">Creado por Christiam Puentes · Instructor de inglés, SENA</p>
<p class="intro">Elige una situación. Yo hago un papel y tú practicas hablando conmigo en inglés. Si te equivocas, te ayudo sin parar la conversación.</p>
<button type="button" class="btnpreg" id="pregInicio">❓ Pregúntale al tutor</button>
</div>
<div id="lista"></div>
</section>
<section id="sala" class="oculto">
<div class="cab">
<div class="tutorcab"><div class="avatar" id="avatar"></div>
<div class="quien"><b id="nombre"></b><span id="rol"></span></div>
<div class="stats"><div id="titulo"></div><b id="palabras">0 palabras</b></div></div>
<div id="pasos" aria-label="Progreso"></div>
</div>
<div id="chat" aria-live="polite"></div>
<div class="pie">
<div class="fila"><button class="sec" id="ayuda" type="button">💡 Ayuda</button><button class="sec" id="otra" type="button">Cambiar de situación</button><button class="btnpreg" id="pregSala" type="button">❓ Pregúntale al tutor</button></div>
<form id="f"><input id="t" autocomplete="off" aria-label="Escribe tu respuesta en inglés" placeholder="Answer in English..."><button id="b">Enviar</button></form>
</div></section>
</main>
<div id="preg" class="oculto" role="dialog" aria-modal="true" aria-labelledby="ptit">
<div class="caja"><div class="top"><b id="ptit">❓ Pregúntale al tutor</b><button class="sec" id="pcierra" type="button" aria-label="Cerrar">✕ Cerrar</button></div>
<div id="pchat" aria-live="polite"></div><div id="prel" class="fila"></div>
<form id="pf"><input id="pt" autocomplete="off" maxlength="300" aria-label="Escribe tu pregunta en español o en inglés" placeholder="Pregunta en español o en inglés..."><button id="pb">Preguntar</button></form></div></div>
<script>
const q=new URLSearchParams(location.search);
const sesion=(q.get("sesion")&&/^[A-Za-z0-9_-]{1,24}$/.test(q.get("sesion")))?q.get("sesion"):"S-"+Math.random().toString(16).slice(2,6).toUpperCase();
document.getElementById("ses").textContent=sesion;
let esc=null, paso=0, ayudaActual="", voz=true;
const chat=document.getElementById("chat");
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e;}
const NS="http://www.w3.org/2000/svg";
const PERS={tienda:["Don Pedro","Tendero","🛒","#9b5a2f","#6b4a2b","sombrero"],entrevista:["Laura","Entrevistadora","💼","#2d5f3a","#3b2a1d","largo"],proyecto:["Sam","Compañero de proyecto","🛠️","#3a6ea5","#2a2a2a","corto"],
 gr1:["Rosa","García Rovira","🌄","#b8472f","#4a2c1a","largo"],gr2:["Daniel","García Rovira","⛰️","#2d5f3a","#2a1f18","corto"],gr3:["Camila","García Rovira","🌿","#8a4f9e","#2a1f18","largo"],gr4:["Marta","García Rovira","🏡","#c47a1a","#cfcfcf","moño"]};
function perso(e){const p=PERS[e.id]||["Tutor","Tu tutor de inglés","💬","#2d5f3a","#3b2a1d","corto"];
  let nombre=p[0], rol=p[1], tipo=p[5];
  if(e.rol_tutor&&typeof e.rol_tutor==="string"){const w=e.rol_tutor.trim().split(/\s+/); if(w[0]){nombre=w[0]; if(/^(don|doña|dona|mr\.?|mrs\.?|ms\.?|miss)$/i.test(w[0])&&w[1])nombre=w[0]+" "+w[1]; rol=e.rol_tutor;}}
  return {nombre,rol,ico:p[2],piel:"#e8b98a",ropa:p[3],pelo:p[4],tipo};}
function avatarSVG(P){const s=document.createElementNS(NS,"svg"); s.setAttribute("viewBox","0 0 100 100"); s.setAttribute("role","img"); s.setAttribute("aria-label","Avatar de "+P.nombre);
  let h='<circle cx="50" cy="50" r="48" fill="#fff1c2" stroke="'+P.ropa+'" stroke-width="3"/><path d="M14 92 Q50 58 86 92 A48 48 0 0 1 14 92Z" fill="'+P.ropa+'"/><g class="cabeza">';
  if(P.tipo==="largo"||P.tipo==="moño")h+='<path d="M24 52 Q22 18 50 16 Q78 18 76 52 L76 76 Q64 70 66 52 L34 52 Q36 70 24 76Z" fill="'+P.pelo+'"/>';
  h+='<ellipse cx="50" cy="50" rx="23" ry="26" fill="'+P.piel+'"/>';
  h+='<path d="M27 46 Q28 22 50 22 Q72 22 73 46 Q62 34 50 34 Q38 34 27 46Z" fill="'+P.pelo+'"/>';
  if(P.tipo==="moño")h+='<circle cx="50" cy="15" r="8" fill="'+P.pelo+'"/>';
  if(P.tipo==="sombrero")h+='<ellipse cx="50" cy="26" rx="34" ry="6" fill="#d9a441"/><path d="M32 26 Q34 8 50 8 Q66 8 68 26Z" fill="#e8bd5a"/><rect x="32" y="22" width="36" height="5" fill="#6b4a2b"/>';
  h+='<g class="ojos"><circle cx="41" cy="49" r="3.2" fill="#222"/><circle cx="59" cy="49" r="3.2" fill="#222"/><circle cx="42" cy="48" r="1" fill="#fff"/><circle cx="60" cy="48" r="1" fill="#fff"/></g>';
  h+='<path d="M36 41 Q41 38 46 41M54 41 Q59 38 64 41" stroke="'+P.pelo+'" stroke-width="2" fill="none" stroke-linecap="round"/>';
  h+='<circle cx="35" cy="59" r="4" fill="#e58b7a" opacity=".5"/><circle cx="65" cy="59" r="4" fill="#e58b7a" opacity=".5"/>';
  if(P.tipo==="sombrero")h+='<path d="M38 62 Q50 58 62 62 Q56 66 50 64 Q44 66 38 62Z" fill="#5a3a22"/>';
  h+='<ellipse class="boca" cx="50" cy="69" rx="7" ry="3" fill="#8a2f2f"/></g>';
  s.innerHTML=h; return s;}
const avatar=document.getElementById("avatar");
const SIN_MOV=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
let actx=null, anal=null, buf=null, raf=0, analizando=false, apertura=0, bocaEl=null;
// El AudioContext se crea o reanuda dentro de un gesto del usuario (clic en un escenario o en una pregunta)
function prepararAudio(){ try{
  if(!actx){ const AC=window.AudioContext||window.webkitAudioContext; if(!AC)return;
    actx=new AC(); anal=actx.createAnalyser(); anal.fftSize=512; anal.smoothingTimeConstant=.2; buf=new Float32Array(anal.fftSize); anal.connect(actx.destination); }
  if(actx.state==="suspended")actx.resume().catch(()=>{});
 }catch(e){actx=null;anal=null;} }
function conectaAnalisis(a){ // true sólo si el audio pasa por el analizador y el contexto está corriendo (si no, el audio quedaría mudo)
  try{ if(!actx||!anal||actx.state!=="running"||!anal.getFloatTimeDomainData)return false; const src=actx.createMediaElementSource(a); src.connect(anal); return true; }catch(e){return false;} }
function pintaBoca(v){ bocaEl=avatar.querySelector(".boca"); if(!bocaEl)return;
  bocaEl.style.transform=v===null?"":"scale("+(1-0.18*v).toFixed(2)+","+(0.3+3.1*v).toFixed(2)+")"; }
function bucle(){ if(!analizando)return;
  anal.getFloatTimeDomainData(buf); let s=0; for(let i=0;i<buf.length;i++)s+=buf[i]*buf[i];
  const rms=Math.sqrt(s/buf.length), obj=Math.min(1,rms*6);
  apertura+=(obj>apertura?0.6:0.25)*(obj-apertura); pintaBoca(apertura);
  raf=requestAnimationFrame(bucle); }
function iniciaAnalisis(){ analizando=true; apertura=0; avatar.classList.add("real"); cancelAnimationFrame(raf); raf=requestAnimationFrame(bucle); }
function paraAnalisis(){ analizando=false; cancelAnimationFrame(raf); avatar.classList.remove("real"); pintaBoca(null); }
function hablando(si){avatar.classList.toggle("habla",!!si); if(!si)paraAnalisis();}
// parpadeo ocasional
(function parpadeo(){ if(SIN_MOV)return; setTimeout(()=>{ avatar.classList.add("parpadea"); setTimeout(()=>{avatar.classList.remove("parpadea"); parpadeo();},140); },2500+Math.random()*3500); })();
let cola=0, sonando=null;
let velocidad=1.0;
function suena(p){return new Promise(res=>{
  if(p.audio){ const a=new Audio("/audio/"+p.audio+".wav"); a.playbackRate=velocidad; a.preservesPitch=true; sonando=a; hablando(true); if(conectaAnalisis(a))iniciaAnalisis(); const fin=()=>{hablando(false);res();}; a.onended=fin; a.onerror=fin; a.play().catch(fin); return; }
  // 5-nov: la voz del navegador sonaba distinta a la pregrabada (Kokoro) y se oía raro; sólo suena la voz natural
  res();});}
async function reproduce(partes,vel){ velocidad=vel||1.0; const mia=++cola; if(sonando){sonando.pause();} if(window.speechSynthesis)speechSynthesis.cancel(); hablando(false);
  if(!voz)return; for(const p of (partes||[])){ if(mia!==cola||!voz)return; await suena(p); } }
// botones de escucha: repetir, más despacio y ver el texto (primero se escucha, después se lee)
function controlesEscucha(b,partes){ if(!partes||!partes.length)return;
  const f=el("div","fila"); const r=el("button","sec","🔁 Repetir"); r.type="button"; r.onclick=()=>reproduce(partes,1.0);
  const d=el("button","sec","🐢 Más despacio"); d.type="button"; d.onclick=()=>reproduce(partes,0.75);
  f.appendChild(r); f.appendChild(d); b.appendChild(f); }
document.getElementById("voz").onclick=()=>{voz=!voz;document.getElementById("voz").textContent="🔊 Voz: "+(voz?"sí":"no"); if(!voz){cola++; if(sonando)sonando.pause(); if(window.speechSynthesis)speechSynthesis.cancel(); hablando(false);}};
function progreso(){const c=document.getElementById("pasos"); c.textContent=""; const n=esc.n_pasos||1;
  for(let i=0;i<n;i++){ if(i>0)c.appendChild(el("span","lin"+(i<=paso?" hecho":"")));
    const k=i<paso?"hecho":(i===paso?"ahora":""); c.appendChild(el("span","pas "+k,i<paso?"✓":String(i+1)));}
  c.setAttribute("aria-label","Paso "+Math.min(paso+1,n)+" de "+n);}
function bajar(n){n.scrollIntoView({behavior:"smooth",block:"nearest"});}
function tutorDice(partes,escuchaPrimero){const b=el("div","b tutor");
  const cont=escuchaPrimero&&voz?el("details"):b;
  if(cont!==b){ cont.appendChild(el("summary","","👀 ver texto")); b.appendChild(cont); }
  for(const [cls,txt] of partes){ if(txt) cont.appendChild(el("div",cls,txt)); }
  chat.appendChild(b); bajar(b); return b;}
function tarjetaPista(txt){const p=el("div","pista"); p.appendChild(el("span","ico","💡")); p.appendChild(el("div","",txt)); return p;}
function escribiendo(){const b=el("div","b tutor escribe"); b.setAttribute("aria-label","escribiendo…"); b.appendChild(el("i")); b.appendChild(el("i")); b.appendChild(el("i")); chat.appendChild(b); bajar(b); return b;}
function marca(texto,errores){const p=el("div");const tro=errores.flatMap(e=>e.marcas||[]).filter(Boolean);
  if(!tro.length){p.textContent=texto;return p;}
  const re=new RegExp("("+tro.map(s=>s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|")+")","gi");
  texto.split(re).forEach(s=>{ if(tro.some(t=>t.toLowerCase()===s.toLowerCase())) p.appendChild(el("mark","",s)); else p.appendChild(document.createTextNode(s)); }); return p;}
function tarjetaEsc(e){const c=el("button","card"); c.type="button"; const P=perso(e);
  c.appendChild(el("span","ic",P.ico)); const t=el("span"); t.appendChild(el("h2","",e.titulo)); t.appendChild(el("p","",e.meta_es)); c.appendChild(t); c.onclick=()=>empieza(e); return c;}
let LISTA=[];
function pintaLista(){const L=document.getElementById("lista"); L.textContent="";
  const gr=LISTA.filter(e=>/^gr[1-4]$/.test(e.id)), otras=LISTA.filter(e=>!/^gr[1-4]$/.test(e.id));
  if(otras.length){L.appendChild(el("div","grupo","Situaciones")); const g=el("div","esc"); otras.forEach(e=>g.appendChild(tarjetaEsc(e))); L.appendChild(g);}
  if(gr.length){L.appendChild(el("div","grupo","García Rovira")); const g=el("div","esc"); gr.forEach(e=>g.appendChild(tarjetaEsc(e))); L.appendChild(g);}}
fetch("/api/escenarios",{method:"POST"}).then(r=>r.json()).then(l=>{LISTA=l; pintaLista();}).catch(()=>{document.getElementById("lista").textContent="No se pudo cargar la lista de situaciones.";});
function empieza(e){prepararAudio(); esc=e; paso=0; chat.textContent=""; ayudaActual=e.ayuda_es;
  document.getElementById("inicio").classList.add("oculto"); document.getElementById("sala").classList.remove("oculto");
  const P=perso(e); avatar.textContent=""; avatar.appendChild(avatarSVG(P)); hablando(false);
  document.getElementById("nombre").textContent=P.nombre; document.getElementById("rol").textContent=P.rol;
  document.getElementById("titulo").textContent=e.titulo; document.getElementById("palabras").textContent="0 palabras"; progreso();
  if(e.vocabulario&&e.vocabulario.length){ // antes de la tarea: palabras clave del módulo
    const v=el("div","b tutor"); v.appendChild(el("div","meta","Palabras para hoy (toca para ver en español)"));
    const f=el("div","fila"); for(const w of e.vocabulario){ const c=el("button","sec",w.en); c.type="button";
      c.onclick=()=>{c.textContent=(c.textContent===w.en)?(w.en+" = "+w.es):w.en;}; f.appendChild(c);} v.appendChild(f); chat.appendChild(v);}
  const pi=[{texto:e.inicio,lang:"en-US",audio:e.inicio_audio}]; const b0=tutorDice([["",e.inicio]],true); controlesEscucha(b0,pi);
  reproduce(pi); document.getElementById("t").focus();}
function otraSituacion(){cola++; if(sonando)sonando.pause(); hablando(false); document.getElementById("sala").classList.add("oculto");document.getElementById("inicio").classList.remove("oculto"); window.scrollTo(0,0);}
document.getElementById("otra").onclick=otraSituacion;
document.getElementById("ayuda").onclick=()=>{const p=tarjetaPista(ayudaActual); p.className="pista ayuda"; chat.appendChild(p); bajar(p);};
function resumenFinal(R){const r=el("div","resumen");
  r.appendChild(el("h2","","¡Terminaste! 🎉"));
  const nd=(R.dilo_otra_vez||[]).length, n=nd===0?3:(nd<=2?2:1);
  const es=el("div","estrellas"); es.setAttribute("aria-label",n+" de 3 estrellas");
  for(let i=0;i<3;i++){const s=el("span",i<n?"":"off","⭐"); s.style.animationDelay=(0.3+i*0.35)+"s"; es.appendChild(s);} r.appendChild(es);
  const c=el("div","cifras"); for(const [v,l] of [[R.palabras,"palabras en inglés"],[R.turnos,"turnos"]]){const d=el("div"); d.appendChild(el("b","",String(v))); d.appendChild(el("span","",l)); c.appendChild(d);} r.appendChild(c);
  if(R.logros&&R.logros.length) r.appendChild(el("div","mej","⭐ Mejoraste: "+R.logros.join("; ")));
  if(nd){ r.appendChild(el("h3","","Dilo otra vez, así:"));
    for(const p of R.dilo_otra_vez){ const x=el("div","dilo"); x.appendChild(el("div","d","Dijiste: "+p.dijiste)); x.appendChild(el("div","m","Mejor: "+p.mejor)); if(p.regla) x.appendChild(el("div","meta",p.regla)); r.appendChild(x);} }
  else if(R.a_practicar&&R.a_practicar.length){ r.appendChild(el("h3","","Para la próxima, practica:")); r.appendChild(el("div","",R.a_practicar.join("; "))); }
  const bo=el("button","","Practicar otra situación"); bo.type="button"; bo.onclick=otraSituacion; r.appendChild(bo);
  chat.appendChild(r); bajar(r);}
document.getElementById("f").addEventListener("submit",async ev=>{ev.preventDefault();
  const inp=document.getElementById("t"),texto=inp.value.trim(); if(!texto||!esc)return; inp.value=""; const btn=document.getElementById("b"); btn.disabled=true;
  const mio=el("div","b yo",texto); chat.appendChild(mio); bajar(mio);
  const cuerpo=JSON.stringify({texto,sesion,escenario:esc.id,paso}); const opts={method:"POST",headers:{"Content-Type":"application/json"},body:cuerpo};
  const pens=escribiendo();
  try{const d=await (await fetch("/api/practica",opts)).json(); pens.remove();
    if(d.error){tutorDice([["meta","Error: "+d.error]]);}
    else{ if(d.errores&&d.errores.length){ mio.textContent=""; mio.appendChild(marca(texto,d.errores));
        for(const e of d.errores){ if(e.pista){ mio.appendChild(tarjetaPista((/^pista/i.test(e.pista)?"":"Pista: ")+e.pista)); } } }
      document.getElementById("palabras").textContent=d.palabras+" palabras";
      if(d.logro){const l=el("div","logro"); l.appendChild(el("span","st","⭐")); l.appendChild(el("span","",d.logro)); chat.appendChild(l);}
      const bt=tutorDice([["recast",d.recast],["",d.reaccion],["",d.tutor],["meta",d.segundos+" s · sin internet"]],true);
      const enIngles=(d.voz||[]).filter(p=>p.lang==="en-US"); controlesEscucha(bt,enIngles);
      reproduce(d.voz);
      paso=d.paso_siguiente; ayudaActual=d.ayuda_es; progreso();
      if(d.fin&&d.resumen){ resumenFinal(d.resumen); }
    }
  }catch(e){pens.remove(); tutorDice([["meta","Se perdió la conexión con el Chromebook."]]);}
  btn.disabled=false; inp.focus();});
// ---- Pregúntale al tutor ----
const pan=document.getElementById("preg"), pch=document.getElementById("pchat"), prel=document.getElementById("prel"), pt=document.getElementById("pt"), pbtn=document.getElementById("pb");
let pregPrevio=null, pregInit=false;
const SUG=["¿Qué eres?","¿Cómo funcionas?","¿Necesitas internet?","¿Quién te hizo?","¿Cómo me corriges?","¿Guardas mis datos?","¿Para qué sirves?"];
function relacionadas(lista){ prel.textContent=""; (lista||[]).slice(0,6).forEach(t=>{const b=el("button","sec",t); b.type="button"; b.onclick=()=>pregunta(t); prel.appendChild(b);}); }
function abrePreg(){ prepararAudio(); pregPrevio=document.activeElement; pan.classList.remove("oculto");
  if(!pregInit){ pregInit=true; pch.appendChild(el("div","b tutor","¡Hola! Pregúntame lo que quieras sobre cómo funciono, en español o en inglés. Toca una pregunta o escribe la tuya.")); relacionadas(SUG); }
  pt.focus(); }
function cierraPreg(){ pan.classList.add("oculto"); if(pregPrevio&&pregPrevio.focus)pregPrevio.focus(); }
async function pregunta(texto){ texto=(texto||"").trim(); if(!texto)return;
  pch.appendChild(el("div","b yo",texto)); const pens=el("div","b tutor escribe"); pens.appendChild(el("i"));pens.appendChild(el("i"));pens.appendChild(el("i")); pch.appendChild(pens); pch.scrollTop=pch.scrollHeight; pbtn.disabled=true;
  try{ const r=await fetch("/api/pregunta",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({texto})}); const d=await r.json(); pens.remove();
    if(!r.ok||d.error||typeof d.respuesta!=="string")throw new Error("x");
    pch.appendChild(el("div","b tutor",d.respuesta)); relacionadas(d.relacionadas);
  }catch(e){ pens.remove(); pch.appendChild(el("div","b tutor","No pude responder ahora. Prueba con otra pregunta o inténtalo de nuevo.")); relacionadas(SUG); }
  pch.scrollTop=pch.scrollHeight; pbtn.disabled=false; pt.focus(); }
document.getElementById("pregInicio").onclick=abrePreg; document.getElementById("pregSala").onclick=abrePreg;
document.getElementById("pcierra").onclick=cierraPreg;
pan.addEventListener("click",ev=>{ if(ev.target===pan)cierraPreg(); });
document.addEventListener("keydown",ev=>{ if(ev.key==="Escape"&&!pan.classList.contains("oculto"))cierraPreg(); });
document.getElementById("pf").addEventListener("submit",ev=>{ ev.preventDefault(); const t=pt.value; pt.value=""; pregunta(t); });
</script></body></html>"""


class Manejador(BaseHTTPRequestHandler):
    def _enviar(self, codigo, cuerpo, tipo="application/json; charset=utf-8"):
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        ruta = self.path.split("?", 1)[0]
        if ruta in ("/", "/index.html", "/practica"):
            self._enviar(200, PAGINA_PRACTICA, "text/html; charset=utf-8")
        elif ruta == "/corrector":
            self._enviar(200, PAGINA, "text/html; charset=utf-8")
        elif ruta.startswith("/audio/") and re.fullmatch(r"/audio/[0-9a-f]{12}\.wav", ruta):
            p = os.path.join(DIR_AUDIO, ruta.split("/")[-1])
            if not os.path.exists(p):
                return self._enviar(404, json.dumps({"error": "sin audio"}))
            datos = open(p, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(datos)))
            self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            self.wfile.write(datos)
        elif ruta == "/api/registro.csv":
            datos = registro_csv().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="registro_tutor_{time.strftime("%Y%m%d_%H%M")}.csv"')
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
        else:
            self._enviar(404, json.dumps({"error": "no existe"}))

    def do_POST(self):
        if self.path == "/api/rapido":
            try:
                n = int(self.headers.get("Content-Length", "0"))
                q = json.loads(self.rfile.read(n) or b"{}")
                texto = str(q.get("texto", "")).strip()[:400]
                r = rapido(texto)
                if _sesion_valida(q.get("sesion")):
                    _t_rapido[(q["sesion"], r["texto"])] = r["segundos"]
                return self._enviar(200, json.dumps(r, ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                return self._enviar(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))
        if self.path == "/api/pregunta":
            try:
                n = int(self.headers.get("Content-Length", "0"))
                q = json.loads(self.rfile.read(n) or b"{}")
                return self._enviar(200, json.dumps(FAQ_.responde(str(q.get("texto", ""))[:300]), ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                return self._enviar(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))
        if self.path == "/api/practica":
            q, texto, sesion = {}, "", "sin-sesion"
            try:
                n = int(self.headers.get("Content-Length", "0"))
                q = json.loads(self.rfile.read(n) or b"{}")
                texto = str(q.get("texto", "")).strip()[:400]
                sesion = q.get("sesion") if _sesion_valida(q.get("sesion")) else "sin-sesion"
                esc = q.get("escenario") if q.get("escenario") in ESCENARIOS else "tienda"
                if not texto:
                    return self._enviar(400, json.dumps({"error": "frase vacía"}))
                out = practica(sesion, esc, q.get("paso", 0), texto)
                registra(sesion, "practica:" + esc, esc, texto, out)
                return self._enviar(200, json.dumps(out, ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                registra(sesion, "practica", "", texto, None, f"{type(e).__name__}: {e}"[:300])
                return self._enviar(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))
        if self.path == "/api/escenarios":
            return self._enviar(200, json.dumps([{k: e[k] for k in ("id", "titulo", "meta_es")} | {
                "inicio": e["pasos"][0]["tutor"], "inicio_audio": aid(e["pasos"][0]["tutor"]),
                "ayuda_es": e["pasos"][0]["ayuda_es"], "n_pasos": len(e["pasos"]),
                "vocabulario": e.get("vocabulario", []), "meta_final_es": e.get("meta_final_es", "")}
                for e in ESCENARIOS.values()], ensure_ascii=False))
        if self.path != "/api/turno":
            return self._enviar(404, json.dumps({"error": "no existe"}))
        q, texto, sesion, ambito, tipo = {}, "", "sin-sesion", "agricola", "texto"
        try:
            n = int(self.headers.get("Content-Length", "0"))
            q = json.loads(self.rfile.read(n) or b"{}")
            texto = str(q.get("texto", "")).strip()[:400]
            sesion = q.get("sesion") if _sesion_valida(q.get("sesion")) else "sin-sesion"
            ambito = q.get("ambito", "agricola") if q.get("ambito") in ("agricola", "tecnico") else "agricola"
            tipo = q.get("tipo_entrada", "texto") if q.get("tipo_entrada") in ("texto", "voz") else "texto"
            if not texto:
                return self._enviar(400, json.dumps({"error": "frase vacía"}))
            out = turno(texto, ambito)
            registra(sesion, tipo, ambito, texto, out)
            self._enviar(200, json.dumps(out, ensure_ascii=False))
        except Exception as e:  # noqa: BLE001
            registra(sesion, tipo, ambito, texto, None, f"{type(e).__name__}: {e}"[:300])
            self._enviar(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def log_message(self, *a):
        pass


def main():
    global TT
    ap = argparse.ArgumentParser()
    ap.add_argument("--tutor", required=True)
    ap.add_argument("--puerto", type=int, default=8080)
    ap.add_argument("--host", default="0.0.0.0")
    a = ap.parse_args()
    sys.path.insert(0, a.tutor)
    import tutor.tutor as T
    TT = T
    print("calentando (la primera consulta es lenta)...", flush=True)
    t0 = time.perf_counter()
    turno("My brother have 20 years and he work in the farm.", "agricola")
    print(f"listo en {time.perf_counter() - t0:.0f} s. Abre http://<ip>:{a.puerto}/", flush=True)
    ThreadingHTTPServer((a.host, a.puerto), Manejador).serve_forever()


if __name__ == "__main__":
    main()
