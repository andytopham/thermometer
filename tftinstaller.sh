#!/bin/sh
echo "****** andyt installer for tft clock **********"
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

apt update
apt upgrade -y
apt -y install python3-pip

echo "** Starting pip installs **"
pip3 install --upgrade setuptools
pip3 install RPI.GPIO
pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-rgb-display
apt -y install ttf-dejavu
apt -y install python3-pil
# For SSD1306
pip3 install adafruit-circuitpython-ssd1306
pip3 install Adafruit-SSD1306
pip3 install Adafruit-GPIO

pip3 install logging
mkdir log

echo '** Setting up systemd service for autostart'
cp starttftclock.service /lib/systemd/system
chmod 644 /lib/systemd/system/starttftclock.service
systemctl daemon-reload
systemctl enable starttftclock.service

echo '** Need to enable i2c via raspi-config. **'
echo '** And need to reboot...'

