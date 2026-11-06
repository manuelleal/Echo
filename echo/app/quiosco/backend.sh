#!/bin/bash
# Servicio del tutor (lo lanza systemd al encender): llama-server (config H06) + demo.py en el puerto 8080.
M=/home/christiam/llama/modelos/qwen05-q4_0-cabezaq4.gguf
/home/christiam/llama/bin/llama-server -m "$M" --host 127.0.0.1 --port 8097 -t 2 -c 2048 -np 1 \
  -ctk q8_0 -ctv q8_0 -fa on --no-webui > /home/christiam/f2/servidor.log 2>&1 &
LLAMA=$!
trap 'kill $LLAMA 2>/dev/null' EXIT
for i in $(seq 1 120); do
  python3 -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8097/health',timeout=2)" 2>/dev/null && break
  sleep 1
done
cd /home/christiam/f2/biblioteca/demo
export ERG_DIR=/home/christiam/f2
python3 -B demo.py --tutor /home/christiam/f2/tutor_pkg --puerto 8080 --host 0.0.0.0
