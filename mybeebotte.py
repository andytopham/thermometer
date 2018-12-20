#!/usr/bin/python
# mybeebotte.py
# To get beebotte working....
#$ sudo apt-get install python-setuptools
#$ sudo easy_install pip
#$ sudo pip install beebotte

import beebotte
import logging, datetime
import keys

LOGFILE = 'log/beebotte.log'
DEFAULT_INTERVAL = 1		# minutes

class Mybeebotte():
	def __init__(self, interval = DEFAULT_INTERVAL, no_sensors = 1):
		self.logger = logging.getLogger(__name__)
		self.logger.info('Beebotte init starting.')
		print 'Beebotte setting up. Interval:', interval, ' Sensors:', no_sensors
		try:
			api = beebotte.BBT(keys.beebotte_api_key, keys.beebotte_secret_key)
			self.test_variable = beebotte.Resource(api,keys.beebotte_channel,keys.beebotte_variable)
			if no_sensors == 2:
				self.test_variable2 = beebotte.Resource(api,keys.beebotte_channel,keys.beebotte_variable2)
			self.logger.info('Beebotte initialised. Interval:'+str(interval)+' Sensors:'+ str(no_sensors))
			self.logger.info('Beebotte channel: '+keys.beebotte_channel+' variables: '+keys.beebotte_variable+' '+keys.beebotte_variable2)
		except:
			self.logger.error('Beebotte failed to initialise.')
		self.beebotte_interval = datetime.timedelta(minutes = interval)
		self.no_sensors = no_sensors
		self.last_time = datetime.datetime.now()
	
	def _process(self, string):
		output = []
		data = string.split()
		data1 = float(data[2])
		output.append(data1)
		if self.no_sensors == 2:
			data2 = float(data[4])
			output.append(data2)		
		return(output) 

	def write(self, string):
	# This does not write if not enough time has passed.
		now = datetime.datetime.now()
		if ((now - self.last_time) > self.beebotte_interval):
			self.last_time = now
			data_pts = self._process(string)
			if len(data_pts) == 1:
				try:
					self.test_variable.write(data_pts[0])
					self.logger.info('Write to beebotte OK')
				except:
					self.logger.warning("Error saving to beebotte. Value="+str(data_pts[0]))				
					return(False)
			if len(data_pts) == 2:
				try:
					self.test_variable.write(data_pts[0])
					self.test_variable2.write(data_pts[1])
					self.logger.info('Write to beebotte OK')
				except:
					self.logger.warning("Error saving to beebotte. Value="+str(data_pts[0]))				
					return(False)
		else:
			return(False)
		return(True)

	def read(self, count = 1):
		bee = self.test_variable.read(limit = 1)[0]
		if count == 1:
			return(bee['data'])
		if count == 2:
			bee1 = self.test_variable2.read(limit = 1)[0]
			return(bee['data'], bee1['data'])
	
if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.INFO)
	logging.warning('Running mybeebotte as a standalone app.')
	print 'Writing test value to beebotte and reading it back.'
	myBeebotte = Mybeebotte(interval = 1, no_sensors = 2)	# Beware!!! Writes every minute.
	myBeebotte.write('16:15 0 10.5 1 12.5')		# Test value
	print 'Wrote'
	print 'Read:', myBeebotte.read(2)