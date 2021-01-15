#!/usr/bin/python
# Jan 2021
# newtft.py
# My routines for writing to the 2.2" TFT.
# This calls on newer info from Adafruit at:
# https://learn.adafruit.com/adafruit-2-8-and-3-2-color-tft-touchscreen-breakout-v2/python-usage

import digitalio
import board
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import RPi.GPIO as GPIO
import sys
import time
import adafruit_rgb_display.ili9341 as ili9341
import alarm
import pwm
import system
import threading
from queue import Queue

BAUDRATE = 24000000		# Config for display baudrate (default max is 24mhz)
BIGFONTSIZE = 48		# was 96
SMALLFONTSIZE = 24
protoboard = True
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)
BLACK = (0,0,0)
BLUE = (0,0,255)
SPI_PORT = 0
SPI_DEVICE = 0
# Using a 5x8 font
FONT_DIR = '/home/pi/master/fonts/'
ROW_HEIGHT = 8
ROW_LENGTH = 10				# 20 is normal
DEFAULT_FONT_SIZE = 64		# 24 is normal
NO_OF_ROWS = 12				# 12 is normal
ROW_LENGTH = 17
LAST_PROG_ROW = 5
BIG_ROW = 1
# gpio pin definitions
L_BUTTON = 19
R_BUTTON = 4
HOSTNAMEROW = 0
TESTING = True

class Screen(threading.Thread):
	def __init__(self, rowcount = NO_OF_ROWS, rowlength = ROW_LENGTH, rotation = 90):
		self.Event = threading.Event()
		self.threadLock = threading.Lock()
		threading.Thread.__init__(self, name='mytft')
		self.q = Queue(maxsize=12)
		self.rowcount = rowcount+1
		self.rowlength = rowlength
		self.last_prog_row = LAST_PROG_ROW
		self.rotation = rotation

		# Setup which pins we are using to control the hardware display
		if protoboard:
		# These are for the 2.2" tft soldered onto proto board.
			cs_pin = digitalio.DigitalInOut(board.CE0)
			dc_pin = digitalio.DigitalInOut(board.D18)		
			reset_pin = digitalio.DigitalInOut(board.D23)	
		else:				# wired tft
			cs_pin = digitalio.DigitalInOut(board.CE0)
			dc_pin = digitalio.DigitalInOut(board.D17)		
			reset_pin = digitalio.DigitalInOut(board.D23)

		# Setup SPI bus using hardware SPI:
		spi = board.SPI()
		self.disp = ili9341.ILI9341(spi, rotation=0,cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)
		if self.disp.rotation % 180 == 90:
			height = self.disp.width   # we swap height/width to rotate it to landscape!
			width = self.disp.height
		else:
			width = self.disp.width   # we swap height/width to rotate it to landscape!
			height = self.disp.height

		self.image = Image.new("RGB", (width, height)) 	# Draw and text
		self.draw = ImageDraw.Draw(self.image)				# Get drawing object to draw on image.
		# Load a TTF Font
		self.big_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", BIGFONTSIZE)
		self.time_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", SMALLFONTSIZE)

#		self.disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
#		self.disp.begin()
#		self.disp.clear()	# black
		self.old_text = [' ' for i in range(self.rowcount)]	# used for clearing oled text
#		self.font = ImageFont.load_default()
#		self.font = ImageFont.truetype('binary/morningtype.ttf',FONTSIZE)
#		self.font = ImageFont.truetype('binary/secrcode.ttf',FONTSIZE)
#		self.font = ImageFont.truetype('binary/DS-DIGI.TTF',FONTSIZE)
#		self.font = [ImageFont.load_default() for i in range(self.rowcount)]
#		self.fontsize = [DEFAULT_FONT_SIZE for i in range(self.rowcount)]
#		self.fontsize[BIG_ROW] = 36
#		if TESTING:
#			self.fontsize[2] = 24
#			self.fontsize[3] = 24
#		for i in range(self.rowcount):
#			self.font[i] = ImageFont.truetype(FONT_DIR+'Hack-Regular.ttf',self.fontsize[i])
		# setup row colours
		self.rowcolour = [WHITE for i in range(self.rowcount)]			# set the defaults
		self.rowcolour[0] = YELLOW
