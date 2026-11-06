#!/bin/bash
# (root, en candy) Acceso del servidor de casa al Chromebook, autorizado por Christiam el 6-nov-2026.
# - La llave del servidor sólo se acepta desde IP_DEL_SERVIDOR y entra como christiam (no como root).
# - christiam puede reiniciar SOLO el servicio del tutor sin contraseña (para instalar módulos y voces nuevos).
# Revertir: borrar la línea "servidor-casa->candy" de ~christiam/.ssh/authorized_keys y /etc/sudoers.d/tutor-restart
set -e
LLAVE="$1"
AK=/home/christiam/.ssh/authorized_keys
grep -q "servidor-casa->candy" "$AK" 2>/dev/null || echo "from=\"IP_DEL_SERVIDOR\" $LLAVE" >> "$AK"
chown christiam:christiam "$AK"; chmod 600 "$AK"
echo 'christiam ALL=(root) NOPASSWD: /usr/bin/systemctl restart tutor-backend, /usr/bin/systemctl restart tutor-backend.service' > /etc/sudoers.d/tutor-restart
chmod 440 /etc/sudoers.d/tutor-restart
visudo -c -f /etc/sudoers.d/tutor-restart
echo "acceso del servidor listo"
