#!/bin/sh
echo "****** andyt installer for thermometer **********"
apt-get update
apt-get -y install python-dev python-smbus python-setuptools python-pip
apt-get -y install build-essential 
# apt-get python-imaging
pip install logging ubidots RPi.GPIO
pip install beebotte

echo "** Setting up pillow, python graphics."
apt-get install libjpeg-dev -y
apt-get install zlib1g-dev -y
apt-get install libfreetype6-dev -y
apt-get install liblcms1-dev -y
apt-get install libopenjp2-7 -y
apt-get install libtiff5 -y
apt-get install python3-setuptools -y

# numpy needed for Adafruit ILI9341
pip install numpy
apt-get install python-pil -y
# Adafruit seems to still use pil, even though this has been superceeded by pillow
# pip install pillow

mkdir log


echo '** Installing adafruit SSD1306'
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install

echo '** Installing Adafruit code for controlling ILI9341 tft'
cd ..
git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git
cd Adafruit_Python_ILI9341
sudo python setup.py install

echo '** Fetching fonts'
cd /home/pi/master
mkdir fonts
cd fonts
curl -sL https://github.com/chrissimpkins/Hack/releases/download/v2.018/Hack-v2_018-ttf.tar.gz | tar xz
cd /home/pi

echo '** Setting up systemd service for autostart'
cp /home/pi/master/thermometer/startthermometer.service /lib/systemd/system
chmod 644 /lib/systemd/system/startthermometer.service
systemctl daemon-reload
systemctl enable startthermometer.service

echo '** Setting up sensor comms.'
# echo 'dtoverlay=w1-gpio' >> /boot/config.txt
cat "dtoverlay=w1-gpio,gpiopin=4,pullup=on" >> /boot/config.txt

echo '** And need to reboot...'

# These two lines needed after reboot, but can probably be in the code.
# modprobe w1-gpio
# modprobe w1-therm
