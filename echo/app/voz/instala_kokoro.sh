#!/bin/bash
# Entorno aparte en el servidor para pregrabar la voz del tutor con Kokoro-82M (Apache-2.0). Torch sólo CPU.
set -e
sudo -n apt-get install -y -q espeak-ng > /tmp/apt_espeak.log 2>&1 || echo "no se pudo instalar espeak-ng"
mkdir -p ~/tutor_voz && cd ~/tutor_voz
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -q "kokoro>=0.9.4" soundfile
.venv/bin/python -c "import kokoro, torch; print('kokoro', kokoro.__version__ if hasattr(kokoro,'__version__') else 'ok', 'torch', torch.__version__)"
which espeak-ng
