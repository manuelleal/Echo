#!/bin/bash
# (root) Convierte el Chromebook en una máquina dedicada al tutor. Autorizado por Christiam el 5-nov-2026.
# Reversible con: bash revierte_quiosco_root.sh
set -e
Q=/home/christiam/f2/biblioteca/demo/quiosco
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -q cage plymouth plymouth-themes > /tmp/apt_quiosco.log 2>&1
apt-get install -y -q plymouth-label >> /tmp/apt_quiosco.log 2>&1 || true

# 1) usuario dedicado, sin contraseña utilizable y sin sudo
id tutor >/dev/null 2>&1 || useradd -m -s /bin/bash -c "Tutor de ingles (quiosco)" tutor
passwd -l tutor >/dev/null
usermod -aG audio,video tutor
install -o tutor -g tutor -m 644 $Q/cargando.html /home/tutor/cargando.html
install -d -o tutor -g tutor /home/tutor/perfil
cat > /home/tutor/perfil/user.js <<'EOF'
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("media.autoplay.default", 0);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
EOF
chown tutor:tutor /home/tutor/perfil/user.js

# 2) el tutor como servicio al encender
cat > /etc/systemd/system/tutor-backend.service <<EOF
[Unit]
Description=Tutor de ingles (modelo + pagina local)
After=network.target
[Service]
User=christiam
ExecStart=/bin/bash $Q/backend.sh
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF

# 3) quiosco: cage muestra sólo Firefox a pantalla completa en tty1, como el usuario tutor
cat > /etc/pam.d/cage <<'EOF'
auth     required pam_unix.so nullok
account  required pam_unix.so
session  required pam_unix.so
session  required pam_systemd.so
EOF
cat > /etc/systemd/system/tutor-quiosco.service <<'EOF'
[Unit]
Description=Tutor de ingles en pantalla completa (cage)
After=systemd-user-sessions.service plymouth-quit-wait.service tutor-backend.service
Wants=dbus.socket systemd-logind.service
Conflicts=getty@tty1.service
ConditionPathExists=/dev/tty1
[Service]
Type=simple
User=tutor
PAMName=cage
TTYPath=/dev/tty1
TTYReset=yes
TTYVHangup=yes
TTYVTDisallocate=yes
UtmpIdentifier=tty1
UtmpMode=user
StandardInput=tty-fail
Environment=XDG_SESSION_TYPE=wayland
ExecStart=/usr/bin/cage -s -- /usr/bin/firefox-esr --kiosk --profile /home/tutor/perfil file:///home/tutor/cargando.html
Restart=always
RestartSec=3
[Install]
WantedBy=graphical.target
EOF

# 4) pantalla de arranque propia y GRUB oculto (Esc o Shift al encender lo muestra)
install -d /usr/share/plymouth/themes/tutor
install -m 644 $Q/tutor.plymouth $Q/tutor.script /usr/share/plymouth/themes/tutor/
cp -n /etc/default/grub /etc/default/grub.antes_quiosco
sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=3 vt.global_cursor_default=0"/' /etc/default/grub
sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=1/' /etc/default/grub
grep -q '^GRUB_TIMEOUT_STYLE' /etc/default/grub && sed -i 's/^GRUB_TIMEOUT_STYLE=.*/GRUB_TIMEOUT_STYLE=hidden/' /etc/default/grub || echo 'GRUB_TIMEOUT_STYLE=hidden' >> /etc/default/grub
plymouth-set-default-theme -R tutor >> /tmp/apt_quiosco.log 2>&1
update-grub >> /tmp/apt_quiosco.log 2>&1

# 5) arranque: sin escritorio GNOME, directo al quiosco
systemctl disable gdm3 >/dev/null 2>&1 || true
systemctl daemon-reload
systemctl enable tutor-backend.service tutor-quiosco.service
systemctl set-default graphical.target
echo "quiosco instalado; reiniciar para verlo"
systemctl is-enabled tutor-backend tutor-quiosco
