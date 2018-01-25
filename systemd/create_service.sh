#!/bin/sh
echo "Installing Drawa Service"
SYSTEMD_SCRIPT_DIR=$( cd  $(dirname "${BASH_SOURCE:=$0}") && pwd)
cp -f "$SYSTEMD_SCRIPT_DIR/drawa.service" /lib/systemd/system
chown root:root /lib/systemd/system/drawa.service
systemctl daemon-reload
echo "Installing Default Config"
mkdir -p /etc/drawa
CONFIG_FILE_DIR=$(pwd)
cp -f "$CONFIG_FILE_DIR/drawa/default2service.conf" /etc/drawa/drawa.conf
cp -f "$CONFIG_FILE_DIR/drawa/aria2.conf" /etc/drawa/aria2.conf
getent passwd drawa > /dev/null
if [ $? -eq 0 ]; then
    echo "User Drawa already exist"
else
    echo "Creating Drawa user"
    useradd -r drawa
fi
