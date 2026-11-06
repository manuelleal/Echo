"""Agente revisor (servidor): espera a que termine nocturno.sh, revisa con Claude cada módulo nuevo y sólo instala en el
Chromebook los aprobados, con sus voces. Deja REVISION_modulos.md y INSTALACION.log en ~/tutor_voz.

Acceso al Chromebook: llave ~/.ssh/id_ed25519_candy (entra como christiam sólo desde esta IP; sudo sólo para reiniciar
tutor-backend). Nada se borra en el Chromebook: sólo se agregan modulos_extra.json y audios.
"""
import json
import os
import subprocess
import time
import urllib.request
from typing import List

import anthropic
from pydantic import BaseModel

D = os.path.expanduser("~/tutor_voz")
CANDY = ["ssh", "-o", "BatchMode=yes", "-i", os.path.expanduser("~/.ssh/id_ed25519_candy"), "christiam@IP_DEL_CHROMEBOOK"]
SCP = ["scp", "-q", "-o", "BatchMode=yes", "-i", os.path.expanduser("~/.ssh/id_ed25519_candy")]
DEMO = "/home/christiam/f2/biblioteca/demo"
LOG = os.path.join(D, "INSTALACION.log")


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M ") + m + "\n")


class Veredicto(BaseModel):
    id: str
    aprobado: bool
    razones: List[str]


class Revision(BaseModel):
    veredictos: List[Veredicto]


CRITERIOS = """Revisa estos módulos de práctica de inglés para aprendices adultos A1-A2 del SENA (Santander, Colombia).
Aprueba un módulo SÓLO si cumple todo:
1) las líneas del tutor están en inglés correcto y sencillo (A1-A2), con UNA sola pregunta;
2) la secuencia de pasos es lógica (una conversación real con principio y cierre);
3) ayuda_es está en español claro y su "Ej.:" es correcto;
4) nada ofensivo, estereotipado, vulgar ni inapropiado para un aula;
5) si usa expresiones santandereanas, son de las marcadas como apropiadas en la investigación y están bien usadas;
6) datos culturales plausibles (no inventa lugares ni hechos).
Sé estricto: ante la duda, rechaza y di por qué."""


def main():
    for _ in range(240):  # espera hasta 4 h a que termine el trabajo nocturno
        if os.path.exists(os.path.join(D, "nocturno.log")) and "== " in open(os.path.join(D, "nocturno.log")).read() and " listo" in open(os.path.join(D, "nocturno.log")).read().split("voces de los módulos nuevos")[-1]:
            break
        time.sleep(60)
    nuevos_p = os.path.join(D, "modulos_nuevos.json")
    if not os.path.exists(nuevos_p):
        return log("no hay modulos_nuevos.json: nada que instalar")
    nuevos = json.load(open(nuevos_p, encoding="utf-8"))
    sant_p = os.path.expanduser("~/tutor_bucle/investigacion/SANTANDER_palabras.md")
    sant = open(sant_p, encoding="utf-8").read()[:10000] if os.path.exists(sant_p) else "(sin investigación)"
    clave = os.environ.get("ANTHROPIC_API_KEY") or open(os.path.expanduser("~/.claves/anthropic.txt")).read().strip()
    client = anthropic.Anthropic(api_key=clave)
    r = client.beta.messages.parse(model="claude-sonnet-5-5", max_tokens=20000, system=CRITERIOS,
                                   messages=[{"role": "user", "content": f"Investigación santandereana:\n{sant}\n\n"
                                              f"Módulos:\n{json.dumps(nuevos, ensure_ascii=False)}"}],
                                   output_format=Revision, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    ver = {v.id: v for v in (r.parsed_output.veredictos if r.parsed_output else [])}
    aprobados = [m for m in nuevos if m["id"] in ver and ver[m["id"]].aprobado]
    with open(os.path.join(D, "REVISION_modulos.md"), "w", encoding="utf-8") as f:
        f.write(f"# Revisión de módulos nuevos ({time.strftime('%Y-%m-%d %H:%M')}, claude-sonnet-5-5)\n\n")
        for m in nuevos:
            v = ver.get(m["id"])
            f.write(f"- **{m['id']}** ({m['titulo']}): {'APROBADO' if v and v.aprobado else 'RECHAZADO'}"
                    f"{' — ' + '; '.join(v.razones) if v else ' — sin veredicto'}\n")
    log(f"revisados {len(nuevos)}, aprobados {len(aprobados)}: {[m['id'] for m in aprobados]}")
    if not aprobados:
        return
    extra = os.path.join(D, "modulos_extra.json")
    json.dump(aprobados, open(extra, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pasos = [
        SCP + [extra, f"christiam@IP_DEL_CHROMEBOOK:{DEMO}/modulos_extra.json"],
        SCP + ["/tmp/audio_tutor.tgz", f"christiam@IP_DEL_CHROMEBOOK:{DEMO}/audio_tutor.tgz"],
        CANDY + [f"cd {DEMO} && tar xzf audio_tutor.tgz && rm -f audio_tutor.tgz && sudo -n systemctl restart tutor-backend"],
    ]
    for p in pasos:
        res = subprocess.run(p, capture_output=True, text=True, timeout=600)
        if res.returncode != 0:
            return log(f"FALLO {p[-1][:80]}: {res.stderr[:200]}")
    for _ in range(40):  # comprobación: el tutor responde y lista los módulos nuevos
        try:
            req = urllib.request.Request("http://IP_DEL_CHROMEBOOK:8080/api/escenarios", data=b"{}", method="POST")
            ids = [e["id"] for e in json.load(urllib.request.urlopen(req, timeout=5))]
            log(f"instalado OK; el tutor ofrece {len(ids)} situaciones; nuevas presentes: "
                f"{[m['id'] for m in aprobados if m['id'] in ids]}")
            return
        except Exception:  # noqa: BLE001
            time.sleep(15)
    log("el tutor no respondió tras reiniciar: revisar a mano")


if __name__ == "__main__":
    main()
