#!/usr/bin/python
# mybeebotte.py
# To get beebotte working....
#$ sudo apt-get install python-setuptools
#$ sudo easy_install pip
#$ sudo pip install beebotte

from beebotte import *
import logging, datetime
import keys

LOGFILE = 'log/mybeebotte.log'

class Mybeebotte():
	def __init__(self, interval = 2):	# default data interval is 2 mins
		self.logger = logging.getLogger(__name__)
		try:
			api = BBT(keys.beebotte_api_key, keys.beebotte_secret_key)
			self.test_variable = Resource(api,keys.beebotte_channel,keys.beebotte_variable)
#			self.test_variable = api.get_variable(keys.ubidots_bench_variable_key)
			self.logger.info('Beebotte initialised.')
		except:
			self.logger.error('Beebotte failed to initialise.')
		self.ubidots_interval = datetime.timedelta(minutes = interval)
		self.last_time = datetime.datetime.now()
		
	def write(self, val):
		now = datetime.datetime.now()
		if ((now - self.last_time) > self.ubidots_interval):
			self.last_time = now
			try:
				self.test_variable.write(val)
#				self.logger.info('Write to beebotte:'+now.strftime('%H:%M'))
				self.logger.info('Write to beebotte OK')
			except:
				self.logger.warning("Error saving to beebotte. Value="+str(val))				
				return(False)
		return(True)

	def read(self):
		bee = self.test_variable.read(limit = 1)[0]
		return(bee['data'])
	
if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.INFO)
	logging.warning('Running mybeebotte as a standalone app.')
	print 'Writing test value to beebotte and reading it back.'
	myBeebotte = Mybeebotte(0)	# Beware!!! Writes with each write call.
	myBeebotte.write(11)		# Test value
	print 'Wrote value 12'
	print 'Read:', myBeebotte.read()