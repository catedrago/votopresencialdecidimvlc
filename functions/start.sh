#!/bin/bash

mkdir -p /tmp/usb/

chown -R dietpi:dietpi /tmp/usb

mount -t vfat /dev/sda1 /tmp/usb/ -o uid=dietpi,gid=dietpi

runuser -l dietpi -c 'python3 /root/evotebox2/manage.py runserver'

runuser -l dietpi -c '@chromium-browser --incognito --kiosk http://127.0.0.1:8000'
