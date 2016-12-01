#!/bin/sh
echo "****** andyt installer for thermometer **********"
apt-get update
apt-get -y install python-dev python-smbus python-setuptools
pip install logging ubidots
mkdir log
echo 'Setting up sensor comms.'
modprobe w1-gpio
modprobe w1-therm