#!/bin/bash
# Lanza el bucle en el servidor de casa hasta el domingo 8-nov 23:59, tope 25 USD, una vuelta por hora, prioridad baja.
# Sobrevive al cierre de SSH (setsid + nohup). Para detenerlo: pkill -f 'bucle.py --tope-usd'
cd ~/tutor_bucle/biblioteca/entreno || exit 1
export ERG_DIR=~/tutor_bucle/ace
setsid nohup nice -n 19 ../../.venv/bin/python -B bucle.py --tope-usd 40 --por-llamada 40 --tipos-por-vuelta 3 \
  --pausa-min 30 --hasta 2026-11-15T23:59 >> ~/tutor_bucle/bucle.log 2>&1 < /dev/null &
sleep 3
pgrep -af 'bucle.py --tope-usd' | head -2
