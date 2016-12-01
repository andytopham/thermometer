#!/bin/sh
# Alarm functions
# Currently just used to identify whether we are between two times.

import time

class Alarm:

	def __init__(self):
		self.minhour = 6
		self.minminute = 30
		self.maxhour = 22
		self.maxminute = 30
		self.minsecs = (self.minhour * 60) + self.minminute
		self.maxsecs = (self.maxhour * 60) + self.maxminute
		print 'Alarm. Min:{0:2d}:{1:2d} Max:{2:2d}:{3:2d}'.format(self.minhour,self.minminute,self.maxhour,self.maxminute)

		
	def alarm_interval(self):
		timearray = list(time.localtime())
		hour = timearray[3]
		minute = timearray[4]
		nowsecs = (hour * 60) + minute
		if nowsecs > self.minsecs:
			if nowsecs < self.maxsecs:
#				print "## Alarm ##"
				return(1)
			else:
				return(0)
		
		
		