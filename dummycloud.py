#!/usr/bin/python
# dummycloud.py

import logging, datetime
LOGFILE = 'log/dummycloud.log'
VALUEFILE = '/home/pi/master/thermometer/log/values.log'

class Mydummycloud():
	def __init__(self, interval = 2):
		self.logger = logging.getLogger(__name__)
		self.logger.info('Dummy cloud initialised.')
		self.cloud_interval = datetime.timedelta(minutes = interval)
		self.last_time = datetime.datetime.now()

	def _log_temp(self, temperature):
		self.fp = open(VALUEFILE,'w')	
		self.fp.write(str(temperature)+'\n')
		self.fp.close
		return(0)
		
	def write(self, val):
		now = datetime.datetime.now()
		if ((now - self.last_time) > self.cloud_interval):
			self.last_time = now
			try:
				print 'Dummy cloud write:', val
				self.logger.info('Write to dummycloud OK')
				self._log_temp(val)
			except:
				self.logger.warning("Error saving to dummycloud. Value="+str(val))				
				return(False)
		return(True)	
		
if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.INFO)
	logging.warning('Running dummycloud as a standalone app.')
	print 'Writing test value to dummycloud'
	myDummy = Mydummycloud()	# Beware!!! Writes all the time.
	myDummy.write(12)		# Test value
	print 'Wrote value 12'
	