#!/usr/bin/python
# myubidots.py
# To get ubidots working....
#$ sudo apt-get install python-setuptools
#$ sudo easy_install pip
#$ sudo pip install ubidots

from ubidots import ApiClient
import logging, datetime
import keys

LOGFILE = 'log/myubidots.log'

class Myubidots():
	def __init__(self, interval = 2):
		self.logger = logging.getLogger(__name__)
		# Ubidots Create an "API" object and variable object
		try:
			api = ApiClient(keys.ubidots_api_key)
			self.test_variable = api.get_variable(keys.ubidots_bench_variable_key)
			self.logger.info('Ubidots initialised.')
		except:
			self.logger.error('Ubidots failed to initialise.')
		self.ubidots_interval = datetime.timedelta(minutes = interval)
		self.last_time = datetime.datetime.now()
		
	def write(self, val):
		now = datetime.datetime.now()
		if ((now - self.last_time) > self.ubidots_interval):
			self.last_time = now
			try:
				self.test_variable.save_value({'value':val})
#				self.logger.info('Write to ubidots:'+now.strftime('%H:%M'))
				self.logger.info('Write to ubidots OK')
			except:
				self.logger.warning("Error saving to ubidots. Value="+str(val))				
				return(False)
		return(True)

if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.INFO)
	logging.warning('Running ubidots as a standalone app.')
	print 'Writing test value to ubidots'
	myUbidots = Myubidots(0)	# Beware!!! Writes all the time.
	myUbidots.write(12)		# Test value
	print 'Wrote value 12'
	