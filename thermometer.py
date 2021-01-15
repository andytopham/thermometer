#!/usr/bin/python
# thermometer.py
# A thermometer that senses using one or more DS18B20.
# Outputs to oled or 7seg display or tft.
# Logs data to beebotte or ubidots cloud.

import os, logging, glob, time, sys, datetime
import alarm, DS18B20, system
import keys
# Other imports in code: oled, uoled, sevenseg, dummycloud, myubidots, mybeebotte
 
PATH = '/home/pi/master/tft/'
LOGFILE = 'log/thermometer'
VALUEFILE = 'log/values.log'
TITLE_ROW = 0
LABELS_ROW = 1
VALUES_ROW = 2
VALUES_ROW2 = 3
NOWTIME_ROW = 7
CLOCK_ROW = 8		# time of last reading shown on display

CLOUD_ROW2 = 9		# cloud errors
CLOUD_ROW4 = 9		# more info about the cloud settings, e.g. beebotte id
CLOUD_ROW = 10		# name of cloud
CLOUD_ROW3 = 11		# cloud count - number of readings to cloud
STATUS_ROW = 12		# hostname

CLOUD_INTERVAL = 120		#  secs - check cloud_write
READING_INTERVAL = 15		# 15 seconds (used in main loop)
BIG_TEXT = True

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
				print ( 'Setting up uoled')
				self.display = uoled.Screen()
			except:
				print ( 'Uoled failed init.')
				self.logger.error('Uoled failed init.')
				sys.exit(0)
		elif self.displaytype == 'uoledada':
			try:
				import uoledada
				print ( 'Setting up uoledada')
				self.display = uoledada.Screen()
			except:
				print ( 'Uoledada failed init.')
				self.logger.error('Uoledada failed init.')
				sys.exit(0)
		elif self.displaytype == 'uoledi2c':
			try:
				import uoledi2c
				print ( 'Setting up uoledi2c')
				self.display = uoledi2c.Screen()
			except:
				print ( 'Uoledi2c failed init.')
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
			print ("setting up newtft")
			try:
				import newtft						# note newtft based on latest adafruit lib
				self.display = newtft.Screen()
			except:
				self.logger.error('newtft failed init.')
				sys.exit(0)
		else:
			self.logger.error('No display specified.')
			print ( 'No display specified')
			sys.exit(0)
			
		if self.cloud == 'none':
			try:
				import dummycloud
				self.myCloud = dummycloud.Mydummycloud()
				self.display.cloud_type = 'file'
				print ( 'Using dummy cloud')
			except:
				self.display.newwriterow(1,"Dummycloud failed init")
				self.logger.error('Dummycloud failed init.')
				sys.exit(0)
		elif self.cloud == 'ubidots':
			try:
				import myubidots
				self.myCloud = myubidots.Myubidots()
				self.display.cloud_type = 'ubidots'
				print ( 'Ubidots cloud')
			except:
				self.display.newwriterow(1,"Ubidots failed init")
				self.logger.error('Ubidots failed init.')
				sys.exit(0)
		elif self.cloud == 'beebotte':
			try:
				import mybeebotte
				self.myCloud = mybeebotte.Mybeebotte( no_sensors = 2)
				self.display.cloud_type = 'beebotte'
				self.display.writerow(CLOUD_ROW4, keys.beebotte_variable+' '+keys.beebotte_variable2)
				print ( 'Beebotte cloud')
			except:
				self.display.writerow(TITLE_ROW,"Beebotte failed init")
				self.logger.error('Beebotte failed init.')
				print ( "Beebotte failed init.",sys.exc_info()[0])
				sys.exit(0)
		else:
			self.logger.error('Cloud type not specified. Check keys file.')
			print ( 'Cloud type not specified. Check keys file.')
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
		self.display.newwriterow(STATUS_ROW,'Hostname:'+hostname)
		self.display.newwriterow(CLOUD_ROW, 'Cloud:'+self.cloud)
		self.log_counter = 0		
		self.cloud_counter = 0
		self.display.newwriterow(TITLE_ROW, 'Thermometer')
		if BIG_TEXT == False:
			self.display.newwriterow(LABELS_ROW, 'Min    Now   Max  ')

	def _update_display(self, temperature):
#		print ("update display")
		clock = time.strftime("%R")+' '
		string = clock + ' '
		for dev in range(self.myDS.no_devices):
			if temperature[dev] == 85:
				print ( 'Skipping because had poor sensor reading twice.')
				self.display.newwriterow(TITLE_ROW,'Bad sensor')
			else:
				string += str(dev)+' '+str(temperature[dev])+' '
