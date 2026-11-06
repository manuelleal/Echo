"""Frases fijas (para pregrabar) de un archivo de módulos: líneas del tutor y sus variantes de ayuda."""
import hashlib
import json
import re
import sys


def clave(t):
    return hashlib.sha1(t.strip().encode("utf-8")).hexdigest()[:12]


en = set()
for m in json.load(open(sys.argv[1], encoding="utf-8")):
    for p in m["pasos"]:
        q = p["tutor"]
        en.update([q, "Can you tell me a little more? " + q, "So, " + q[0].lower() + q[1:]])
        ops = p.get("opciones") or []
        if len(ops) > 1:
            en.add(f"For example: \"{ops[0]}\" or \"{ops[1]}\"")
        if ops:
            en.add(f"Let me help you. You can say: \"{ops[0]}\"")
        ej = re.search(r"Ej\.?:\s*(.+)$", p.get("ayuda_es", ""))
        if ej:
            en.add(f"Let me help you. You can say: \"{ej.group(1).strip()}\"")
json.dump([{"id": clave(t), "texto": t, "idioma": "en"} for t in sorted(en)], open(sys.argv[2], "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("frases:", len(en))
