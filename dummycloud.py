#!/usr/bin/python
# dummycloud.py

import logging, datetime
PATH = '/home/pi/master/tft/'
LOGFILE = 'log/dummycloud.log'
VALUEFILE = 'log/values.log'
TESTING = True

class Mydummycloud():
	def __init__(self, interval = 2):
		self.logger = logging.getLogger(__name__)
		self.logger.info('Dummy cloud initialised.')
		if TESTING:
			self.cloud_interval = datetime.timedelta(seconds = 10)	# currently overridden by thermometer.py
		else:
			self.cloud_interval = datetime.timedelta(minutes = interval)
		self.last_time = datetime.datetime.now()
		self.fp = open(PATH+VALUEFILE,'w')	
		self.fp.write('Dummy cloud writes\n')
		self.fp.close

	def _log_temp(self, temperature):
		self.fp = open(PATH+VALUEFILE,'a')	
		self.fp.write(str(temperature)+'\n')
		self.fp.close
		return(0)
		
	def write(self, val):
		'''Write a string to stdout'''
#		print ("...writing to cloud")
		now = datetime.datetime.now()
		if ((now - self.last_time) > self.cloud_interval):
			self.last_time = now
			try:
				self._log_temp(val)
#				print ('Dummy cloud write:', val)
				self.logger.info('Write to dummycloud OK')
			except:
				self.logger.warning("Error saving to dummycloud. Value="+str(val))				
				return(False)
		return(True)	
	
	def read(self):
		self.fp = open(PATH+VALUEFILE,'r')
		data = 'test'
		sensor = ''
		while data != '':
			data = self.fp.readline()
			sensor.append(data[2])
		self.fp.close
		return(sensor)
	
if __name__ == "__main__":
	logging.basicConfig(filename=PATH+LOGFILE,filemode='w',level=logging.INFO)
	logging.warning('Running dummycloud as a standalone app.')
	print ('Writing test value to dummycloud')
	myDummy = Mydummycloud()	# Beware!!! Writes all the time.
	myDummy.write(12)		# Test value
	print ('Wrote value 12')
	