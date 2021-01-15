#!/bin/sh
# Alarm functions
# Currently just used to identify whether we are between two times.

import time

MINHOUR = 6		# 6
MINMINUTE = 30		# 30
MAXHOUR = 23		# 22
MAXMINUTE = 00		# 30

class Alarm():
	def __init__(self):
		self.minhour = MINHOUR
		self.minminute = MINMINUTE
		self.maxhour = MAXHOUR
		self.maxminute = MAXMINUTE
		self.minsecs = (self.minhour * 60) + self.minminute
		self.maxsecs = (self.maxhour * 60) + self.maxminute
		print ('Alarm. Min:{0:2d}:{1:02d} Max:{2:2d}:{3:02d}'.format(self.minhour,self.minminute,self.maxhour,self.maxminute))

	def alarm_interval(self):
		# Return True if daytime.
		timearray = list(time.localtime())
		hour = timearray[3]
		minute = timearray[4]
		nowsecs = (hour * 60) + minute
#		print (nowsecs, self.minsecs)
		if nowsecs >= self.minsecs:
			if nowsecs < self.maxsecs:
#				print ("## Alarm running ##")
				return(True)
			else:
				return(False)
		return(False)
		
	def nighttime(self):
		timearray = list(time.localtime())
		hour = timearray[3]
		minute = timearray[4]
		nowsecs = (hour * 60) + minute
		if nowsecs <= self.minsecs or nowsecs >= self.maxsecs:
#			print ("## Night time ##")
			return(True)
		return(False)
	
	def alarmtime(self):
		return('{0:2d}:{1:02d}-{2:2d}:{3:02d}'.format(self.minhour,self.minminute,self.maxhour,self.maxminute))
		
		