#		self.rowcolour[self.rowcount-1] = BLUE
#		self.calc_offsets()
#		GPIO.setmode(GPIO.BCM)
#		GPIO.setup(LED,GPIO.OUT)
#		pi_pwm=GPIO.PWM(LED,100)		# pin number, frquency
#		pi_pwm.start(100)				# duty cycle
#		GPIO.setup(L_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#		GPIO.setup(R_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		self.myalarm = alarm.Alarm()
		self.mypwm = pwm.PWM()
		self.mysystem = system.System()
#		self.fill_screen()
		
	def run(self):
		print ('Starting tft queue manager.')
		myevent = False
		while not myevent:
			while not self.q.empty():
				entry = self.q.get()
				self.writerow(entry[0], entry[1])	
				self.q.task_done()
			myevent = self.Event.wait(.5)	# wait for this timeout or the flag being set.
		print ('Tft exiting')
		
	def clear(self):
#		self.led.clear_display() # This clears the display but only when there is a led.display() as well!
		time.sleep(.5)
#		self.led.display()
		time.sleep(1)		# this really is needed!

	def small_display_update(self, x=0, y=0):
		# to speed things up, just update a fraction of the display.
		screen_width = 240
		x1 = screen_width-1
		y1 = y + DEFAULT_FONT_SIZE-1
		self.disp.set_window(x,y,x1,y1)
		pixelbytes = list(TFT.image_to_data(self.disp.buffer))
		self.disp.data(pixelbytes)					# actually write the data.
		return(0)
		
	def info(self):
		return(self.rowcount, self.rowlength)
		
	def write_button_labels(self, next = False, stop = False):
		if next:
			self.writerow(self.rowcount-1, '****         Stop')
		if stop:
			self.writerow(self.rowcount-1, 'Next         ****')
		else:		# back to normal
			self.writerow(self.rowcount-1, 'Next         Stop')
		return(0)
		
	def write_radio_extras(self, clock, temperature):
		self.writerow(self.rowcount-2,'{0:5s}   {1:7.1f}^C'.format(clock,float(temperature)))		
		return(0)
		
	def _draw_rotated_text(self, image, text, position, angle, font, fill=WHITE):
		# Get rendered font width and height.
		draw = ImageDraw.Draw(image)
		width, height = draw.textsize(text, font=font)
		# Create a new image with transparent background to store the text.
		textimage = Image.new('RGBA', (width, height), (0,0,0,0))
		# Render the text.
		textdraw = ImageDraw.Draw(textimage)
		textdraw.text((0,0), text, font=font, fill=fill)
		# Rotate the text image.
		rotated = textimage.rotate(angle, expand=1)
		# Paste the text into the image, using it as a mask for transparency.
		image.paste(rotated, position, rotated)

	def scroll_text(self,rownumber,text):
		''' So far just scrolls one row.'''
#		print 'Scrolling row number ',rownumber
		x = 0
		y = ROW_HEIGHT * rownumber-1
		i = 0
		time.sleep(1)
		while i < len(text) - self.rowlength:
			todraw = '{: <20}'.format(text[i:])
			self.MySsd.draw_text2(x,y,todraw,1)
			self.MySsd.display()
			i += 1
		time.sleep(1)
		return(0)
	
	def writerow(self, rownumber, string, clear=True):
		'''Now runs from row 0.'''
		thisfont = self.font[rownumber]
		if clear == True:
			self._draw_rotated_text(self.disp.buffer, self.old_text[rownumber], (self.xpos[rownumber], self.ypos[rownumber]), self.rotation, thisfont, fill=BLACK)
		self._draw_rotated_text(self.disp.buffer, string, (self.xpos[rownumber], self.ypos[rownumber]), self.rotation, thisfont, fill=self.rowcolour[rownumber])
		self.old_text[rownumber] = string
		self.display()
#		self.small_display_update(self.xpos[rownumber], self.ypos[rownumber])		
		return(0)

	def calc_offsets(self):
		self.xpos = [0 for i in range(self.rowcount)]
		self.ypos = [0 for i in range(self.rowcount)]
		if self.rotation == 0:
			for i in range(1, self.rowcount):
				self.ypos[i] = self.ypos[i-1] + self.fontsize[i-1]
		else:
			for i in range (1, self.rowcount):
				self.xpos[i] = self.xpos[i-1] + self.fontsize[i-1]
		return(0)
		
	def draw_blob(self,x,y):
		self.MySsd.draw_pixel(x,y,True)
#		self.MySsd.draw_pixel(x+1,y,True)
#		self.MySsd.draw_pixel(x,y+1,True)
#		self.MySsd.draw_pixel(x+1,y+1,True)
		return(0)
		
	def delete_blob(self,x,y):
		self.MySsd.draw_pixel(x,y,False)
