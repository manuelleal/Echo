#!/bin/bash
# Arranca la demo en el Chromebook: llama-server (config H06) + tutor con reglas + ERG + página en el puerto 8080.
# Uso: bash ~/f2/biblioteca/demo/arranca_demo.sh      Detener: bash ~/f2/biblioteca/demo/arranca_demo.sh parar
if [ "$1" = "parar" ]; then
  pkill -f 'demo.py --tutor'; pkill -f 'llama-server.*--port 8097'; echo "detenido"; exit 0
fi
bash ~/f2/arranca_servidor_candy.sh > /dev/null 2>&1
cd ~/f2/biblioteca/demo || exit 1
pkill -f 'demo.py --tutor'
ERG_DIR=~/f2 setsid nohup python3 -B demo.py --tutor ~/f2/tutor_pkg --puerto 8080 > ~/f2/demo.log 2>&1 < /dev/null &
for i in $(seq 1 120); do grep -q 'listo en' ~/f2/demo.log && break; sleep 1; done
tail -2 ~/f2/demo.log
echo "En este Chromebook: http://127.0.0.1:8080/   ·   Desde otro aparato en la misma WiFi: http://$(hostname -I | awk '{print $1}'):8080/"
