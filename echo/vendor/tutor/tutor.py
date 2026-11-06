"""Tutor de inglés local: corrige la frase del aprendiz y hace UNA pregunta corta.

Interfaz estable (otro agente evalúa contra ella; no cambiar):
    responder(texto_aprendiz: str, contexto: dict) -> dict con EXACTAMENTE
    {"errores": [{"original", "corregido", "tipo"}], "frase_corregida": str,
     "pregunta_siguiente": str, "latencia_s": float, "tokens": int}

Diseño (dos pasos, el primero con dos llamadas):
  (a) EXTRACCIÓN, temperatura 0, JSON forzado por esquema (gramática de llama-server) y reintento si
      el JSON no parsea:
      a1. el modelo REESCRIBE la frase con cambios mínimos -> {"frase_corregida"};
      a2. el código calcula, palabra a palabra, qué cambió (original -> corregido) y el modelo sólo
          clasifica cada cambio con un tipo de una lista cerrada -> {"tipos": [...]}.
      Así cada error listado es un cambio real de la corrección (no se inventan errores que la
      corrección no hace) y "sin errores" sólo ocurre si la lista quedó vacía.
  (b) CONVERSACIÓN: una pregunta corta (A1–A2) ligada a lo que dijo y al ámbito vocacional.

Si la extracción falla del todo: errores == [] y frase_corregida == "" (la interfaz NO debe decir
"sin errores" en ese caso; ver `responder_detallado()["estado"]`).

`contexto` (todas las claves opcionales): {"ambito": "agricola"|"tecnico", "nivel": "A1"|"A2",
"historial": [{"aprendiz": str, "pregunta": str}, ...], "version": "v1"|"v2"}.
"version" (por defecto "v1") sólo cambia los ejemplos del paso a1 (ver pruebas/PREREGISTRO_v2.md).
Si no hay servidor en 127.0.0.1:8097, `responder` lanza uno (4 hilos) y lo detiene al salir de Python.
"""
import atexit
import difflib
import hashlib
import json
import os
import re
import time
import urllib.request

from . import servidor as _srv

URL = os.environ.get("TUTOR_URL", _srv.URL)
MAX_CHARS = 600  # textos más largos se recortan (declarado en README)

TIPOS = [
    "tiempo_verbal", "concordancia_sujeto_verbo", "sujeto_omitido", "forma_verbal",
    "negacion", "preposicion", "articulo", "vocabulario", "orden_palabras",
    "ortografia", "otro",
]

# ---------------------------------------------------------------- prompts (a1)
SISTEMA_CORRIGE = """You correct English sentences written by Spanish-speaking students (level A1-A2).
Rules:
- Make the MINIMUM changes needed to make the text grammatically correct.
- Keep the student's words, word order and meaning. Do not rephrase. Do not add new ideas.
- If the text is already correct, return it exactly unchanged.
- Check every verb and every clause: verb tense with time words (yesterday, last week, ago = past
  tense for all the actions); he/she/it + verb-s; every clause needs a subject (It is ...);
  no double negatives; subject-verb agreement; prepositions; articles.
Answer only with JSON: {"frase_corregida": "<corrected text>"}"""

EJEMPLOS_CORRIGE = [
    ("Last year my father plant corn and he sell it in the town.",
     "Last year my father planted corn and he sold it in the town."),
    ("I like to work with animals.", "I like to work with animals."),
    ("Is important to give water to the cows every day.",
     "It is important to give water to the cows every day."),
    ("My sister work in the bakery every day.", "My sister works in the bakery every day."),
]

ESQ_CORRIGE = {
    "type": "object",
    "properties": {"frase_corregida": {"type": "string", "minLength": 1}},
    "required": ["frase_corregida"],
}

# ---------------------------------------------------------------- prompts (a2)
SISTEMA_TIPOS = """You label grammar corrections made to a Spanish-speaking student's English sentence.
For each numbered change "original -> corrected", choose exactly one type from this list:
tiempo_verbal (wrong verb tense), concordancia_sujeto_verbo (subject-verb agreement, e.g. he work -> he works),
sujeto_omitido (missing subject, e.g. is hot -> it is hot), forma_verbal (wrong verb form or pattern),
negacion (negation, double negative), preposicion, articulo, vocabulario (wrong word),
orden_palabras (word order), ortografia (spelling), otro.
Answer only with JSON: {"tipos": ["<type of change 1>", "<type of change 2>", ...]}"""

