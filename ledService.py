from flask import Flask, render_template, request, jsonify, json, url_for
import datetime
import time
import multiprocessing as mp
from neopixel import *
import argparse
import signal
import sys

POISON_PILL = "STOP"

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
LED_COUNT      = 37      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!)dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

# Define functions which animate LEDs in various ways.
# attempting to allow multiprocess via this post : https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
def colorWipe(strip, color):
	# Change color of the pixel strip
        # Check queue for POISON_PILL, just to delete it
        if ( in_queue.qsize() > 0):
                #lets throw that POISON_PILL away
                ick = in_queue.get()
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
	strip.show()
        return None

def theaterChase(strip, color, wait_ms=50):
        # Movie theater light style chaser animation
        while True:
                for q in range(3):
                        # Check queue for POISON_PILL
                        if ( in_queue.qsize() > 0):
                                ick = in_queue.get()
                                if ick == POISON_PILL:
                                #time to exit this function
                                break  
                        for i in range(0, strip.numPixels(), 3):
                                strip.setPixelColor(i+q, color)
                        strip.show()
                        time.sleep(wait_ms/1000.0)
                        for i in range(0, strip.numPixels(), 3):
                                strip.setPixelColor(i+q, 0)
        return None 

@app.route('/led', methods=['GET', 'POST'])
@app.route('/echo', methods = ['GET', 'POST'])
def ledRequest():
        if request.method == 'GET':
                return "OK\nMethod: GET\n"

        elif request.method == 'POST':
                content = request.json
                red = int(content['red'])
                green = int(content['green'])
                blue = int(content['blue'])
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
                if content['ledFunction'] == "colorWipe":
                        # Create NeoPixel object with appropriate configuration.
                        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
                        strip.begin()
                        # this only runs once, so not started as parallel process
                        colorWipe(strip, Color(red, green, blue))  # wipe strip with color
                        print "here in colorwipe"
                elif content['ledFunction'] == "theaterChase":
                        # Create NeoPixel object with appropriate configuration.
                        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
                        strip.begin()
                        # this is run as a parallel process as it will continuously upate
                        worker = mp.Process(theaterChase(strip, Color(red, green, blue)))  # chase strip with color
                        worker.start()
                        print "here in theaterchase"

        #print content['ledFunction']
        #print content['ledSection']
        return "OK\nMethod: POST\n"

if __name__ == "__main__":
        # Configure multiprocessing
        manager = multiprocessing.Manager()
        in_queue = manager.Queue()
        pool = multiprocessing.Pool()
        app.run(host='0.0.0.0', port=80, debug=True)
