from flask import Flask, render_template, request, jsonify, json, url_for
import datetime
import time
import multiprocessing as mp
from neopixel import *
import argparse
import signal
import sys
import random

POISON_PILL = "STOP"
firstRun = True
worker = True

app = Flask(__name__)

def signal_handler(signal, frame):
        colorWipe(strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 67      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!)dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
LED_Ring_Low   = 0
LED_Ring_High  = 23
LED_Strip_Low  = 24
LED_Strip_High = 37     # This should match the LED_COUNT variable

# Define functions which animate LEDs in various ways.
# attempting to allow multiprocess via this post : https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
def happyFace(strip, color):
	# Change color of the pixel strip
	while True:
		# Setup the initial smilie face
		strip.setPixelColor(5, color)
		strip.setPixelColor(22, color)
		for i in range(10,17):
			strip.setPixelColor(i, color)
		strip.setPixelColor(5, color)
		strip.show()
		while True:
        		# Check for POISON_PILL and exit if there is one
			if poisonPill():
				return None
			# Lets do some random winks
			winkCheck = random.randrange(1,150)
			if (winkCheck == 1):
				strip.setPixelColor(5, Color(0,0,0))
				strip.setPixelColor(16, Color(0,0,0))
				strip.setPixelColor(17, Color(0,0,0))
				strip.setPixelColor(9, color)
				strip.show()
				time.sleep(1.5)
				strip.setPixelColor(5, color)
				strip.setPixelColor(9, Color(0,0,0))
				strip.setPixelColor(16, color)
				strip.setPixelColor(17, color)
				strip.show()	
			time.sleep(.1)
	return None

def colorWipe(strip, color):
	# Change color of the pixel strip
        # Check for POISON_PILL and exit if there is one
        if poisonPill():
                return None
        for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
        strip.show()
        return None

def theaterChase(strip, color, wait_ms=50):
        # Movie theater light style chaser animation
        while True:
                for q in range(3):
                        # Check for POISON_PILL and exit if there is one
                        if poisonPill():
                                return None
                        for i in range(0, strip.numPixels(), 3):
                                strip.setPixelColor(i+q, color)
                        strip.show()
                        time.sleep(wait_ms/1000.0)
                        for i in range(0, strip.numPixels(), 3):
                                strip.setPixelColor(i+q, 0)
        return None 

def poisonPill():
        # Check queue for POISON_PILL
        if ( in_queue.qsize() > 0):
                ick = in_queue.get()
		if ick == "STOP":
	                # time to die
                        return True
                else:
                        return False

@app.route('/led', methods=['GET', 'POST'])
def ledRequest():
        global firstRun
        global worker
        if request.method == 'POST':
                content = request.json
                red = int(content['red'])
                green = int(content['green'])
                blue = int(content['blue'])
                section = content['section']
                        
                #dont check for workers on first time through - variable not defined
                if (firstRun == False):	
                        # is there a worker subprocess out there?
                        if worker.is_alive():
                                # seems we have one
                                in_queue.put(POISON_PILL)
                                while worker.is_alive():
                                        # wait for it to take POISON_PILL
                                        time.sleep(0.1)
                        if not worker.is_alive():
                                # if worker is dead
                                worker.join(timeout=1.0)

                # Create NeoPixel object with appropriate configuration.
                strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
                strip.begin()
                if content['ledFunction'] == "happyFace":
                        # this is run as a parallel process as it will continuously upate
                        worker = mp.Process(target=happyFace, args=(strip, Color(red, green, blue)))  # chase strip with color
                        worker.start()
                        # print "here in colorwipe"
                if content['ledFunction'] == "colorWipe":
                        # this is run as a parallel process as it will continuously upate
                        worker = mp.Process(target=colorWipe, args=(strip, Color(red, green, blue)))  # chase strip with color
                        worker.start()
                        # print "here in colorwipe"
                elif content['ledFunction'] == "theaterChase":
                        # this is run as a parallel process as it will continuously upate
                        worker = mp.Process(target=theaterChase, args=(strip, Color(red, green, blue)))  # chase strip with color
                        worker.start()
                        # print "here in theaterchase"
        firstRun = False
        return "OK\nMethod: POST\n"

if __name__ == "__main__":
        # Configure multiprocessing
        in_queue = mp.Queue()
        app.run(host='0.0.0.0', port=80, debug=True)