#		print ( string)
		if self.displaytype == 'oled':
			if self.myAlarm.alarm_interval():		# if we should display anything
				clock = time.strftime("%R")
				if self.cloud_error == False:
					mystring1 = '.*{0:^16s}'.format(clock)
				else:
					mystring1 = '.U{0:^16s}'.format(clock)				
				mystring2 = '{1:2.1f}C {2:2.1f}C {3:2.1f}C  '.format(clock, 
					self.myDS.min_temp, temperature, self.myDS.max_temp)
				self.display.newwriterow(STATUS_ROW,mystring1)
				self.display.newwriterow(VALUES_ROW,mystring2)
			else:
				self.display.cleardisplay()
			self._toggle_indicator()
		elif self.displaytype == 'uoled' or self.displaytype == 'uoledi2c' or self.displaytype == 'tft' or self.displaytype == 'uoledada':
			if self.myAlarm.alarm_interval():		# if we should display anything
				if BIG_TEXT:
					self.write_single_temperature(temperature, self.myDS.max_temp, self.myDS.min_temp, self.cloud_error, self.myDS.no_devices)				
				else:
					self.write_temperatures(temperature, self.myDS.max_temp, self.myDS.min_temp, self.cloud_error, self.myDS.no_devices)				
			else:
				self.display.cleardisplay()
		return(False)
		
	def write_temperatures(self, temperature, max, min, cloud, num_devs):
		clock = time.strftime("%R")
		string = '{0:2.1f}C {1:2.1f}C {2:2.1f}C  '.format(min[0], temperature[0], max[0])
#		print ("writing temp")
		self.display.newwriterow(VALUES_ROW, string)
		if num_devs > 1:
			string = '{0:2.1f}C {1:2.1f}C {2:2.1f}C  '.format(min[1], temperature[1], max[1])
			self.display.newwriterow(VALUES_ROW2, string)			
		self.display.newwriterow(CLOCK_ROW, 'Readtime: '+clock+'  ')					
		return(0)
		
	def write_single_temperature(self, temperature, max, min, cloud, num_devs):
		clock = time.strftime("%R")
		string = 'In: {0:2.1f}C '.format(temperature[0])
		self.display.newwriterow(LABELS_ROW, string, clear=True, bigfont=True)
		string = 'Out:{0:2.1f}C '.format(temperature[1])
		self.display.newwriterow(VALUES_ROW2, string, clear=True, bigfont=True)
		self.display.newwriterow(CLOCK_ROW, 'Readtime: '+clock+'  ')					
		return(0)
		
	def _cloud_log(self, t):
		now = datetime.datetime.now()
		if ((now - self.cloud_time) > self.cloud_interval):
			self.cloud_time = now
			if self.myDS.no_devices == 1:
				string = time.strftime("%R") + ' 0 ' + str(t[0])
			else:
				string = time.strftime("%R") + ' 0 ' + str(t[1]) + ' 1 ' + str(t[0])
			if self.myCloud.write(string) == False:
				print ( 'Error writing value to cloud.')
				self.logger.error('Error writing value to cloud')
				self.display.newwriterow(CLOUD_ROW2, 'Error writing value to cloud')
				return(True)
			else:
				print ( 'Wrote to cloud: ', string)
				self.cloud_counter += 1
				self.logger.info('Number of values written to cloud:'+str(self.cloud_counter))
				clock = time.strftime("%R")+' '
				self.display.newwriterow(CLOUD_ROW3, 'Cloud count:'+str(self.cloud_counter))
				return(False)
	
	def _draw_graph(self):
		data = self.myCloud.read()
		self.display.draw_graph(data)
		return(0)
	
	def read_temperature(self, device):
		temperature = self.myDS.read_max_min_temp(device)	
		if temperature == 85:
			print ( 'Error: temperature = 85')
			time.sleep(.5)
			temperature = self.myDS.read_max_min_temp(device)	# try a second time
		return(temperature)

	def readings(self):
		t = [None]*2
		now = datetime.datetime.now()
		if ((now - self.reading_time) > self.reading_interval):
			self.reading_time = now
		for device in range(self.myDS.no_devices):
			try:
				t[device] = self.read_temperature(device)
			except:
				print ( 'Error reading temperature')
				self.logger.error('Error reading temperature')	
				time.sleep(5)		# give it some time to recover - was 15
				continue			# next loop iteration
		return(t)
	
	def mainloop(self):
#		print ("main loop")
		self.display.newwriterow(NOWTIME_ROW, 'Nowtime: '+time.strftime("%R")+'  ')					
		now = datetime.datetime.now()
		self.cloud_interval = datetime.timedelta(seconds = CLOUD_INTERVAL)
		self.reading_interval = datetime.timedelta(seconds = READING_INTERVAL)
		self.cloud_time = now - self.cloud_interval		# to make sure we get an instant reading
		self.reading_time = now
		while True:
			self.display.newwriterow(NOWTIME_ROW, 'Nowtime: '+time.strftime("%H:%M:%S")+'  ')					
			t = self.readings()
			self._cloud_log(t)
			self._update_display(t)

if __name__ == "__main__":
	# Note that the logging level can be set at the command line with --log=INFO.
	# filemode='w' means that the file is started afresh each time.
#	numeric_level = getattr(logging, loglevel.upper(), WARNING)
#	if not isinstance(numeric_level, int):
#		raise ValueError('Invalid log level: %s' % loglevel)	
	logfilename = PATH+LOGFILE+time.strftime("%y%m%d.log")
#	logging.basicConfig(filename=logfilename,filemode='w',level=logging.WARNING,format='%(asctime)s:%(message)s')
	logging.basicConfig(filename=logfilename,filemode='w',level=logging.INFO,format='%(asctime)s:%(message)s')
	logging.warning('Running thermometer as a standalone app.')

	print ( 'Starting thermometer')
	myThermometer = Thermometer()
	myThermometer.mainloop()
	logging.shutdown()
	
	