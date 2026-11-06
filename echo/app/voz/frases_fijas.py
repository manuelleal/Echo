"""Reúne todas las frases FIJAS que dice el tutor, para pregrabarlas: líneas de escenarios, reacciones de plantilla,
pistas de las fichas y ánimos. Escribe frases.json = [{"id": sha1[:12], "texto": ..., "idioma": "en"|"es"}]."""
import glob
import hashlib
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.dirname(AQUI)
BIB = os.path.join(os.path.dirname(DEMO), "core")  # Echo: core/ reemplaza a biblioteca/


def clave(texto):
    return hashlib.sha1(texto.strip().encode("utf-8")).hexdigest()[:12]


def main():
    en, es = set(), set()
    escs = json.load(open(os.path.join(DEMO, "escenarios.json"), encoding="utf-8"))
    gr_path = os.path.join(DEMO, "garcia_rovira.json")
    animos = []
    if os.path.exists(gr_path):
        gr = json.load(open(gr_path, encoding="utf-8"))
        escs += gr.get("ideas_escenarios", [])
        animos = [a for a in gr.get("animos_es", []) if not re.search(r"sumerc|\bmana\b|nonos|taitas", a, re.I)]
    mod_path = os.path.join(DEMO, "modulos.json")
    if os.path.exists(mod_path):
        escs += json.load(open(mod_path, encoding="utf-8"))
    for e in escs:
        for p in e["pasos"]:
            q = p["tutor"]
            en.add(q)
            en.add("Can you tell me a little more? " + q)
            en.add("So, " + q[0].lower() + q[1:])  # tras responder una pregunta del aprendiz
            ops = p.get("opciones") or []
            if len(ops) > 1:
                en.add(f"For example: \"{ops[0]}\" or \"{ops[1]}\"")
            if ops:
                en.add(f"Let me help you. You can say: \"{ops[0]}\"")
            ej = re.search(r"Ej\.?:\s*(.+)$", p.get("ayuda_es", ""))
            if ej:
                en.add(f"Let me help you. You can say: \"{ej.group(1).strip()}\"")
    en.update(["Nice!", "Great!", "I see.", "Interesting!", "Very good!", "Cool!", "Oh, nice!",
               "Can you say it like that?", "Great job! See you next time."])
    for f in glob.glob(os.path.join(BIB, "fichas", "*.json")):
        x = json.load(open(f, encoding="utf-8"))
        es.add(x["pista_es"])
    es.update(animos)
    es.update(["¡Muy bien!", "¡Terminaste!"])
    out = [{"id": clave(t), "texto": t, "idioma": "en"} for t in sorted(en)] + \
          [{"id": clave(t), "texto": t, "idioma": "es"} for t in sorted(es)]
    json.dump(out, open(os.path.join(AQUI, "frases.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"inglés: {len(en)}  español: {len(es)}  total: {len(out)}")


if __name__ == "__main__":
    main()
