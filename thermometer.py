#!/usr/bin/python
# thermometer.py
# A thermometer that senses using a DS18B20 and outputs to oled or 7seg display and ubidots cloud.

import os, logging, glob, time, sys
import alarm, DS18B20, system
import keys
# Other imports in code: oled, uoled, sevenseg, dummycloud, myubidots, mybeebotte
 
LOGFILE = '/home/pi/master/thermometer/log/thermometer.log'
VALUEFILE = '/home/pi/master/thermometer/log/values.log'
TITLE_ROW = 0
LABELS_ROW = 1
VALUES_ROW = 2
VALUES_ROW2 = 3
STATUS_ROW = 4
CLOCK_ROW = 5
CLOUD_ROW = 6
BEEBOTTE_INTERVAL = 60
BIG_TEXT = False

class Thermometer():
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.displaytype = keys.display
		self.cloud = keys.cloud
		if self.displaytype == 'oled':
			try:
				import oled
				self.display = oled.Oled()
				self.display.writerow(TITLE_ROW,"Starting up")
			except:
				self.logger.error('Oled failed init.')
				sys.exit(0)
		elif self.displaytype == 'uoled':
			try:
				import uoled
				print 'Setting up uoled'
				self.display = uoled.Screen()
			except:
				print 'Uoled failed init.'
				self.logger.error('Uoled failed init.')
				sys.exit(0)
		elif self.displaytype == 'uoledada':
			try:
				import uoledada
				print 'Setting up uoledada'
				self.display = uoledada.Screen()
			except:
				print 'Uoledada failed init.'
				self.logger.error('Uoledada failed init.')
				sys.exit(0)
		elif self.displaytype == 'uoledi2c':
			try:
				import uoledi2c
				print 'Setting up uoledi2c'
				self.display = uoledi2c.Screen()
			except:
				print 'Uoledi2c failed init.'
				self.logger.error('Uoledi2c failed init.')
				sys.exit(0)
		elif self.displaytype == '7seg':
			try:
				import sevenseg
				self.sevenseg = sevenseg.Sevenseg()
			except:
				self.logger.error('7seg failed init.')
				sys.exit(0)
		elif self.displaytype == 'tft':
			try:
				import tft
				self.display = tft.Screen()
			except:
				self.logger.error('tft failed init.')
				sys.exit(0)
		else:
			self.logger.error('No display specified.')
			print 'No display specified'
			sys.exit(0)
			
		if self.cloud == 'none':
			try:
				import dummycloud
				self.myCloud = dummycloud.Mydummycloud()
				self.display.cloud_type = 'file'
				print 'Using dummy cloud'
			except:
				self.display.writerow(1,"Dummycloud failed init")
				self.logger.error('Dummycloud failed init.')
				sys.exit(0)
		elif self.cloud == 'ubidots':
			try:
				import myubidots
				self.myCloud = myubidots.Myubidots()
				self.display.cloud_type = 'ubidots'
				print 'Ubidots cloud'
			except:
				self.display.writerow(1,"Ubidots failed init")
				self.logger.error('Ubidots failed init.')
				sys.exit(0)
		elif self.cloud == 'beebotte':
			try:
				import mybeebotte
