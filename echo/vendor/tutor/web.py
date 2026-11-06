"""Página local mínima (sin dependencias ni recursos externos: funciona con el wifi apagado).

    python -m tutor.web [--puerto 8098] [--hilos 4]     -> abrir http://127.0.0.1:8098/

Rutas: GET /  (página) · POST /api/turno {"sesion","texto","ambito"} · GET /api/sesion/<id> (jsonl)
Sólo escucha en 127.0.0.1.
"""
import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import registro
from . import tutor as T
from .servidor import Servidor, salud, URL

_candado = threading.Lock()   # un solo turno a la vez (llama-server con -np 1)
_contextos = {}

PAGINA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tutor de inglés local</title>
<style>
 body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:760px;margin:1.5em auto;padding:0 1em;color:#222}
 h1{font-size:1.3em;margin-bottom:.2em} .sub{color:#666;font-size:.9em;margin-top:0}
 #chat{border:1px solid #ccc;border-radius:6px;padding:.8em;min-height:220px;max-height:55vh;overflow:auto;background:#fafafa}
 .yo{margin:.6em 0 .2em;font-weight:600} .tu{margin:.2em 0 .8em 1em}
 .err{margin:.1em 0 .1em 1em;font-size:.95em} del{color:#b00} ins{color:#070;text-decoration:none;font-weight:600}
 .tipo{color:#666;font-size:.85em} .ok{color:#070} .mal{color:#b60} .meta{color:#999;font-size:.8em}
 form{display:flex;gap:.5em;margin-top:.8em} #texto{flex:1;padding:.5em;font-size:1em}
 button{padding:.5em 1em;font-size:1em} #panel{margin-top:1em;font-size:.9em;color:#444}
 table{border-collapse:collapse} td{padding:.1em .6em;border-bottom:1px solid #eee}
</style></head><body>
<h1>Tutor de inglés (local, sin internet)</h1>
<p class="sub">Sesión <b id="ses"></b> · ámbito
 <select id="ambito"><option value="agricola">agrícola</option><option value="tecnico">técnico</option></select>
 · cada turno se registra para analítica (sin nombres).</p>
<div id="chat"><div class="tu">Tutor: Hello! Tell me about your work today.</div></div>
<form id="f"><input id="texto" autocomplete="off" placeholder="Write in English..." autofocus>
<button id="b">Enviar</button></form>
<div id="panel"></div>
<script>
const q = new URLSearchParams(location.search);
const sesion = q.get("sesion") || ("w-" + Math.random().toString(16).slice(2, 10));
document.getElementById("ses").textContent = sesion;
const chat = document.getElementById("chat"), conteo = {};
let turnos = 0;
function linea(cls, txt){const d=document.createElement("div");d.className=cls;d.textContent=txt;chat.appendChild(d);return d;}
function panel(){
  const p=document.getElementById("panel"); p.textContent="";
  const t=document.createElement("table");
  const h=document.createElement("tr"); h.innerHTML="<td><b>tipo de error (esta sesión)</b></td><td><b>n</b></td>"; t.appendChild(h);
  for (const [k,v] of Object.entries(conteo).sort((a,b)=>b[1]-a[1])){
    const r=document.createElement("tr"); const a=document.createElement("td"); a.textContent=k.replaceAll("_"," ");
    const b=document.createElement("td"); b.textContent=v; r.appendChild(a); r.appendChild(b); t.appendChild(r);}
  const s=document.createElement("p"); s.textContent="turnos: "+turnos+" · ";
  const a=document.createElement("a"); a.href="/api/sesion/"+sesion; a.textContent="descargar registro (.jsonl)"; s.appendChild(a);
  p.appendChild(s); p.appendChild(t);
}
document.getElementById("f").addEventListener("submit", async ev => {
  ev.preventDefault();
  const inp=document.getElementById("texto"), texto=inp.value.trim(); if(!texto) return;
  inp.value=""; document.getElementById("b").disabled=true;
  linea("yo", "Tú: "+texto); const espera=linea("meta","pensando...");
  try{
    const r = await fetch("/api/turno",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({sesion, texto, ambito:document.getElementById("ambito").value})});
    const d = await r.json(); espera.remove();
    if(d.error){ linea("mal","Error: "+d.error); }
    else{
      turnos++;
      if(!d.frase_corregida){ linea("mal","(no se pudo analizar la frase; no se afirma que esté bien)"); }
      else if(d.errores.length===0){ linea("ok","Sin errores detectados."); }
      else{
        linea("tu","Corrección: "+d.frase_corregida);
        for(const e of d.errores){
          conteo[e.tipo]=(conteo[e.tipo]||0)+1;
          const x=document.createElement("div"); x.className="err";
          const de=document.createElement("del"); de.textContent=e.original||"(nada)";
          const in_=document.createElement("ins"); in_.textContent=e.corregido||"(quitar)";
          const ti=document.createElement("span"); ti.className="tipo"; ti.textContent="  "+e.tipo.replaceAll("_"," ");
          x.appendChild(de); x.appendChild(document.createTextNode(" → ")); x.appendChild(in_); x.appendChild(ti);
          chat.appendChild(x);
        }
      }
      linea("tu","Tutor: "+d.pregunta_siguiente);
      linea("meta", d.latencia_s+" s · "+d.tokens+" tokens");
      panel();
    }
  }catch(e){ espera.remove(); linea("mal","Error de conexión con el servidor local"); }
  document.getElementById("b").disabled=false; chat.scrollTop=chat.scrollHeight; inp.focus();
});
panel();
</script></body></html>"""


class Manejador(BaseHTTPRequestHandler):
    def _enviar(self, codigo, cuerpo, tipo="application/json; charset=utf-8"):
        datos = cuerpo.encode("utf-8") if isinstance(cuerpo, str) else cuerpo
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            return self._enviar(200, PAGINA, "text/html; charset=utf-8")
        if self.path.startswith("/api/sesion/"):
            sesion = self.path.rsplit("/", 1)[-1]
            try:
                p = registro.ruta(sesion)
            except ValueError as e:
                return self._enviar(400, json.dumps({"error": str(e)}))
            datos = p.read_bytes() if p.exists() else b""
            return self._enviar(200, datos, "application/x-ndjson; charset=utf-8")
        self._enviar(404, json.dumps({"error": "no existe"}))

    def do_POST(self):
        if self.path != "/api/turno":
            return self._enviar(404, json.dumps({"error": "no existe"}))
        try:
            n = int(self.headers.get("Content-Length", "0"))
            pet = json.loads(self.rfile.read(min(n, 20000)).decode("utf-8"))
            sesion, texto = str(pet.get("sesion", "")), str(pet.get("texto", "")).strip()
            registro.ruta(sesion)
            ambito = pet.get("ambito") if pet.get("ambito") in T.AMBITOS else "agricola"
        except (ValueError, json.JSONDecodeError) as e:
            return self._enviar(400, json.dumps({"error": str(e)}))
        with _candado:
            ctx = _contextos.setdefault(sesion, {"ambito": ambito, "nivel": "A1-A2", "historial": []})
            ctx["ambito"] = ambito
            try:
                d = T.responder_detallado(texto, ctx)
            except Exception as e:  # el modelo local no responde
                return self._enviar(500, json.dumps({"error": f"modelo local: {e}"}))
            registro.anotar(sesion, texto, d, ctx, extra={"interfaz": "web"})
            ctx["historial"].append({"aprendiz": d["frase_corregida"] or texto, "pregunta": d["pregunta_siguiente"]})
        self._enviar(200, json.dumps({k: d[k] for k in T.CLAVES}, ensure_ascii=False))

    def log_message(self, *a):
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tutor de inglés local (web)")
    ap.add_argument("--puerto", type=int, default=8098)
    ap.add_argument("--hilos", type=int, default=4)
    a = ap.parse_args(argv)
    srv = None
    if not salud(URL):
        print("arrancando el modelo local...", flush=True)
        srv = Servidor(hilos=a.hilos).iniciar()
    http = ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador)
    print(f"Abre http://127.0.0.1:{a.puerto}/  (Ctrl+C para detener)", flush=True)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http.server_close()
        if srv:
            srv.detener()


if __name__ == "__main__":
    main()
