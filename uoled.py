#!/usr/bin/python
# uoled.py
# My routines for writing to the micro oled.
# This calls on info from guyc at py-gaugette on github and raspi.tv.
# First, enable the spi bus using sudo raspi-config
# GPIO docs are here...
# https://pypi.python.org/pypi/RPi.GPIO
# http://raspi.tv/2015/rpi-gpio-new-feature-gpio-rpi_info-replaces-gpio-rpi_revision

import gaugette.ssd1306
import time

# Setup which pins we are using to control the oled
RESET_PIN = 15
DC_PIN    = 16
# Using a 5x8 font
ROW_HEIGHT = 8
ROW_LENGTH = 20
NO_OF_ROWS = 4


class Screen:
	''' Class to control the micro oled based on the gaugette routines.
		The row numbering starts at 1.
		Calling writerow does not display anything. Also need to call display.
		'''
	def __init__(self):
		self.MySsd = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
		self.MySsd.begin()
		self.MySsd.clear_display()
		self.font_size = 2		# = 1 for small font
		self.toggle = False
		self.cloud_error = False
		
	def _toggle_indicator(self):
		if self.toggle == False:
			self.toggle = True
#			self.display.writerow(1,' ')
#			return(0)
		else:
			self.toggle = False
#		self.MySsd.draw_pixel(127,30,self.toggle)
		self.draw_blob(126,29,self.toggle)
		self.MySsd.draw_pixel(127,31,self.cloud_error)
		
	def scroll_text(self,rownumber,text):
		''' So far just scrolls one row.'''
#		print 'Scrolling row number ',rownumber
		x = 0
		y = ROW_HEIGHT * rownumber-1
		i = 0
		time.sleep(1)
		while i < len(text)-ROW_LENGTH:
			todraw = '{: <20}'.format(text[i:])
			self.MySsd.draw_text2(x,y,todraw,1)
			self.MySsd.display()
			i += 1
		time.sleep(1)
		return(0)
	
	def writerow(self,rownumber,string):
		self.MySsd.draw_text2(0,((rownumber)*ROW_HEIGHT)*self.font_size,string,self.font_size)
		self.MySsd.display()
		return(0)

	def _writerow(self,rownumber,string):
		self.MySsd.draw_text2(0,(rownumber)*ROW_HEIGHT,string,1)
		return(0)
	
	def write_temperatures(self, rownumber, current, max, min, cloud_error):
		current_string = '{0:2.1f}C  '.format(current)
		max_string = '{0:2.1f}C    '.format(max)
		min_string = '{0:2.1f}C    '.format(min)
		self.MySsd.draw_text2(0,((rownumber)*ROW_HEIGHT)*self.font_size, current_string, self.font_size)
		self.MySsd.draw_text2(64,((rownumber)*ROW_HEIGHT)*self.font_size, max_string, 1)
		self.MySsd.draw_text2(64,((rownumber)*ROW_HEIGHT)*self.font_size + 8, min_string, 1)
		self._toggle_indicator()
		cloudx = 110
		cloudy = 29
#		cloud_error = True
		self.draw_cloud(cloudx, cloudy, cloud_error)
		clock = time.strftime("%R")
		self.MySsd.draw_text2(100, 0, clock, 1)
		self.MySsd.draw_text2(100, 8, '          ', 1)	# empty
		self.MySsd.display()
		return(0)
	
	def draw_cloud(self,x,y, state = True):
#		self.MySsd.draw_pixel(x,y, state)
		self.MySsd.draw_pixel(x+1,y, state)
		self.MySsd.draw_pixel(x+2,y, state)
		self.MySsd.draw_pixel(x+3,y, state)
		self.MySsd.draw_pixel(x+4,y, state)
		self.MySsd.draw_pixel(x+5,y, state)
		self.MySsd.draw_pixel(x+6,y, state)
		self.MySsd.draw_pixel(x+7,y, state)
		self.MySsd.draw_pixel(x+8,y, state)
		self.MySsd.draw_pixel(x+9,y, state)
#		self.MySsd.draw_pixel(x+10,y, state)
		self.MySsd.draw_pixel(x,y-1, state)
		self.MySsd.draw_pixel(x+1,y-2, state)
		self.MySsd.draw_pixel(x+2,y-2, state)
		self.MySsd.draw_pixel(x+3,y-3, state)
		self.MySsd.draw_pixel(x+4,y-4, state)
		self.MySsd.draw_pixel(x+4,y-4, state)
		self.MySsd.draw_pixel(x+5,y-4, state)
		self.MySsd.draw_pixel(x+6,y-4, state)
		self.MySsd.draw_pixel(x+7,y-3, state)
		self.MySsd.draw_pixel(x+8,y-2, state)
		self.MySsd.draw_pixel(x+9,y-2, state)
		self.MySsd.draw_pixel(x+10,y-1, state)
		return(0)

	def draw_blob(self,x,y, state = True):
		self.MySsd.draw_pixel(x,y, state)
		self.MySsd.draw_pixel(x+1,y, state)
		self.MySsd.draw_pixel(x,y+1, state)
		self.MySsd.draw_pixel(x+1,y+1, state)
		return(0)
		
	def cleardisplay(self):
		self.MySsd.clear_display()
		return(0)
				
	def display(self):
		self.MySsd.display()
		return(0)
	
	def test(self):
		self.writerow(1,'Test')
#		self.display()
		return(0)
		
	def info(self):
		return(NO_OF_ROWS, ROW_LENGTH)
		
if __name__ == "__main__":
	print 'Uoled test'		
	MyScreen = Screen()
	MyScreen.test()
	