# ---------------------------------------------------------------- prompts (b)
AMBITOS = {
    "agricola": "farm work: animals, crops, tools, weather, the market",
    "tecnico": "technical work: machines, tools, repairs, safety, the workshop",
}
SISTEMA_PREGUNTA = """You are a friendly English teacher in a rural technical school. Your students are
teenagers and young adults, level {nivel}. Their field: {ambito}.
Write ONE short question (maximum 12 words) in very simple English that continues the conversation
about what the student just said, connected to their field. Do not correct the student. Do not explain.
Answer only with the question."""

VERSION_PROMPTS = hashlib.sha1(
    json.dumps([SISTEMA_CORRIGE, EJEMPLOS_CORRIGE, SISTEMA_TIPOS, SISTEMA_PREGUNTA, AMBITOS, "reglas-tipo-v1", "sin-fusion-r2"]).encode()
).hexdigest()[:10]

# ---------------------------------------------------------------- v2 (pruebas/PREREGISTRO_v2.md)
# Sólo cambia el paso a1: a los 4 ejemplos de v1 se suman 16 pares escritos SIN mirar el banco de
# evaluación: edad con "have", falsos cognados de hispanohablantes, orden de adjetivo, y 4 frases
# correctas (con las mismas palabras bien usadas) que NO se tocan.
# Ronda 1 de ajuste (humo_v2 ronda 0: "Actually I work in the kitchen..." quedó sin corregir): una
# línea de regla sobre edad y falsos amigos, permitida por el preregistro. Va antes de la línea final.
_REGLA_V2 = ("- Spanish speakers' errors: age uses \"be\" (I am 20 years old, not I have 20 years); false "
             "friends: actualmente = currently (\"Actually I work...\" -> \"Currently I work...\"), "
             "asistir = attend, embarazada = pregnant, carrera = degree, librería = bookstore, "
             "constipado = have a cold, sensible = sensitive, realizar = do / carry out. "
             "Change a word only when it is clearly wrong.\n")
_FIN = "Answer only with JSON:"
SISTEMA_CORRIGE_V2 = SISTEMA_CORRIGE.replace(_FIN, _REGLA_V2 + _FIN, 1)

EJEMPLOS_V2 = [
    ("I have 19 years and I study mechanics.", "I am 19 years old and I study mechanics."),
    ("How many years have your father?", "How old is your father?"),
    ("Actually I work in a bakery in the town.", "Currently I work in a bakery in the town."),
    ("Every Friday I assist to the computer class.", "Every Friday I attend the computer class."),
    ("Actually, the engine is fine; the problem is the battery.",
     "Actually, the engine is fine; the problem is the battery."),
    ("The cow is embarrassed, she will have a calf in March.",
     "The cow is pregnant, she will have a calf in March."),
    ("I want to finish my career in agronomy.", "I want to finish my degree in agronomy."),
    ("We bought a tractor red for the farm.", "We bought a red tractor for the farm."),
    ("I buy notebooks and pencils in the library.", "I buy notebooks and pencils in the bookstore."),
    ("I realized that the chickens had no water.", "I realized that the chickens had no water."),
    ("I am constipated and I cannot cook in the restaurant today.",
     "I have a cold and I cannot cook in the restaurant today."),
    ("The new calves are very sensible to the cold.", "The new calves are very sensitive to the cold."),
    ("Yesterday we realized the vaccination of the cattle.",
     "Yesterday we carried out the vaccination of the cattle."),
    # ronda 2: "Actually I work..." seguía sin corregir con la regla de la ronda 1; este par reemplaza al
    # control "The school library has manuals about computers and networks." (quedan 3 controles).
    ("Actually we have 40 cows on the farm, but before we had 20.",
     "Currently we have 40 cows on the farm, but before we had 20."),
    ("We have a white big horse.", "We have a big white horse."),
    ("My grandfather is 70 years old and he still milks the cows.",
     "My grandfather is 70 years old and he still milks the cows."),
]

VERSION_PROMPTS_V2 = hashlib.sha1(
    json.dumps([SISTEMA_CORRIGE_V2, EJEMPLOS_CORRIGE + EJEMPLOS_V2, SISTEMA_TIPOS, SISTEMA_PREGUNTA, AMBITOS,
                "reglas-tipo-v1", "sin-fusion-r2", "v2-r2"]).encode()
).hexdigest()[:10]

# versión -> (prompt de sistema de a1, ejemplos de a1, huella de los prompts)
VERSIONES = {
    "v1": (SISTEMA_CORRIGE, EJEMPLOS_CORRIGE, VERSION_PROMPTS),
    "v2": (SISTEMA_CORRIGE_V2, EJEMPLOS_CORRIGE + EJEMPLOS_V2, VERSION_PROMPTS_V2),
}


