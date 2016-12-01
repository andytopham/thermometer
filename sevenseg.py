#!/usr/bin/python
# 7seg.py
# routines to drive the sparkfun i2c 7 segment display
# This is the syntax:  bus.write_byte_data(address,register,value)
# Or, to read values back:  value =  bus.read_byte_data(address,register) 
# to get i2c working, remove i2c from the blacklist file.
# Then add i2c-dev to /etc/modules
# sudo adduser pi i2c
# then reboot
# sudo i2cdetect -y 1    --- will show the map of detected devices

import DS18B20, myubidots
import time
import smbus
import logging
import datetime
 
address = 0x20 			# i2C address of MCP23017
sevensegaddress=0x77	# i2c address of 7segment display
# this address above can get changed by sw glitch. It started at 0x71.
#registera = 0x12
#registerb = 0x13
# decide how bright we want it
defaultbrightness=255
#constants for the sparkfun 7 seg dsplay
cleardisplay=0x76		#followed by nothing
decimalcontrol=0x77		#followed by 0-63
cursorcontrol=0x79		#followed by 0-3
brightnesscontrol=0x7A	#followed by 0-255
digit1control=0x7B
digit2control=0x7C
digit3control=0x7D
digit4control=0x7E
baudrateconfig=0x7F
i2caddressconfig=0x80
factoryreset=0x81
LOGFILE = '/home/pi/master/7seg/log/7seg.log'

class Sevenseg:
	'''7 segment control.'''
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		bus = smbus.SMBus(1) # 0 for revision 1 Raspberry Pi, change to bus = smbus.SMBus(1) for revision 2.
		self.ioerrorcount = 0
		try:
			bus.write_byte(sevensegaddress,cleardisplay)
			bus.write_byte_data(sevensegaddress,decimalcontrol,16)	#draw colon
			time.sleep(.1)
			bus.write_byte(sevensegaddress,0)
			time.sleep(.1)
			bus.write_byte(sevensegaddress,1)
			time.sleep(.1)
			bus.write_byte(sevensegaddress,2)
			time.sleep(.1)
			bus.write_byte(sevensegaddress,3)
		except IOError:
			self.ioerrorcount = self.ioerrorcount + 1
			self.logger.warning('IO error in init')

	def updateclock(self):
		timenow=list(time.localtime())
		hour=timenow[3]
		minute=timenow[4] 
		self.logger.info("updating clock"+str(timenow))
		try:  
			bus.write_byte(sevensegaddress,cleardisplay)
			bus.write_byte_data(sevensegaddress,decimalcontrol,16)	#draw colon
			bus.write_byte(sevensegaddress,int(hour/10))
			bus.write_byte(sevensegaddress,hour%10)
			bus.write_byte(sevensegaddress,int(minute/10))
			bus.write_byte(sevensegaddress,minute%10)
			return(0)
		except IOError:
			self.ioerrorcount = self.ioerrorcount + 1
			# need to reset cursor position when this happens
			self.logger.warning('update_clock:error writing to 7seg display')
			time.sleep(1)
			bus.write_byte(sevensegaddress,cleardisplay)
			time.sleep(1)
			return(1)

	def write_temp(self,value):
		'''Value is a float.'''
		intvalue = int(value)
		firstdec = int(10 * (value - intvalue))
		try:  
			bus.write_byte(sevensegaddress,cleardisplay)
			bus.write_byte(sevensegaddress,intvalue/10)
			bus.write_byte(sevensegaddress,intvalue%10)
			bus.write_byte(sevensegaddress,firstdec)
			bus.write_byte(sevensegaddress,0x63)
			bus.write_byte_data(sevensegaddress,decimalcontrol, 2)	# decimal point
		except IOError:
			self.ioerrrocount = self.ioerrorcount + 1
			self.logger.warning('write_temp:error writing to 7seg display')
			
	def dimdisplay(self,brightness):
	  # max brightness=255
		try:  
			bus.write_byte_data(sevensegaddress,brightnesscontrol,brightness)
		except IOError:
			self.ioerrorcount = self.ioerrorcount + 1
		
  ##The start of the real code ##
if __name__ == "__main__":
	logging.basicConfig(filename=LOGFILE,filemode='w',level=logging.WARNING)
	logging.warning(datetime.datetime.now().strftime('%d %b %H:%M')+". Running 7seg class as a standalone app")

	print "Running 7seg class as a standalone app"
	my7seg = Sevenseg()
	myDS = DS18B20.DS18B20()
	myDots = myubidots.Ubidots()
	time.sleep(2)		#let the board settle down
	i = 0
	while True:
		if my7seg.updateclock() == 0:
			my7seg.dimdisplay(defaultbrightness)
			time.sleep(3)
			temp = myDS.read_temp()
#			logging.info("Temperature:"+str(temp))
			my7seg.write_temp(temp)
			if i > 5:		# every 2 mins
				myDots.write(temp)
				i = 0
			i += 1
		time.sleep(17)
		