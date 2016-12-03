#!/usr/bin/python
# thermometer.py
# A thermometer that senses using a DS18B20 and outputs to oled or 7seg display and ubidots cloud.

import os, logging, glob, time, sys
import alarm, DS18B20, system
import keys
# Other imports in code: oled, uoled, sevenseg, dummycloud, myubidots, mybeebotte
 
LOGFILE = '/home/pi/master/thermometer/log/thermometer.log'
VALUEFILE = '/home/pi/master/thermometer/log/values.log'

class Thermometer():
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.displaytype = keys.display
		self.cloud = keys.cloud
		if self.displaytype == 'oled':
			try:
				import oled
				self.display = oled.Oled()
				self.display.writerow(1,"Starting up")
			except:
				self.logger.error('Oled failed init.')
				sys.exit(0)
		elif self.displaytype == 'uoled':
			try:
				import uoled
				print 'Setting up uoled'
				self.display = uoled.Screen()
				self.display.writerow(0,'Thermometer')
				self.display.writerow(2,'Getting ready')
				self.display.writerow(3,' Min   Now   Max')
			except:
				print 'Uoled failed init.'
				self.logger.error('Uoled failed init.')
				sys.exit(0)
		elif self.displaytype == '7seg':
			try:
				import sevenseg
				self.sevenseg = sevenseg.Sevenseg()
			except:
				self.logger.error('7seg failed init.')
				sys.exit(0)
		else:
			self.logger.error('No display specified.')
			print 'No display specified'
			sys.exit(0)
			
		if self.cloud == 'none':
			try:
				import dummycloud
				self.myCloud = dummycloud.Mydummycloud()
				self.cloud_error = False
			except:
				self.display.writerow(1,"Dummycloud failed init")
				self.logger.error('Dummycloud failed init.')
				sys.exit(0)
		elif self.cloud == 'ubidots':
			try:
				import myubidots
				self.myCloud = myubidots.Myubidots()
				self.cloud_error = False
			except:
				self.display.writerow(1,"Ubidots failed init")
				self.logger.error('Ubidots failed init.')
				sys.exit(0)
		elif self.cloud == 'beebotte':
			try:
				import mybeebotte
				self.myCloud = mybeebotte.Mybeebotte()
				self.cloud_error = False
			except:
				self.display.writerow(1,"Beebotte failed init")
				self.logger.error('Beebotte failed init.')
				sys.exit(0)
		else:
			self.logger.error('Cloud type not specified. Check keys file.')
			print 'Cloud type not specified. Check keys file.'
			sys.exit(0)			

		try:
			self.myDS = DS18B20.DS18B20()
		except:
			self.display.writerow(1,"Sensor init failed")
			self.logger.error('Sensor init failed.')
			sys.exit(0)
		self.myAlarm = alarm.Alarm()
		self.mySystem = system.System()
		hostname = self.mySystem.hostname()
		self.display.writerow(2,hostname)
		self.flag = False
#		self.fp = open(VALUEFILE,'w')
#		self.fp.write('Temperature values\n')
#		self.fp.close()
		self.log_counter = 0
		self.display.writerow(1,"  Initialised     ")
		
	def _toggle_indicator(self):
		if self.flag == False:
			self.flag = True
			self.display.writerow(1,' ')
			return(0)
		else:
			self.flag = False
	

	def _update_display(self, temperature, device):
		if self.displaytype == 'oled':
			if self.myAlarm.alarm_interval():		# if we should display anything
				clock = time.strftime("%R")
				if self.cloud_error == False:
					mystring1 = '.*{0:^16s}'.format(clock)
				else:
					mystring1 = '.U{0:^16s}'.format(clock)				
				mystring2 = '{1:2.1f}C {2:2.1f}C {3:2.1f}C  '.format(clock, 
					self.myDS.min_temp, temperature, self.myDS.max_temp)
				self.display.writerow(1,mystring1)
				self.display.writerow(2,mystring2)
			else:
				self.display.cleardisplay()
		if self.displaytype == 'uoled':
			if self.myAlarm.alarm_interval():		# if we should display anything
				clock = time.strftime("%R")
				if self.cloud_error == False:
					mystring1 = '.*{0:^16s}'.format(clock)
				else:
					mystring1 = '.U{0:^16s}'.format(clock)				
				mystring2 = '{1:2.1f}C {2:2.1f}C {3:2.1f}C  '.format(clock, 
					self.myDS.min_temp[device], temperature, self.myDS.max_temp[device])
				if False:		# this is the small text output version
					self.display.writerow(1,mystring1)
					self.display.writerow(2+device,mystring2)
				else:
					mystring2 = '{0:2.1f}C        '.format(temperature)
					mystringmax = '{0:2.1f}C      '.format(self.myDS.max_temp[device])
					mystringmin = '{0:2.1f}C      '.format(self.myDS.min_temp[device])
					self.display.write_temperatures(device, mystring2, mystringmax, mystringmin)				
			else:
				self.display.cleardisplay()
		if False:		# only do this if using small text
			self._toggle_indicator()
		return(0)
		
	def _log_temp(self, temperature):
		self.log_counter += 1
		if self.log_counter > 12:
			self.log_counter = 0
			self.fp = open(VALUEFILE,'w')
			self.fp.write(str(temperature)+'\n')
			self.fp.close
		return(0)
		
	def measure_temp(self):
		return(0)
		
	def _cloud_log(self, temperature):
		if self.myCloud.write(temperature) == False:
			self.cloud_error = True
			print 'Error writing to cloud.'
			self.display.writerow(1,' Cloud error')
		else:
			self.cloud_error = False
		return(0)
	
	def mainloop(self):
		while True:
			string = ''
			for device in range(self.myDS.no_devices):
				temperature = self.myDS.read_max_min_temp(device)	
				if temperature == 85:
					print 'Error: temperature = 85'
					time.sleep(.5)
					temperature = self.myDS.read_max_min_temp(device)	# try a second time
				print 'Device=',device,'Min=',self.myDS.min_temp[device],' Current=',temperature,' Max=',self.myDS.max_temp[device]	
				if temperature == 85:
					print 'Skipping because had poor sensor reading twice.'
					self.display.writerow(1,'Bad sensor')
				else:
					self._update_display(temperature,device)
					string += str(device)+' '+str(temperature)+' '
			self._cloud_log(string)
			time.sleep(5)

if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.WARNING)
	logging.warning('Running thermometer as a standalone app.')

	print 'Starting thermometer'
	myThermometer = Thermometer()
	myThermometer.mainloop()
	