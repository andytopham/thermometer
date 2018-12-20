#!/bin/sh
echo "****** andyt installer for thermometer **********"
apt-get update
apt-get -y install python-dev python-smbus python-setuptools python-pip
apt-get -y install build-essential python-imaging
pip install logging ubidots RPi.GPIO
pip install beebotte

mkdir log
echo 'Setting up sensor comms.'
echo 'dtoverlay=w1-gpio' >> /boot/config.txt

echo 'Installing adafruit SSD1306'
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install

echo 'Installing Adafruit code for controlling ILI9341 tft'
cd ..
git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git
cd Adafruit_Python_ILI9341
sudo python setup.py install

echo 'Fetching fonts'
cd /home/pi/master
mkdir fonts
cd fonts
curl -sL https://github.com/chrissimpkins/Hack/releases/download/v2.018/Hack-v2_018-ttf.tar.gz | tar xz
cd /home/pi

echo 'Setting up systemd service for autostart'
cp /home/pi/master/thermometer/startthermometer.service /lib/systemd/system
chmod 644 /lib/systemd/system/startthermometer.service
systemctl daemon-reload
systemctl enable startthermometer.service

cat "dtoverlay=w1-gpio,gpiopin=4,pullup=on" >> /boot/config.txt

echo 'And need to reboot'

# These two lines needed after reboot, but can probably be in the code.
# modprobe w1-gpio
# modprobe w1-therm
