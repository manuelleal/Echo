#!/bin/bash
# (root) 5-nov: el firmware tenía en BootOrder una entrada inexistente y el arranque quedó en negro antes de Linux.
# Deja UNA entrada fija para Debian (shim) de primera y la ruta de respaldo EFI/BOOT con su grub.cfg.
set -e
cp /boot/efi/EFI/debian/grub.cfg /boot/efi/EFI/BOOT/grub.cfg
# borra entradas duplicadas "Tutor (Debian)" y deja una sola
for n in $(efibootmgr | sed -n 's/^Boot\([0-9A-F]\{4\}\)\* Tutor (Debian).*/\1/p'); do efibootmgr -q -b "$n" -B; done
efibootmgr -q -c -d /dev/mmcblk1 -p 1 -L "Tutor (Debian)" -l '\EFI\debian\shimx64.efi'
N=$(efibootmgr | sed -n 's/^Boot\([0-9A-F]\{4\}\)\* Tutor (Debian).*/\1/p' | head -1)
RESTO=$(efibootmgr | sed -n 's/^Boot\([0-9A-F]\{4\}\)\*.*/\1/p' | grep -v "^$N$" | paste -sd, -)
efibootmgr -q -o "$N,$RESTO"
efibootmgr | head -8
