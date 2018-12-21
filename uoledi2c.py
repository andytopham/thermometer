#!/usr/bin/python
# uoledi2c.py
# SSD1306 driver based on info from adafruit at:
# https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black/usage

import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = 14
DC = 15
SPI_PORT = 0
SPI_DEVICE = 0


RESET_PIN = 14
DC_PIN    = 15
# Using a 5x8 font
# ROW_HEIGHT = 8
# CHAR_HEIGHT = 12
CHAR_HEIGHT = 40
SMALL_HEIGHT = 8
ROW_SPACE = 4
# ROW_SPACE = 8
ROW_HEIGHT = CHAR_HEIGHT + ROW_SPACE
ROW_LENGTH = 20
NO_OF_ROWS = 4

PATH = '/home/pi/master/'

class Screen:
	''' Class to control the micro oled based on the gaugette routines.
		The row numbering starts at 1.
		Calling writerow does not display anything. Also need to call display.
		'''
	def __init__(self):
		print 'Starting uoledi2c.py'
		self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)  
		self.disp.begin()
		self.disp.clear()
		self.disp.display()
		# Create blank image for drawing. Create image with mode '1' for 1-bit color.
		width = self.disp.width
		height = self.disp.height
		self.image = Image.new('1', (width, height))
		# Get drawing object to draw on image.
		self.draw = ImageDraw.Draw(self.image)
		# Draw a black filled box to clear the image.
		self.draw.rectangle((0,0,width,height), outline=0, fill=0)
		# Load default font.
#		self.font = ImageFont.load_default()
		# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
		# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# 		self.font = ImageFont.truetype(PATH+'fonts/Hack-BoldItalic.ttf', 25)
		self.font = ImageFont.truetype(PATH+'fonts/Hack-BoldItalic.ttf', CHAR_HEIGHT)
		self.fontsmall = ImageFont.truetype(PATH+'fonts/Hack-BoldItalic.ttf', SMALL_HEIGHT)
		# Write two lines of text.
		x = 2
		top = 2
		self.draw.text((x, top), 'uoledada setup',  font=self.font, fill=255)
		# Display image.
		self.disp.image(self.image)
		self.disp.display()
	
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
		
	def clear(self):
		width = self.disp.width
		height = self.disp.height
		self.image = Image.new('1', (width, height))
		# Get drawing object to draw on image.
		self.draw = ImageDraw.Draw(self.image)
		# Draw a black filled box to clear the image.
		self.draw.rectangle((0,0,width,height), outline=0, fill=0)	
		return(0)
			
#	def writerow(self,rownumber,string):
#		self.MySsd.draw_text2(0,(rownumber)*ROW_HEIGHT,string,1)
#		return(0)

	def clear_row(self, rownumber):
		width = self.disp.width
		height = rownumber*ROW_HEIGHT
#		self.image = Image.new('1', (width, height))
		# Get drawing object to draw on image.
#		self.draw = ImageDraw.Draw(self.image)
		# Draw a black filled box to clear the image.
		self.draw.rectangle((0,height,width,height+ROW_HEIGHT), outline=0, fill=0)	
		return(0)

	def writerow(self,rownumber, string, fontsize="small"):
		if rownumber > NO_OF_ROWS-1:
			rownumber = NO_OF_ROWS-1		# crunch all up onto last row
		self.clear_row(rownumber)
		if fontsize == "normal":
			thisfont=self.font
		else:
			thisfont=self.fontsmall
		self.draw.text((2,(rownumber)*ROW_HEIGHT), string, font=thisfont, fill=255)
#		self.draw.text((2, 2), string, font=self.font, fill=255)
		self.display()
		return(0)
		
	def display(self):
		self.disp.image(self.image)
		self.disp.display()
		return(0)
	
	def test(self):
		self.clear()
		x = 2
		top = 2
		string = time.strftime("%H:%M:%S")
		string2 = time.strftime("%d %b")
		self.draw.text((x, top), string,  font=self.font, fill=255)
		self.draw.text((x, top+40), string2,  font=self.font, fill=255)
		self.display()
		return(0)
		
	def info(self):
		return(NO_OF_ROWS, ROW_LENGTH)
		
if __name__ == "__main__":
	print 'Uoled test'		
	MyScreen = Screen()
	while True:
		MyScreen.test()
		time.sleep(1)