def _version(contexto):
    v = contexto.get("version", "v1")
    if v not in VERSIONES:
        raise ValueError(f"versión desconocida: {v!r} (válidas: {sorted(VERSIONES)})")
    return v

_servidor_propio = None


def _asegurar_servidor():
    global _servidor_propio
    if _srv.salud(URL):
        return
    if _servidor_propio is None:
        _servidor_propio = _srv.Servidor(hilos=int(os.environ.get("TUTOR_HILOS", "4"))).iniciar()
        atexit.register(_servidor_propio.detener)


def _chat(mensajes, max_tokens, temperatura=0.0, esquema=None, semilla=42):
    cuerpo = {"messages": mensajes, "temperature": temperatura, "max_tokens": max_tokens,
              "seed": semilla, "cache_prompt": True}
    if esquema is not None:
        cuerpo["response_format"] = {"type": "json_schema",
                                     "json_schema": {"name": "salida", "schema": esquema}}
    req = urllib.request.Request(URL + "/v1/chat/completions", data=json.dumps(cuerpo).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    texto = resp["choices"][0]["message"]["content"] or ""
    t = resp.get("timings", {})
    uso = {"tokens": int(resp.get("usage", {}).get("completion_tokens", 0)),
           "tokens_prompt": int(resp.get("usage", {}).get("prompt_tokens", 0)),
           "gen_ms": float(t.get("predicted_ms", 0.0)), "prompt_ms": float(t.get("prompt_ms", 0.0)),
           "prompt_n": int(t.get("prompt_n", 0))}  # prompt_n: tokens leídos de verdad (sin los de caché)
    return texto, uso


def _chat_json(mensajes, max_tokens, esquema, clave, acum, intentos=3):
    """Temperatura 0 + esquema; si el JSON no parsea o falta la clave, reintenta con más tokens."""
    for k in range(intentos):
        texto, uso = _chat(mensajes, max_tokens * (2 ** k), 0.0, esquema)
        for c in uso:
            acum[c] += uso[c]
        acum["llamadas"] += 1
        try:
            obj = json.loads(texto)
            if isinstance(obj, dict) and clave in obj:
                return obj
        except json.JSONDecodeError:
            pass
        acum["reintentos"] += 1
    return None


# ---------------------------------------------------------------- diferencia palabra a palabra
_PUNT = ".,;:!?\"()[]"


def _clave(tok):
    return tok.lower().strip(_PUNT).replace("’", "'")


def _tokens(s):
    return [t for t in s.split() if _clave(t)]


def _limpia(toks):
    return " ".join(toks).strip(_PUNT + " ")


def cambios(original: str, corregida: str):
    """Lista de (original, corregido) por cada tramo que cambió (ignora mayúsculas y puntuación).
    Inserciones y borrados llevan una palabra vecina para que se lean ("feed to" -> "feed")."""
    a, b = _tokens(original), _tokens(corregida)
    ka, kb = [_clave(t) for t in a], [_clave(t) for t in b]
    ops = [o for o in difflib.SequenceMatcher(None, ka, kb, autojunk=False).get_opcodes() if o[0] != "equal"]
    # ronda 2: ya NO se fusionan tramos separados por una palabra igual (en la reserva "come and give" salió
    # como UN error cuando eran dos). Sólo se juntan tramos contiguos (difflib ya los junta).
    fus = []
    for o in ops:
        if fus and o[1] - fus[-1][2] <= 0 and o[3] - fus[-1][4] <= 0:
            p = fus[-1]
            fus[-1] = ("replace", p[1], o[2], p[3], o[4])
        else:
            fus.append(o)
    salida = []
    for tag, i1, i2, j1, j2 in fus:
        if i1 == i2 or j1 == j2:  # inserción o borrado puro: añadir vecino
            if i1 > 0 and j1 > 0:
                i1, j1 = i1 - 1, j1 - 1
            elif i2 < len(a) and j2 < len(b):
                i2, j2 = i2 + 1, j2 + 1
        o, c = _limpia(a[i1:i2]), _limpia(b[j1:j2])
        if o.lower() != c.lower():
            salida.append((o, c))
    return salida


def _similitud(x, y):
    return difflib.SequenceMatcher(None, [_clave(t) for t in _tokens(x)],
                                   [_clave(t) for t in _tokens(y)], autojunk=False).ratio()


# ---------------------------------------------------------------- pasos
def _corregir(texto, acum, version="v1"):
    sistema, ejemplos, _ = VERSIONES[version]
    mensajes = [{"role": "system", "content": sistema}]
    for o, c in ejemplos:
        mensajes.append({"role": "user", "content": o})
        mensajes.append({"role": "assistant", "content": json.dumps({"frase_corregida": c})})
    mensajes.append({"role": "user", "content": texto})
    tope = min(512, 40 + 2 * len(texto.split()) * 2)
    obj = _chat_json(mensajes, tope, ESQ_CORRIGE, "frase_corregida", acum)
    if obj is None:
        return None
    return str(obj["frase_corregida"]).strip()


# ---------------------------------------------------------------- tipo por reglas (ronda 1)
# En la ronda 0 el modelo puso "negacion" a 6 de 12 cambios que no lo eran: el tipo lo deciden primero
# reglas lingüísticas generales; el modelo sólo clasifica lo que las reglas no reconocen.
_PREP = {"in", "on", "at", "to", "for", "of", "from", "with", "by", "about", "into", "until", "during"}
_ART = {"a", "an", "the"}
_SUJ = {"it", "i", "he", "she", "we", "they", "there", "you"}
_NEG = {("nothing", "anything"), ("nobody", "anybody"), ("never", "ever"), ("no", "any"),
        ("none", "any"), ("nowhere", "anywhere"), ("no", "not")}
_AGR = {("have", "has"), ("do", "does"), ("don't", "doesn't"), ("is", "are"), ("was", "were"),
        ("am", "is"), ("am", "are")}
_IRREG = {"go": "went", "come": "came", "give": "gave", "have": "had", "has": "had", "is": "was",
          "are": "were", "am": "was", "do": "did", "make": "made", "take": "took", "see": "saw",
          "eat": "ate", "buy": "bought", "sell": "sold", "feed": "fed", "get": "got", "run": "ran",
          "bring": "brought", "say": "said", "tell": "told", "think": "thought", "write": "wrote",
          "drive": "drove", "grow": "grew", "catch": "caught", "find": "found", "leave": "left",
          "put": "put", "cut": "cut", "sleep": "slept", "fall": "fell", "know": "knew", "begin": "began",
          "drink": "drank", "ride": "rode", "teach": "taught", "build": "built", "send": "sent",
          "spend": "spent", "meet": "met", "lose": "lost", "pay": "paid", "keep": "kept", "feel": "felt",
          "can": "could", "will": "would", "don't": "didn't", "doesn't": "didn't"}


def _es_pasado(o, c):
    return _IRREG.get(o) == c or c in (o + "ed", o + "d") or (o.endswith("y") and c == o[:-1] + "ied")


def _tipo_regla(o, c):
    ko, kc = [_clave(t) for t in o.split()], [_clave(t) for t in c.split()]
    so, sc = set(ko), set(kc)
    ins, bor = [t for t in kc if t not in so], [t for t in ko if t not in sc]
    if ins and not bor and all(t in _SUJ for t in ins):
        return "sujeto_omitido"
    if ins and not bor and all(t in _ART for t in ins) or bor and not ins and all(t in _ART for t in bor):
        return "articulo"
    if len(ins) == 1 and len(bor) == 1:
        x, y = bor[0], ins[0]
        if x in _ART and y in _ART:
            return "articulo"
        if (x, y) in _NEG:
            return "negacion"
        if (x, y) in _AGR or (y, x) in _AGR or y in (x + "s", x + "es") or x in (y + "s", y + "es"):
            return "concordancia_sujeto_verbo"
        if _es_pasado(x, y):
            return "tiempo_verbal"
        if x in _PREP and y in _PREP:
            return "preposicion"
    if (ins and not bor and all(t in _PREP for t in ins)) or (bor and not ins and all(t in _PREP for t in bor)):
        return "preposicion"
    # progresivo -> pasado simple ("am cleaning" -> "cleaned")
    if len(ko) == 2 and ko[0] in ("am", "is", "are") and ko[1].endswith("ing") and len(kc) == 1 \
            and (kc[0].endswith("ed") or kc[0] in _IRREG.values()):
        return "tiempo_verbal"
    return None


def _clasificar(texto, corregida, lista, acum):
    tipos = [_tipo_regla(o, c) for o, c in lista]
    resto = [i for i, t in enumerate(tipos) if t is None]
    if resto:
        modelo = _clasificar_modelo(texto, corregida, [lista[i] for i in resto], acum)
        for i, t in zip(resto, modelo):
            tipos[i] = t
    return tipos


def _clasificar_modelo(texto, corregida, lista, acum):
    n = len(lista)
    esquema = {"type": "object", "properties": {"tipos": {
        "type": "array", "items": {"type": "string", "enum": TIPOS}, "minItems": n, "maxItems": n}},
        "required": ["tipos"]}
    cuerpo = (f"Student: {texto}\nCorrected: {corregida}\nChanges:\n"
              + "\n".join(f"{i + 1}. \"{o}\" -> \"{c}\"" for i, (o, c) in enumerate(lista)))
    obj = _chat_json([{"role": "system", "content": SISTEMA_TIPOS}, {"role": "user", "content": cuerpo}],
                     20 + 12 * n, esquema, "tipos", acum)
    tipos = list(obj["tipos"]) if obj and isinstance(obj.get("tipos"), list) else []
    tipos = [t if t in TIPOS else "otro" for t in tipos][:n]
    return tipos + ["otro"] * (n - len(tipos))


def _pregunta(corregida, contexto, acum):
    ambito = contexto.get("ambito", "agricola")
    nivel = contexto.get("nivel", "A1-A2")
    sistema = SISTEMA_PREGUNTA.format(nivel=nivel, ambito=AMBITOS.get(ambito, AMBITOS["agricola"]))
    mensajes = [{"role": "system", "content": sistema}]
    for h in (contexto.get("historial") or [])[-2:]:
        # turno previo: el aprendiz dijo X, el tutor preguntó Y; ahora el aprendiz responde
        if isinstance(h, dict) and h.get("pregunta") and h.get("aprendiz"):
            mensajes.append({"role": "user", "content": str(h["aprendiz"])})
            mensajes.append({"role": "assistant", "content": str(h["pregunta"])})
    mensajes.append({"role": "user", "content": corregida})
    texto, uso = _chat(mensajes, 40, temperatura=0.3)
    for c in uso:
        acum[c] += uso[c]
    acum["llamadas"] += 1
    texto = " ".join(texto.replace("\n", " ").split()).strip().strip('"')
    m = re.search(r"[^?]*\?", texto)
    p = m.group(0).strip() if m else ""
    if not p or len(p.split()) > 20:
        p = "What do you do on the farm every day?" if ambito != "tecnico" else "What tools do you use at work?"
        acum["pregunta_respaldo"] = True
    return p


def responder_detallado(texto_aprendiz: str, contexto: dict | None = None) -> dict:
    """Como `responder`, más diagnóstico: estado, tokens_prompt, llamadas, reintentos, tiempos."""
    t0 = time.perf_counter()
    contexto = contexto if isinstance(contexto, dict) else {}
    version = _version(contexto)
    texto = " ".join(str(texto_aprendiz or "").split())[:MAX_CHARS]
    acum = {"tokens": 0, "tokens_prompt": 0, "gen_ms": 0.0, "prompt_ms": 0.0, "prompt_n": 0,
            "llamadas": 0, "reintentos": 0, "pregunta_respaldo": False}
    if not texto:
        return {"errores": [], "frase_corregida": "", "pregunta_siguiente": "Can you write a sentence in English?",
                "latencia_s": round(time.perf_counter() - t0, 3), "tokens": 0, "estado": "vacio", **acum}
    _asegurar_servidor()
    estado = "ok"
    corregida = _corregir(texto, acum, version)
    if corregida is not None and _similitud(texto, corregida) < 0.5:
        # reescritura demasiado libre (o respondió en vez de corregir): reintento con aviso
        acum["reintentos"] += 1
        otra = _corregir(texto + "\n(Correct this text with minimal changes. Do not answer it.)", acum, version)
        if otra is not None and _similitud(texto, otra) > _similitud(texto, corregida):
            corregida = otra
        if _similitud(texto, corregida) < 0.5:
            estado = "reescritura_libre"
    errores = []
    if corregida is None:
        estado, corregida = "fallo_extraccion", ""
    else:
        lista = cambios(texto, corregida)
        if lista:
            tipos = _clasificar(texto, corregida, lista, acum)
            errores = [{"original": o, "corregido": c, "tipo": t} for (o, c), t in zip(lista, tipos)]
    pregunta = _pregunta(corregida or texto, contexto, acum)
    return {"errores": errores, "frase_corregida": corregida, "pregunta_siguiente": pregunta,
            "latencia_s": round(time.perf_counter() - t0, 3), "tokens": int(acum["tokens"]),
            "estado": estado, **{k: v for k, v in acum.items() if k != "tokens"},
            "version_prompts": VERSIONES[version][2], "version": version}


CLAVES = ("errores", "frase_corregida", "pregunta_siguiente", "latencia_s", "tokens")


def responder(texto_aprendiz: str, contexto: dict) -> dict:
    """Interfaz estable: devuelve sólo las cinco claves del contrato."""
    d = responder_detallado(texto_aprendiz, contexto)
    return {k: d[k] for k in CLAVES}
