#!/usr/bin/python
# graphtest.py
# Testing graphing routines.

import uoled, logging
#import os, logging, glob, time, sys
#import alarm, DS18B20, system
#import keys
 
LOGFILE = '/home/pi/master/thermometer/log/graphtest.log'
VALUEFILE = '/home/pi/master/thermometer/log/values.bak'

class Graphtest():
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		print 'Setting up uoled'
		self.display = uoled.Screen()
		
	def process(self):
		self.fp = open(VALUEFILE,'r')
		data = 'test'
		sensor = []
		data = self.fp.readline()		# discard title row
		while data <> '':
			data = self.fp.readline()
			if data <> '':
				data2 = data.split()
				data3 = float(data2[2])
#				print 'Output', data3
				sensor.append(int(data3))
		self.fp.close
		return(sensor)
		
	def draw(self, data):
		self.display.draw_graph(data)
		return(0)
	
		
if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.WARNING)
	logging.warning('Running graphtest.')

	print 'Starting graphtest'
	myTest = Graphtest()
	myTest.draw(myTest.process())

	
	