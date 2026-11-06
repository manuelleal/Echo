"""Pregraba las frases fijas del tutor con Kokoro-82M (Apache-2.0) en el servidor.

    python genera_audio.py frases.json salida/      -> salida/<id>.wav (24 kHz mono) + salida/manifiesto.json
Voces: inglés af_heart (lang a, inglés americano); español ef_dora (lang e).
"""
import json
import os
import sys
import time

import numpy as np
import soundfile as sf
from kokoro import KPipeline


def main():
    frases = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    tuberias = {"en": (KPipeline(lang_code="a"), "af_heart", 0.9), "es": (KPipeline(lang_code="e"), "ef_dora", 1.0)}
    hechos = {}
    t0 = time.time()
    for f in frases:
        ruta = os.path.join(out, f["id"] + ".wav")
        if not os.path.exists(ruta):
            pipe, voz, vel = tuberias[f["idioma"]]
            trozos = [a for _, _, a in pipe(f["texto"], voice=voz, speed=vel)]
            if not trozos:
                print("sin audio:", f["id"], flush=True)
                continue
            sf.write(ruta, np.concatenate([np.asarray(t) for t in trozos]), 24000)
        hechos[f["id"]] = f["texto"]
    json.dump(hechos, open(os.path.join(out, "manifiesto.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"audios: {len(hechos)}/{len(frases)} en {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
