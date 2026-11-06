#!/bin/bash
# (root) Deshace el quiosco: vuelve al arranque en modo texto, GRUB visible y sin servicios del tutor.
systemctl disable --now tutor-quiosco.service tutor-backend.service 2>/dev/null
[ -f /etc/default/grub.antes_quiosco ] && cp /etc/default/grub.antes_quiosco /etc/default/grub && update-grub
plymouth-set-default-theme -R bgrt 2>/dev/null || true
systemctl set-default multi-user.target
echo "quiosco desactivado (el usuario tutor queda bloqueado; borrarlo con: userdel -r tutor)"
