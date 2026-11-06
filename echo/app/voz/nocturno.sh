#!/bin/bash
# Trabajo nocturno en el servidor (lo pidió Christiam el 6-nov al apagar los PC). Todo sobrevive al cierre de SSH.
# 1) voces de las frases nuevas  2) investigación de palabras santandereanas  3) módulos nuevos con la API
#    4) voces de los módulos nuevos. Log: ~/tutor_voz/nocturno.log
cd ~/tutor_voz || exit 1
{
echo "== $(date) voces (frases actuales)"
nice -n 10 .venv/bin/python -B genera_audio.py frases.json audio 2>&1 | grep -E 'audios:|sin audio'
echo "== $(date) investigación Santander"
cd ~/tutor_bucle/investigacion && ../.venv/bin/python -B investiga_api.py --contexto contexto_investigacion.md \
  --encargo encargo_santander.md --modelo claude-sonnet-5-5 --max-turnos 10 --salida SANTANDER_palabras.md 2>&1 | tail -3
echo "== $(date) módulos nuevos"
cd ~/tutor_voz && ~/tutor_bucle/.venv/bin/python -B genera_modulos_api.py --base modulos.json \
  --santander ~/tutor_bucle/investigacion/SANTANDER_palabras.md --salida modulos_nuevos.json 2>&1 | tail -12
echo "== $(date) voces de los módulos nuevos"
.venv/bin/python -B frases_desde_modulos.py modulos_nuevos.json frases_nuevas.json
nice -n 10 .venv/bin/python -B genera_audio.py frases_nuevas.json audio 2>&1 | grep -E 'audios:|sin audio'
tar czf /tmp/audio_tutor.tgz audio
echo "== $(date) listo"
} >> ~/tutor_voz/nocturno.log 2>&1
