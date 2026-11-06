#!/bin/bash
# Estado del bucle nocturno en el servidor (sin frases: sólo conteos y métricas).
D=~/tutor_bucle/biblioteca/entreno
echo "== proceso"; ps -eo pid,etime,args | grep '[b]ucle.py' || echo "NO corre"
echo "== datos"; echo "pares: $(wc -l < $D/datos/pares.jsonl)  correctas: $(wc -l < $D/datos/correctas.jsonl)"
echo "== gasto anotado (a tarifa Opus, el real es menor)"
~/tutor_bucle/.venv/bin/python -c "import json;print(round(sum(json.loads(l)['usd'] for l in open('$D/datos/gasto.jsonl')),2),'USD')"
echo "== vueltas"; wc -l < $D/registro.jsonl
echo "== métricas por vuelta"
~/tutor_bucle/.venv/bin/python - <<EOF
import json
for l in open("$D/registro.jsonl"):
    r = json.loads(l)
    v, b, s = r.get("validacion", {}), r.get("biblioteca", {}), r.get("sonda_estructura", {})
    print(r.get("vuelta"), "pares", r.get("n_pares"), "| valid det", v.get("det"), "falsas", v.get("falsas"),
          "| biblio det", b.get("det"), "falsas", b.get("falsas"), "| sonda det", s.get("det"), "falsas", s.get("falsas"),
          "|", r.get("tipos"))
EOF
echo "== errores"; grep -E 'error de API|Traceback|tope|límite|sin director' ~/tutor_bucle/bucle.log | tail -3
