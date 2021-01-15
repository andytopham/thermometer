#!/usr/bin/python
# DS18B20.py
# Developed from sensor instructions from:
#  https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
# /boot/config.txt add....
#   dtoverlay=w1-gpio,gpiopin=4,pullup=on

import logging, os, glob, time

PATH = '/home/pi/master/tft/'
LOGFILE = 'log/DS18B20.log'

class DS18B20():
	def __init__(self):
		self.logger = logging.getLogger(__name__)
#		os.system('modprobe w1-gpio')
#		os.system('modprobe w1-therm')
		base_dir = '/sys/bus/w1/devices/'
		self.device_file = []
		self.min_temp = []
		self.max_temp = []
		folders = glob.glob(base_dir + '28*')
		self.no_devices = len(folders)
		print ( 'Found ',self.no_devices, ' DS18B20 devices')
		for dev in folders:
			dev_file = dev + '/w1_slave'
			self.device_file.append(dev_file)
		for i in range(self.no_devices):
			temperature = self.read_temp(i)	
#			print ( i, temperature)
			self.min_temp.append(temperature)
			self.max_temp.append(temperature)
		self.logger.info('Temperature sensor initialised.')

	def _read_temp_raw(self, device):
		try:
			f = open(self.device_file[device], 'r')
			lines = f.readlines()
			f.close()
			return lines
		except:
			self.logger.warning("Error reading device file")
			return(' ')

	def read_temp(self, device):
		lines = self._read_temp_raw(device)
		while lines[0].strip()[-3:] != 'YES':
			time.sleep(0.2)
			lines = self._read_temp_raw(device)
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			temp_c = float(temp_string) / 1000.0
			temp_f = temp_c * 9.0 / 5.0 + 32.0
			if int(temp_c) == 85:		# sensor still converting
				self.logger.warning('Temperature read as 85C.')
			self.logger.info('Temperature:'+str(temp_c))
			return temp_c

	def read_max_min_temp(self, device):
		temperature = self.read_temp(device)
		if temperature < self.min_temp[device]:
			self.min_temp[device] = temperature
		if temperature != 85:
			if temperature > self.max_temp[device]:
				self.max_temp[device] = temperature
		return(temperature)
	
if __name__ == "__main__":
	logging.basicConfig(filename=PATH+LOGFILE,filemode='w',level=logging.WARNING)
	logging.warning('Running DS18B20 as a standalone app.')
	myReader = DS18B20()
#	print ( myReader.read_max_min_temp())
#	print ( 'min=',myReader.min_temp, 'max=',myReader.max_temp)
	
	