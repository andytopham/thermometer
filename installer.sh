#!/bin/sh
echo "****** andyt installer for thermometer **********"
apt-get update
apt-get -y install python-dev python-smbus python-setuptools python-pip
apt-get -y install build-essential python-imaging
pip install logging ubidots RPi.GPIO
mkdir log
echo 'Setting up sensor comms.'
modprobe w1-gpio
modprobe w1-therm
echo 'Installing adafruit SSD1306'
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install

echo 'Fetching fonts'
cd /home/pi/master
mkdir fonts
cd fonts
curl -sL https://github.com/chrissimpkins/Hack/releases/download/v2.018/Hack-v2_018-ttf.tar.gz | tar xz
cd /home/pi

echo 'Need to enable DS sensors by editing /boot/config.txt'
echo 'Instructions on adafruit website'