#		self.MySsd.draw_pixel(x+1,y,True)
#		self.MySsd.draw_pixel(x,y+1,True)
#		self.MySsd.draw_pixel(x+1,y+1,True)
		return(0)
		
	def write_counter(self):
		x = 0
		for x in range(100):
			self.writerow(5, str(x), True)
			self.display()
			time.sleep(1)
			
	def button_test(self):
		if GPIO.input(L_BUTTON):
			self.writerow(self.rowcount-2, 'Left button true', True)
		else:
			self.writerow(self.rowcount-2, 'Left button false', True)
		if GPIO.input(R_BUTTON):
			self.writerow(self.rowcount-1, 'Right button true', True)
		else:
			self.writerow(self.rowcount-1, 'Right button false', True)
#			self.display()

	def draw_image(self):
		if disp.rotation % 180 == 90:
			height = disp.width   # we swap height/width to rotate it to landscape!
			width = disp.height
		else:
			width = disp.width   # we swap height/width to rotate it to landscape!
			height = disp.height
		image = Image.new('RGB', (width, height))	# Make sure to create image with mode 'RGB' for full color.
		draw = ImageDraw.Draw(image)				# Get drawing object to draw on image.
		draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))	# Draw a black filled box to clear the image.
		disp.image(image)
		image = Image.open("blinka.jpg")
		# Scale the image to the smaller screen dimension
		image_ratio = image.width / image.height
		screen_ratio = width / height
		if screen_ratio < image_ratio:
			scaled_width = image.width * height // image.height
			scaled_height = height
		else:
			scaled_width = width
			scaled_height = image.height * width // image.width
		image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
		# Crop and center the image
		x = scaled_width // 2 - width // 2
		y = scaled_height // 2 - height // 2
		image = image.crop((x, y, x + width, y + height))
		disp.image(image)	
	
	def show_time(self):
		for i in range(3,self.rowcount-2):
			self.writerow(i, 'Row '+str(i), True)	
		while True:
			date_now = time.strftime("%b %d %Y ", time.localtime())
			time_now = time.strftime("%H:%M:%S", time.localtime())
			self.writerow(1, time_now, True)	
			self.writerow(3, date_now, True)
#			self.button_test()
			time.sleep(1)
		return(0)
	
	def fill_screen(self):
		# Draw Some Text
		print ("fill screen")
		date_now = time.strftime("%b %d %Y ", time.localtime())
		time_now = time.strftime("%H:%M", time.localtime())
		(time_width, time_height) = self.time_font.getsize(time_now)
		(date_width, date_height) = self.date_font.getsize(date_now)
		row= SMALLFONTSIZE * 5
		self.newwriterow(5, time_now)
#		self.draw.text((0, row), time_now, font=self.time_font, fill=WHITE)
		row += SMALLFONTSIZE
		self.draw.text((0, row), date_now, font=self.date_font, fill=WHITE)
		row = HOSTNAMEROW
		hostname = self.mysystem.hostname()
		atime = self.myalarm.alarmtime()
		self.draw.text((0, row), hostname+"    "+atime, font=self.date_font, fill=WHITE)
		self.disp.image(self.image)

	def regular_updates(self):
		while True:
			if self.myalarm.nighttime():
				self.mypwm.dull()
			else:
				self.mypwm.bright()
			time_now = time.strftime("%H:%M:%S", time.localtime())
			row= SMALLFONTSIZE * 5
			self.draw.text((0, row), time_now, font=self.time_font, fill=WHITE)
			self.disp.image(self.image)
			time.sleep(1)
			# delete old text by drawing black version
			self.draw.text((0, row), time_now, font=self.time_font, fill=BLACK)
	
	
	def newwriterow(self, rownumber, string, clear=True, bigfont=False):
		'''Now runs from row 0.'''
		if bigfont:
			thisfont = self.big_font
		else:
			thisfont = self.time_font
		if clear == True:
			self.draw.text((0, rownumber*SMALLFONTSIZE), self.old_text[rownumber], font=thisfont, fill=BLACK)
		self.draw.text((0, rownumber*SMALLFONTSIZE), string, font=thisfont, fill=WHITE)
		self.old_text[rownumber] = string
		self.disp.image(self.image)
		return(0)
		
	def display(self):
		self.disp.display()
		return(0)

if __name__ == "__main__":
	print ("TFT control using new adafruit code")
	myScreen = Screen()
	myScreen.fill_screen()			
	myScreen.regular_updates()