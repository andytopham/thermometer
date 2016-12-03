#!/bin/sh
echo "****** andyt installer for thermometer **********"
apt-get update
apt-get -y install python-dev python-smbus python-setuptools
pip install logging ubidots
mkdir log
echo 'Setting up sensor comms.'
modprobe w1-gpio
modprobe w1-therm
echo '** Installing gaugette **'
git clone git://github.com/guyc/py-gaugette.git
cd py-gaugette
python setup.py install
cd ..
git clone git://git.drogon.net/wiringPi
cd wiringPi
git pull origin
./build
cd ..
# next one is needed for wiringpi2
apt-get -y install python-dev
echo '** Installing wiringpi2 (needed for gaugette) **'
pip install wiringpi2