#				self.myCloud = mybeebotte.Mybeebotte(interval = BEEBOTTE_INTERVAL, no_sensors = 2)
				self.myCloud = mybeebotte.Mybeebotte(no_sensors = 2)
				self.display.cloud_type = 'beebotte'
				print 'Beebotte cloud'
			except:
				self.display.writerow(TITLE_ROW,"Beebotte failed init")
				self.logger.error('Beebotte failed init.')
				print "Beebotte failed init.",sys.exc_info()[0]
				sys.exit(0)
		else:
			self.logger.error('Cloud type not specified. Check keys file.')
			print 'Cloud type not specified. Check keys file.'
			self.display.cloud_type = 'no cloud'
			sys.exit(0)			
		self.cloud_error = False
		
		try:
			self.myDS = DS18B20.DS18B20()
		except:
			self.display.writerow(1,"Sensor init failed")
			self.logger.error('Sensor init failed.')
			sys.exit(0)
		self.myAlarm = alarm.Alarm()
		self.mySystem = system.System()
		hostname = self.mySystem.hostname()
		self.display.writerow(STATUS_ROW,'Hostname:'+hostname)
		self.display.writerow(CLOUD_ROW,self.cloud)
		self.log_counter = 0		
		self.cloud_counter = 0
		self.display.writerow(TITLE_ROW, 'Thermometer')
		self.display.writerow(LABELS_ROW, 'Min   Now   Max  ')

	def _update_display(self, temperature):
		clock = time.strftime("%R")+' '
		string = clock + ' '
		for dev in range(self.myDS.no_devices):
			if temperature[dev] == 85:
				print 'Skipping because had poor sensor reading twice.'
				self.display.writerow(TITLE_ROW,'Bad sensor')
			else:
				string += str(dev)+' '+str(temperature[dev])+' '
		print string
		if self.displaytype == 'oled':
			if self.myAlarm.alarm_interval():		# if we should display anything
				clock = time.strftime("%R")
				if self.cloud_error == False:
					mystring1 = '.*{0:^16s}'.format(clock)
				else:
					mystring1 = '.U{0:^16s}'.format(clock)				
				mystring2 = '{1:2.1f}C {2:2.1f}C {3:2.1f}C  '.format(clock, 
					self.myDS.min_temp, temperature, self.myDS.max_temp)
				self.display.writerow(STATUS_ROW,mystring1)
				self.display.writerow(VALUES_ROW,mystring2)
			else:
				self.display.cleardisplay()
			self._toggle_indicator()
		elif self.displaytype == 'uoled' or self.displaytype == 'uoledi2c' or self.displaytype == 'tft':
			if self.myAlarm.alarm_interval():		# if we should display anything
				if BIG_TEXT:
					self.write_single_temperature(temperature, self.myDS.max_temp, self.myDS.min_temp, self.cloud_error, self.myDS.no_devices)				
				else:
					self.write_temperatures(temperature, self.myDS.max_temp, self.myDS.min_temp, self.cloud_error, self.myDS.no_devices)				
					self.display.writerow(CLOCK_ROW, 'Reading: '+clock+'  ')					
			else:
				self.display.cleardisplay()
#		elif self.displaytype == 'tft':
#			print 'displaying values...',str(temperature)
#			self.write_temperatures(temperature, self.myDS.max_temp, self.myDS.min_temp, self.cloud_error, self.myDS.no_devices)				
		return(0)
		
	def write_temperatures(self, temperature, max, min, cloud, num_devs):
		string = '{0:2.1f}C {1:2.1f}C {2:2.1f}C  '.format(min[0], temperature[0], max[0])
		self.display.writerow(VALUES_ROW, string)
		if num_devs > 1:
			string = '{0:2.1f}C {1:2.1f}C {2:2.1f}C  '.format(min[1], temperature[1], max[1])
			self.display.writerow(VALUES_ROW2, string)			
		return(0)
		
	def write_single_temperature(self, temperature, max, min, cloud, num_devs):
		string = '{0:2.1f}C '.format(temperature[0])
		self.display.writerow(TITLE_ROW, string)
		string = "Cloud = "+self.cloud+time.strftime(" %R ")
		self.display.writerow(LABELS_ROW, string, fontsize="small")
#		if num_devs > 1:
#			string = '{0:2.1f}C {1:2.1f}C {2:2.1f}C  '.format(min[1], temperature[1], max[1])
#			self.display.writerow(VALUES_ROW2, string)			
		return(0)
		
	def _cloud_log(self, t):
#		self.cloud_counter += 1
#		print 'Cloud counter = ',self.cloud_counter
		if self.myDS.no_devices == 1:
			string = time.strftime("%R") + ' 0 ' + str(t[0])
		else:
			string = time.strftime("%R") + ' 0 ' + str(t[1]) + ' 1 ' + str(t[0])
		if self.myCloud.write(string) == False:
			print 'Error writing to cloud.'
#			self.display.writerow(LABELS_ROW, 'Error writing to cloud', fontsize='small')
#			self.display.writerow(LABELS_ROW, 'Error writing to cloud')
			return(True)
		else:
			print 'Wrote to cloud: ', string
			clock = time.strftime("%R")+' '
			self.display.writerow(CLOUD_ROW, self.cloud+': '+clock+'  ')					
			return(False)
	
	def _draw_graph(self):
		data = self.myCloud.read()
		self.display.draw_graph(data)
		return(0)
	
	def read_temperature(self, device):
		temperature = self.myDS.read_max_min_temp(device)	
		if temperature == 85:
			print 'Error: temperature = 85'
			time.sleep(.5)
			temperature = self.myDS.read_max_min_temp(device)	# try a second time
		return(temperature)
	
	def mainloop(self):
		t = [None]*2
		while True:
			for device in range(self.myDS.no_devices):
				t[device] = self.read_temperature(device)
			self.display.cloud_error = self._cloud_log(t)
			self._update_display(t)
			time.sleep(5)

if __name__ == "__main__":
#	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.WARNING)
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.INFO)
	logging.warning('Running thermometer as a standalone app.')

	print 'Starting thermometer'
	myThermometer = Thermometer()
	myThermometer.mainloop()
	