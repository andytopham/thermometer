#!/usr/bin/python
# uoledada.py. Updated 1/1/21.
# SSD1306 driver based on info from adafruit at:
# https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage
# also check:
# https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/blob/master/examples/ssd1306_pillow_text.py
# Needs:
# sudo apt-get install python3-pip
# sudo pip3 install adafruit-circuitpython-ssd1306
# sudo apt-get install python3-pil

import time
import Adafruit_GPIO.SPI as SPI
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

ROW_HEIGHT = 24
# CHAR_HEIGHT = 12
#CHAR_HEIGHT = 40
#SMALL_HEIGHT = 8
#ROW_SPACE = 4
# ROW_SPACE = 8
#ROW_HEIGHT = CHAR_HEIGHT + ROW_SPACE
#ROW_LENGTH = 20
#NO_OF_ROWS = 4
PATH = '/home/pi/master/therm/'

class Screen:
	''' Class to control the micro oled based on the adafruit routines.
		The row numbering starts at 1.
		Calling writerow does not display anything. Also need to call display.
		'''
	def __init__(self):
		print ('Starting uoledada.py')
		# Create the I2C interface.
		i2c = busio.I2C(SCL, SDA)
		# The first two parameters are the pixel width and pixel height.
		self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
		# Clear display.
		self.disp.fill(0)
		self.disp.show()
		# Create blank image for drawing.
		# Make sure to create image with mode '1' for 1-bit color.
		width = self.disp.width
		height = self.disp.height
		self.image = Image.new("1", (width, height))
		# Get drawing object to draw on image.
		self.draw = ImageDraw.Draw(self.image)
		# Draw a black filled box to clear the image.
		self.draw.rectangle((0, 0, width, height), outline=0, fill=0)
		# Load default font.
#		self.font = ImageFont.load_default()
		self.font = ImageFont.truetype('/home/pi/master/therm/slkscr.ttf', ROW_HEIGHT)
		
		self.draw.text((0, 0), "uoledada.py AT ", font=self.font, fill=255)
		string = time.strftime("%H:%M:%S")
		self.draw.text((0, ROW_HEIGHT), string, font=self.font, fill=255)
		# Display image.
		self.disp.image(self.image)
		self.disp.show()		
		# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
		# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# 		self.font = ImageFont.truetype(PATH+'fonts/Hack-BoldItalic.ttf', 25)
#		self.font = ImageFont.truetype(PATH+'fonts/Hack-BoldItalic.ttf', CHAR_HEIGHT)
#		self.fontsmall = ImageFont.truetype(PATH+'fonts/Hack-BoldItalic.ttf', SMALL_HEIGHT)
	
	def scroll_text(self,rownumber,text):
		''' So far just scrolls one row.'''
#		print ('Scrolling row number ',rownumber)
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
		
	def clear(self):
		width = self.disp.width
		height = self.disp.height
		self.image = Image.new('1', (width, height))
		# Get drawing object to self.draw on image.
		self.draw = ImageDraw.Draw(self.image)
		# Draw a black filled box to clear the image.
		self.draw.rectangle((0,0,width,height), outline=0, fill=0)	
		return(0)
			
	def clear_row(self, rownumber):
		width = self.disp.width
		height = rownumber*ROW_HEIGHT
		# Draw a black filled box to clear the image.
		self.draw.rectangle((0,height,width,height+ROW_HEIGHT), outline=0, fill=0)	
		return(0)

	def writerow(self,rownumber, string, fontsize="normal"):
#		print ("writerow:", rownumber, string)
		self.clear_row(rownumber)
		if fontsize == "normal":
			thisfont=self.font
		else:
			thisfont=self.fontsmall
		self.draw.text((2,(rownumber)*ROW_HEIGHT), string, font=thisfont, fill=255)
		self.display()
		return(0)
		
	def display(self):
		# Display image.
		self.disp.image(self.image)
		self.disp.show()
		return(0)
	
	def test(self):
		self.clear()
		x = 0
		top = -2
		string = time.strftime("%H:%M:%S")
		string2 = time.strftime("%d %b %Y")
		self.draw.text((x, 0), "uoledada.py",  font=self.font, fill=255)
		self.draw.text((x, ROW_HEIGHT), string,  font=self.font, fill=255)
		self.draw.text((x, ROW_HEIGHT * 2), string2,  font=self.font, fill=255)
		self.disp.image(self.image)
		self.disp.show()
		return(0)
		
	def info(self):
		return(NO_OF_ROWS, ROW_LENGTH)
		
if __name__ == "__main__":
	print ('Uoled test')		
	MyScreen = Screen()
	while True:
		MyScreen.test()
		time.sleep(1)