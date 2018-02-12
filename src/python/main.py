#!/usr/bin/env python



# FOR ANDROID

import bluetooth

print("performing inquiry...")

nearby_devices = bluetooth.discover_devices(duration=2, lookup_names=True,
                                            lookup_class=False)

print("found %d devices" % len(nearby_devices))

for addr, name in nearby_devices:
    print("  %s - %s" % (addr, name))
    

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import v_conf
from v_conf import SPRAY_IN_PARALLEL, PRU_ENABLE

X_BASE = v_conf.X_BASE
Y_BASE = v_conf.Y_BASE
DRIVE_L_START_DISTANCE = v_conf.DRIVE_L_START_DISTANCE
DRIVE_R_START_DISTANCE = v_conf.DRIVE_R_START_DISTANCE
S_STEP_DISTANCE = v_conf.S_STEP_DISTANCE
D_STEP_DISTANCE = v_conf.D_STEP_DISTANCE
L_STEP_DISTANCE = v_conf.L_STEP_DISTANCE
SPRAY_TIME = v_conf.SPRAY_TIME
SVG_RATIO = v_conf.SVG_RATIO

X_SIZE = v_conf.X_SIZE
Y_SIZE = v_conf.Y_SIZE
X_0 = v_conf.X_0
Y_0 = v_conf.Y_0

LOG = v_conf.LOG

PRU_ENABLED = v_conf.PRU_ENABLE
DRIVE_IN_PARALLEL = v_conf.DRIVE_IN_PARALLEL
SPRAY_IN_PARALLEL = v_conf.SPRAY_IN_PARALLEL


#-------------------
#X_BASE = 4000#1400 # distance between drives (width) [mm]
#Y_BASE = 1400 # distance between drives and ground (height) [mm], only limitation, all parameters are calculated from X_BASE

#DRIVE_L_START_DISTANCE = 2500#1100 #X_BASE # initial distance for drive A [mm]
#DRIVE_R_START_DISTANCE = 2500#1100 #X_BASE # initial distance for drive B [mm]

#SPRAY_TIME = 0.13 # 0.15#0.2#1#0.1


#S_STEP_DISTANCE = 5 #10 #10 # static step distance [mm], for passive drive 
#D_STEP_DISTANCE = 5 # 10 #10 # dynamic step distance [mm], for active drive 

#L_STEP_DISTANCE = 10 #step for curve drawings [mm]
#--------------------

SPRAY_D = 5# 1 #0.5 # spray diameter for simulation (outputMap)

#print sys.path

#_GPIO_ = False
_GPIO_ = True

_SPRAY_ = False #real spray or draw square

_PYGAME_ = False
PYGAME_RATIO = 0.5

#SVG_RATIO = 0.75#0.5#fish 1#0.5
#SVG_RATIO = 5.6 #calibr1.svg
#_PYGAME_ = True 


import v_tension




import thread
import sys
import math
from os import walk
import time
import select
from PIL import Image, ImageDraw, ImageFont
import datetime
from threading import Thread




def conf():
    global PRU_ENABLE
    global DRIVE_IN_PARALLEL
    global SPRAY_IN_PARALLEL
    global _GPIO_
    PRU_ENABLE = v_conf.conf("> Enable PRU?", PRU_ENABLE)
    DRIVE_IN_PARALLEL = v_conf.conf("> Enable drive in parallel?", DRIVE_IN_PARALLEL)
    SPRAY_IN_PARALLEL = v_conf.conf("> Enable spray in parallel?", SPRAY_IN_PARALLEL)
    
_GPIO_ = v_conf.conf("> Enable GPIO?", _GPIO_)

conf()

#print PRU_ENABLE
#print DRIVE_IN_PARALLEL
#print SPRAY_IN_PARALLEL

#if raw_input("> Enable PRU? (y/N): ") == "y":
#    print "> PRU enabled"
#    PRU_ENABLE = True

#if raw_input("> Enable drive in parallel? (Y/n): ") == "n":
#    print "> Drive in parallel disabled"
#    DRIVE_IN_PARALLEL = False

#if raw_input("> Enable spray in parallel? (Y/n): ") == "n":
#    print "> Spray in parallel disabled"
#    SPRAY_IN_PARALLEL = False
    
if LOG:
    logFile = open('log.csv', 'w+')
    logFile.write('drive;time;i/o;time;steps;time/steps\n')

#if raw_input("> Press y to enable PYGAME?: ") == "y":
#    print "> PYGAME enabled"
#    _PYGAME_ = True

#if raw_input("> Press n to disable GPIO?: ") == "n":
#    _GPIO_ = False

_SPRAY_ = True
#if raw_input("> Press n to disable real SPRAY (no draw square)?: ") == "n":
#    _SPRAY_ = False
    #L_STEP_DISTANCE = 10 #step for curve drawings [mm] in spray mode

if _GPIO_:
    try:
    
        #if PRU_ENABLE:
        import pru.moveStepper as moveStepper
        #import RPi.GPIO as GPIO  
        import Adafruit_BBIO.GPIO as GPIO  
        import Adafruit_BBIO.PWM as PWM  
        ##import pcd8544v2.lcd as lcd
        import Adafruit_GPIO.SPI as SPI    
        import Adafruit_Nokia_LCD as LCD
    


    except:
        print "Unexpected error:", sys.exc_info()[0]
        print "> GPIO disabled"
        _GPIO_ = False     

#if _GPIO_:
		#moveStepper.init()
	
if _PYGAME_:
        import pygame

# Beaglebone Black hardware SPI config:
DC = 'P9_42'
RST = 'P9_12'
SPI_PORT = 1
SPI_DEVICE = 0
 
# Beaglebone Black software SPI config:
# DC = 'P9_15'
# RST = 'P9_12'
# SCLK = 'P8_7'
# DIN = 'P8_9'
# CS = 'P8_11'

#from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier
#from svg.path import parse_path



            


import xml.etree.ElementTree as ET
paths = []



# ---------------------------------------------------------
# settings
# ---------------------------------------------------------

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)


#in config file
#--------------
#X_SIZE = int(X_BASE * 0.4)      # X size of drawing area [mm]
#Y_SIZE = int(X_BASE * 0.25) # Y size of drawing area [mm]
#if Y_SIZE > Y_BASE:
#        Y_SIZE = Y_BASE
#        
#X_0 = int(X_BASE * 0.3) # X offset from drive L [mm]
#Y_0 = int(X_BASE * 0.25) # Y offset from drive L [mm]
#
#if Y_0 > Y_BASE:
#        print "Error: Y_BASE is lower than optimal printing area offset!"
#        exit
#--------------

#X_SIZE = 100 # X size of drawing area [mm]
#Y_SIZE = 100 # Y size of drawing area [mm]
#X_0 = 550      # X offset from drive L [mm]
#Y_0 = 800      # Y offset from drive L [mm]





DRIVE_STEP_TIME = 0.0003#0.0002 #0.00005 # step time [s]
DRIVE_STEP_ANGLE = math.pi / 800 #5650 # step angle [rad]
DRIVE_WHEEL_DIAMETER = 9.5 # 75 # wheel diameter [mm]
DRIVE_STEP_MULT = 1 #2

#H bridge setting 
 #5650 # step angle [rad]


# GPIO outputs
GPIO_DRIVE_L_DIR = 'P9_11' #25 #4 #25 #17
GPIO_DRIVE_L_PUL = 'P9_23' #12 #22 #17 #24 #22
GPIO_DRIVE_R_DIR = 'P9_13' #27 #4 #23 #23
GPIO_DRIVE_R_PUL = 'P9_15' #'P9_14' #17 #22 #24
GPIO_SPRAY = 'P9_41' #18
GPIO_TIME2 = 0.00065#0.00026 #time per step set 0, set 1

# calculated values
D_SIZE = int(math.sqrt((X_SIZE ** 2) + (Y_SIZE ** 2))) # drawing area diagonal size
D_0 = int(math.sqrt((X_0 ** 2) + (Y_0 ** 2))) # distance to X0, Y0 from L; minimal distance
D_1 = int(math.sqrt(((X_SIZE + X_0) ** 2) + ((Y_SIZE + Y_0) ** 2))) # distance to Xmax, Ymax; maximal distance
D_2 = int(math.sqrt(((X_SIZE + X_0) ** 2) + (Y_0 ** 2))) # distance  to X0, Y0 from R

DRIVE_STEP_DISTANCE = (DRIVE_STEP_ANGLE / DRIVE_STEP_MULT) * DRIVE_WHEEL_DIAMETER

# ---------------------------------------------------------
# DRIVE HW
# ---------------------------------------------------------
class driveHW:
        l = 0
        pinDIR = 0
        pinPUL = 0
        invDIR = False
        name = None
        
        def __init__ (self, name, l, pinDIR, pinPUL, invDIR):
                self.l = l
                self.pinDIR = pinDIR
                self.pinPUL = pinPUL
                self.invDIR = invDIR
                self.name = name
		
		#GPIO.output(pinPUL, True);

                
        def driveMoveGPIO(self, steps, pinDIR, pinPUL, stepTime = DRIVE_STEP_TIME):
            #print self.name + ' step time: ' + str(stepTime) + ' steps: ' + str(steps)
            
            tin = time.time()
            if LOG:
                global logFile
                logFile.write(self.name + ';' + str(tin) + ';i\n')
            if _GPIO_:
                stepTime = stepTime / 2 
                
                #return
                steps = int(steps)
                if steps < 0:
                        GPIO.output(pinDIR, True)
                else:
                        GPIO.output(pinDIR, False)
        	
                if PRU_ENABLE:
                    if self.name == 'R' and steps != 0:		
                        moveStepper.moveStepper_p9_15(abs(steps))		
                    if self.name == 'L' and steps != 0:		
                        moveStepper.moveStepper_p9_23(abs(steps))
                else:		
                    for i in range(0, abs(steps)):
                        #print i
                        GPIO.output(pinPUL, False)
                        time.sleep(stepTime)
                        GPIO.output(pinPUL, True)
                        time.sleep(stepTime)
			
            tout = time.time()
            if abs(steps) > 0:
                tps = str(abs((tout-tin)/steps))
            else:
                tps = '0'
				
            if LOG:
                logFile.write(self.name + ';' + str(tout) + ';o;' + str(tout-tin) + ';' + str(steps) + ';' + tps + '\n')
            return
        
        def scrollTo(self, l, stepTime = DRIVE_STEP_TIME):
                #print self.name + ' start time: ' + str(time.time())

                dl = l - self.l
                self.l = self.l + dl
                #print dl
                s = dl / DRIVE_STEP_DISTANCE
                if self.invDIR:
                        s = -s
                
                #lcdInfo()
                
                t0 =  time.time()
                self.driveMoveGPIO(s, self.pinDIR, self.pinPUL, stepTime)
                t1 =  time.time() 
                #print self.name + ' time: ' + str(t1 - t0)
         
        def getStepsTo(self, l,):
                dl = l - self.l
                self.l = self.l + dl
                #print dl
                s = dl / DRIVE_STEP_DISTANCE
                #if self.invDIR:
                #        s = -s
                return int(abs(s))    

	

# ---------------------------------------------------------
# V-PLOTTER HW
# ---------------------------------------------------------        
class v_plotterHW:
    
    driveL = driveHW('L', DRIVE_L_START_DISTANCE, GPIO_DRIVE_L_DIR, GPIO_DRIVE_L_PUL, False)      
    driveR = driveHW('R', DRIVE_R_START_DISTANCE, GPIO_DRIVE_R_DIR, GPIO_DRIVE_R_PUL, True) 
    bSpray = False
     
    @staticmethod 
    def testSpeed(mult, pin):
        if _GPIO_:
        
            t0 =  time.time()
            for i in range(0, int(mult)):
                GPIO.output(pin, True)
                GPIO.output(pin, False)
            t1 =  time.time()
            
            print '> start time:' + str(t0)
            print '> finish time:' + str(t1)
            print '> ' + str(mult) + ' cycles 1-0 in ' + str(t1 - t0)
            print '> 1 change 1-0 in ' + str((t1 - t0) / mult) 
            print '>'
                
    @staticmethod 
    def initOutputsGPIO(outputs):
        if _GPIO_:
            #GPIO.setmode(GPIO.BCM)
            print ""
            for pin in outputs:
                print "> SetOuput:", pin
                GPIO.setup(pin,GPIO.OUT)
                GPIO.output(pin, False)
               
            
            if _SPRAY_:
		GPIO.output(GPIO_SPRAY, False)
            else:            
		GPIO.output(GPIO_SPRAY, True)

     
    @staticmethod
    def init():
        v_plotterHW.initOutputsGPIO((GPIO_DRIVE_L_DIR, GPIO_DRIVE_L_PUL, GPIO_DRIVE_R_DIR, GPIO_DRIVE_R_PUL, GPIO_SPRAY))
        
	#GPIO.output(GPIO_DRIVE_L_PUL, True);
	#GPIO.output(GPIO_DRIVE_R_PUL, True);
        #global driveL
        #global driveR
        #driveL =  driveHW(DRIVE_L_START_DISTANCE, GPIO_DRIVE_L_DIR, GPIO_DRIVE_L_PUL, False)        
        #driveR = driveHW(DRIVE_R_START_DISTANCE, GPIO_DRIVE_R_DIR, GPIO_DRIVE_R_PUL, False)   

    @staticmethod
    def setOutputs(level):
        if _GPIO_:
            GPIO.output(GPIO_SPRAY, level)
            GPIO.output(GPIO_DRIVE_L_DIR, level)
            GPIO.output(GPIO_DRIVE_L_PUL, level)
            GPIO.output(GPIO_DRIVE_R_DIR, level)
            GPIO.output(GPIO_DRIVE_R_PUL, level)
    
    @staticmethod
    def sprayGPIO(t):
        if LOG:
            logFile.write('S;' + str(time.time()) + ';i\n')
        if _GPIO_:
        	if _SPRAY_:    
			GPIO.output(GPIO_SPRAY, True)
            		time.sleep(t)
			GPIO.output(GPIO_SPRAY, False)
		else:
	            	GPIO.output(GPIO_SPRAY, False)
        	    	time.sleep(t)

         
        	    	l = v_plotterHW.driveL.l
            		r = v_plotterHW.driveR.l
            		d = 2
            		v_plotterHW.scrollTo(l + d, r + d)
            		v_plotterHW.scrollTo(l + d, r - d)
            		v_plotterHW.scrollTo(l - d, r - d)
            		v_plotterHW.scrollTo(l - d, r + d)
            		v_plotterHW.scrollTo(l, r)

            		GPIO.output(GPIO_SPRAY, True)
            		time.sleep(t)

        outputMap.spray(v_plotter.getX(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + X_0, (v_plotter.getY(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + Y_0))
        pygameGui.spray(v_plotter.getX(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + X_0, (v_plotter.getY(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + Y_0))           
        #x = int(self.getX(driveL.l, driveR.l)) + X_0
        #y = int(self.getY(driveL.l, driveR.l)) + Y_0
        #d = 1
        #draw_v_tension.ellipse((x-d, y-d, x+d, y+d), fill = 'blue', outline ='blue')
        if LOG:
            logFile.write('S ;' + str(time.time()) + ';o;\n')

    @staticmethod
    def measureGPIO():
	aTime = []
	aTime.append(time.time())
	for i in range (0, 10000):
		GPIO.output(GPIO_SPRAY, False)
		#time.sleep(DRIVE_STEP_TIME)
		GPIO.output(GPIO_SPRAY, True)	    
		#time.sleep(DRIVE_STEP_TIME)
		aTime.append(time.time())
	tMax = 0.0
	tMin = 1000.0	
	for i in range (2, 10000):
		dTime =	(aTime[i] - aTime[i-1]) * 1000
		#print '{0:2d} [ms]: {1:0.2f}'.format(i, dTime)
		tMax = max(tMax, dTime)
		tMin = min(tMin, dTime)
	print '[ms] max: {0:0.2f} min: {1:0.2f} avg: {2:0.2f} '.format(tMax, tMin, (aTime[10000 - 1] - aTime[2]) / (10000 -2) * 1000)

    @staticmethod
    def scrollTo(Ll, Rl, stepTime = DRIVE_STEP_TIME):
        
        #lcdHW.displayInfo(Ll, Rl)
        #gui.printInfo(1)
        v_plotterHW.driveL.scrollTo(Ll, stepTime)
        v_plotterHW.driveR.scrollTo(Rl, stepTime)
        #print ">"
        
    @staticmethod
    def sprayGPIO2(b):
        if b != v_plotterHW.bSpray:
            if _GPIO_:
                GPIO.output(GPIO_SPRAY, b)
                time.sleep(1)
        v_plotterHW.bSpray = b
        
    @staticmethod
    def scrollToXY(x, y):
        
        Ll = int(round(v_plotter.getLl(x, y)))
        Rl = int(round(v_plotter.getRl(x, y)))
        
        #if not v_plotterHW.bSpray:
        #    outputMap.sprayLine(v_plotter.getX(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + X_0, (v_plotter.getY(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + Y_0), v_plotter.getX(Ll, Rl) + X_0, v_plotter.getY(Ll, Rl) + Y_0)
        #    pygameGui.sprayLine(v_plotter.getX(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + X_0, (v_plotter.getY(v_plotterHW.driveL.l, v_plotterHW.driveR.l) + Y_0), v_plotter.getX(Ll, Rl) + X_0, v_plotter.getY(Ll, Rl) + Y_0)
        
        #lcdHW.displayInfo(Ll, Rl)
        #gui.printInfo(1)
        #v_plotterHW.driveL.scrollTo(Ll)
        #v_plotterHW.driveR.scrollTo(Rl)
        #tL = thread.start_new_thread(v_plotterHW.driveL.scrollTo, (Ll,))
        #tR = thread.start_new_thread(v_plotterHW.driveR.scrollTo, (Rl,))
        
        dLl = abs(v_plotterHW.driveL.l - Ll)
        dRl = abs(v_plotterHW.driveR.l - Rl)
        
        stepsL = (dLl / DRIVE_STEP_DISTANCE) #* DRIVE_STEP_TIME
        stepsR = (dRl / DRIVE_STEP_DISTANCE) #* DRIVE_STEP_TIME
        
        timeL = stepsL * (GPIO_TIME2 + DRIVE_STEP_TIME)
        timeR = stepsR * (GPIO_TIME2 + DRIVE_STEP_TIME)
        
       
        #stepsTimeL = stepsL * GPIO_TIME2
        #stepsTimeR = stepsR * GPIO_TIME2
        
        #totalTimeL = stepsTimeL + timeL
        #totalTimeR = stepsTimeR + timeR
        
        #print 'L: GPIO time: ' + str(stepsTimeL) + ' steps time: ' + str(timeL) + ' total time: ' + str(totalTimeL)       
        #print 'R: GPIO time: ' + str(stepsTimeR) + ' steps time: ' + str(timeR) + ' total time: ' + str(totalTimeR)
        
        #stepsMax = max(stepsL, stepsR)
        #timeMax = max(totalTimeL, totalTimeR)
        timeMax = max(timeL, timeR)
        
        
        if stepsL > 0: 
            stepTimeL = ((timeMax - timeL) / stepsL) + DRIVE_STEP_TIME# - GPIO_TIME2 #DRIVE_STEP_TIME
            
        else:
            stepTimeL = DRIVE_STEP_TIME
        if stepsR > 0:
            stepTimeR = ((timeMax - timeR) / stepsR) + DRIVE_STEP_TIME# - GPIO_TIME2
        else:
            #stepTimeL = ((timeMax - timeL) / stepsL) + DRIVE_STEP_TIME# - GPIO_TIME2
            stepTimeR = DRIVE_STEP_TIME#((timeMax - timeR) / stepsR) + DRIVE_STEP_TIME# - GPIO_TIME2 #stepTimeR = DRIVE_STEP_TIME
           
        
        #stepTimeMultL = 1
        #stepTimeMultR = 1
        #if stepsL > 0:
        #    stepTimeMultL = (stepsMax / stepsL) / 2 
            #stepTimeMultL = ((timeMax / stepsL) / DRIVE_STEP_TIME) * 2- stepsTimeL 
        #if stepsR > 0:
        #    stepTimeMultR = (stepsMax / stepsR) / 2
            #stepTimeMultR = ((timeMax / stepsR)  / DRIVE_STEP_TIME) * 2  - stepsTimeR         
        
        #print "> L: steps: " + str(stepsL) + ' time: ' + str(stepTimeL) + ' total time: ' + str(stepTimeL * stepsL + GPIO_TIME2 * stepsL)
        #print "> R: steps: " + str(stepsR) + ' time: ' + str(stepTimeR) + ' total time: ' + str(stepTimeR * stepsR + GPIO_TIME2 * stepsR)
        #print "> L: steps: " + str(stepsL) + ' time: ' + str(stepTimeL + GPIO_TIME2) + ' total time: ' + str((stepTimeL + GPIO_TIME2) * stepsL)
        #print "> R: steps: " + str(stepsR) + ' time: ' + str(stepTimeR + GPIO_TIME2) + ' total time: ' + str((stepTimeR + GPIO_TIME2) * stepsR)
        
        
        if DRIVE_IN_PARALLEL:
        
            if not PRU_ENABLE:
                tL = Thread(target=v_plotterHW.driveL.scrollTo, args=(Ll, stepTimeL,))
                tR = Thread(target=v_plotterHW.driveR.scrollTo, args=(Rl, stepTimeR,))
                tL.start()
                tR.start()
                tL.join()
                tR.join()
            else:
                l = v_plotterHW.driveL.getStepsTo(Ll)
                r = v_plotterHW.driveL.getStepsTo(Rl)
                #print l
                #print r
                if _GPIO_:
                   moveStepper.moveStepper2(l ,r)
                
        else:
            v_plotterHW.driveL.scrollTo(Ll)
            v_plotterHW.driveR.scrollTo(Rl)
        #print ">"


# ---------------------------------------------------------
# V-PLOTTER
# ---------------------------------------------------------   
class v_plotter:
    
    #v_plotterHW = None
    #def __init__ (self, v_plotterHW):
    #    self.v_plotterHW = v_plotterHW
       
    @staticmethod    
    def getLl(x, y):
        return math.sqrt((x + X_0) ** 2 + (y + Y_0) ** 2)
        
    @staticmethod
    def getRl(x, y):
        return math.sqrt((X_0 + X_SIZE - x) ** 2 + (Y_0 + y) ** 2)      

    @staticmethod                
    def getX(Ll, Rl):
        return (((Rl ** 2) -  (Ll ** 2) - (X_SIZE ** 2)) - (2 * X_SIZE * X_0 )) / ((-2 * X_SIZE) - (4 * X_0))

    @staticmethod
    def getY(Ll, Rl):
        l2 = (Ll ** 2) - ((v_plotter.getX(Ll, Rl) + X_0 ) ** 2)
        if l2 <= 0:
            return -1
        else:
            return math.sqrt(l2) - Y_0
        

    @staticmethod
    def getPixel(x, y, rgbImage, colorLimit):
        width, height = rgbImage.size
        x = int(float(x) / (float(X_SIZE) / float(width)))
        y = int(float(y) / (float((Y_SIZE) / float(height))))
        x = min(x, width - 1)
        y = min(y, height - 1)
        r, g, b = rgbImage.getpixel((x, y))
        l = (r, g, b)
        c = sum(l) / len(l)
        #print r, g, b
        #if r < limit or g < limit or b < limit:
        if c < colorLimit:
                return True
        else:
                return False
    @staticmethod           
    def calibrate():
        v_plotterHW.scrollTo(DRIVE_L_START_DISTANCE, DRIVE_R_START_DISTANCE)
        for x in range (0, X_SIZE + 1, 100):
            for y in range (0, Y_SIZE + 1, 100):
                Ll = int(v_plotter.getLl(x, y))
                Rl = int(v_plotter.getRl(x, y))
                v_plotterHW.scrollTo(Ll, Rl)
                v_plotterHW.sprayGPIO(SPRAY_TIME) 
                
                #outputMap.spray(x + X_0, y + Y_0)
                #pygameGui.spray(x + X_0, y + Y_0)
                
                gui.printInfo(1)
                if raw_input("> press Enter to continue, 0 for exit: "):
                    print "> stopping from calibrating"
                    return
    
    @staticmethod           
    def calibrateLines():
        o = 0
        try:
           o = int(int(raw_input("> set X_0 test offset (0 - 0.3) * 10: ")) * 0.1 * X_BASE) 
        except:
            o = 0
        v_plotterHW.sprayGPIO2(True)      
        v_plotterHW.scrollToXY(0, 0)
        v_plotterHW.sprayGPIO2(False)
        
        x = 0
        y = 0   
        s =  int(L_STEP_DISTANCE * 0.2)   
        for x in range (0, X_SIZE, s):
            v_plotterHW.scrollToXY(x, y)
        for y in range (0, Y_SIZE, s):
            v_plotterHW.scrollToXY(x, y)
        for x in range (X_SIZE, 0, -s):
            v_plotterHW.scrollToXY(x, y) 
        for y in range (Y_SIZE, 0, -s):
            v_plotterHW.scrollToXY(x, y)   
            
        return
        #o = int(X_BASE * 0.2)
        for x in range (0, -o, -s):
            v_plotterHW.scrollToXY(x, y)
        for y in range (0, Y_SIZE, s):
            v_plotterHW.scrollToXY(x, y)
        for x in range (-o, X_SIZE + o, s):
            v_plotterHW.scrollToXY(x, y)
        for y in range (Y_SIZE, 0, -s):
            v_plotterHW.scrollToXY(x, y) 
        for x in range (X_SIZE + o, 0, -s):
            v_plotterHW.scrollToXY(x, y)  
        
        v_plotterHW.sprayGPIO2(True)   
        
        
    @staticmethod                                    
    def vPlottL(rgbImage, colorLimit):
        for Ll in xrange(D_0, D_1 + 1, S_STEP_DISTANCE):
            for Rl in xrange(D_1, D_0 -1, -D_STEP_DISTANCE):
                                              
                    if heardEnter():
                        gui.printInfo(1)
                        if raw_input("> vPlottL paused, 0 for exit: ") == "0":
                            print "> stopping from vPlottR"
                            return
                        
                    x = int(v_plotter.getX(Ll, Rl))
                    if x >= 0 and x < X_SIZE:
                        y = int(v_plotter.getY(Ll, Rl))
                        if y >= 0 and y < Y_SIZE:
                            if v_plotter.getPixel(x, y, rgbImage, colorLimit):
                                v_plotterHW.scrollTo(Ll, Rl)
                                
                                if SPRAY_IN_PARALLEL:
                                    tS = Thread(target=v_plotterHW.sprayGPIO, args=(SPRAY_TIME,))
                                    tS.start()
                                else:
                                    v_plotterHW.sprayGPIO(SPRAY_TIME)
                                #pygame.draw.circle(window, WHITE, (x + X_0, y + Y_0), 1)
                                #pygameGui.spray(x + X_0, y + Y_0)
                                #if _PYGAME_:
                                #    pygame.draw.circle(window, WHITE, (), 1)
                                #    pygame.display.flip() 
                                #else:
                                    #if _PYGAME_:
                                        #pygame.draw.circle(window, BLUE, (x + X_0, y + Y_0), 1) 
                                        #pygame.display.flip() 
                                  

    @staticmethod
    def vPlottR(rgbImage, colorLimit):
        for Rl in xrange(D_0, D_1 + 1, S_STEP_DISTANCE):
                for Ll in xrange(D_1, D_0 -1, -D_STEP_DISTANCE):
                    
                    if heardEnter():
                        gui.printInfo(1)
                        if raw_input("> vPlottR paused, 0 for exit: ") == "0":
                            print "> stopping from vPlottR"
                            return

                    x = int(v_plotter.getX(Ll, Rl))
                    if x >= 0 and x < X_SIZE:
                        y = int(v_plotter.getY(Ll, Rl))
                        if y >= 0 and y < Y_SIZE:
                            if v_plotter.getPixel(x, y, rgbImage, colorLimit):
                                v_plotterHW.scrollTo(Ll, Rl)
                                
                                if SPRAY_IN_PARALLEL:
                                    tS = Thread(target=v_plotterHW.sprayGPIO, args=(SPRAY_TIME,))
                                    tS.start()
                                else:
                                    v_plotterHW.sprayGPIO(SPRAY_TIME)
                                
                                #pygameGui.spray(x + X_0, y + Y_0)    
                                #if _PYGAME_:
                                #    pygame.draw.circle(window, WHITE, (x + X_0, y + Y_0), 1)
                                #pygame.display.flip() 
                                #else:
                                    #if _PYGAME_:
                                        #pygame.draw.circle(window, BLUE, (x + X_0, y + Y_0), 1)
                                        #pygame.display.flip() 
                                                                                                                                
    @staticmethod
    def vPlott(rgbImg, colorLimitL, colorLimitR):
        v_plotter.vPlottL(rgbImg, colorLimitL)
        #self.vPlottR(rgbImg, colorLimitR)
 
      
    @staticmethod
    def vPlottSVG(paths):
        for path in paths:
        #print path
            
            #x = X_0
            #y = Y_0
			
            l =  path.length(error=1e-5) * SVG_RATIO
					
            for i in range(0, int(l), L_STEP_DISTANCE):
                if heardEnter():
                        gui.printInfo(1)
                        print("> vPlottSVGlines paused")
                        print("> 0 for exit")
                        print("> 1 for setting")
                        inp = raw_input("> Select option: ")
                        if inp == "0":
                            print "> stopping from vPlottSVGlines"
                            return
                        if inp == "1":
                            gui.displayMenu()
                #
                #print "."
                point = path.point(i / l)
                print str(point)#(str(point.real) + ', ' + str(point.imag))
                v_plotterHW.scrollToXY(point.real * SVG_RATIO, point.imag * SVG_RATIO)
                
                #v_plotterHW.scrollToXY(x, y)
                #x = x + 10 				
                #y = y + 10				
                if SPRAY_IN_PARALLEL:
                    tS = Thread(target=v_plotterHW.sprayGPIO, args=(SPRAY_TIME,))
                    tS.start()
                else:
                    v_plotterHW.sprayGPIO(SPRAY_TIME)
            
            
            
    @staticmethod
    def vPlottSVGlines(paths):
       

        for path in paths:
        #print path
            v_plotterHW.sprayGPIO2(True)
            
            #time.sleep(1)
            l =  path.length(error=1e-5) * SVG_RATIO
            for i in range(0, int(l)):
                if heardEnter():
                        gui.printInfo(1)
                        print("> vPlottSVGlines paused")
                        print("> 0 for exit")
                        print("> 1 for setting")
                        inp = raw_input("> Select option: ")
                        if inp == "0":
                            print "> stopping from vPlottSVGlines"
                            return
                        if inp == "1":
                            gui.displayMenu()
                #v_plotterHW.sprayGPIO2(True)
                print path.point(i / l)
                point = path.point(i / l)
                v_plotterHW.scrollToXY(point.real * SVG_RATIO, point.imag * SVG_RATIO)
                        
            
                v_plotterHW.sprayGPIO2(False)
                
        v_plotterHW.sprayGPIO2(True)       
        
# ---------------------------------------------------------
# LCD
# ---------------------------------------------------------
class lcdHW:
    disp = None   
    image = None
    draw = None
    font = None

    @staticmethod
    def init(): 
        if _GPIO_:
            #lcd.init()
            #lcd.cls()
            ##lcd.backlight(ON)
            #lcd.gotorc(0,0)
            #lcd.text("v-plotter")

		lcdHW.disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
		lcdHW.disp.begin(contrast=60)
		lcdHW.disp.clear()
		lcdHW.disp.display()
		
		# Make sure to create image with mode '1' for 1-bit color.
		lcdHW.image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
		# Get drawing object to draw on image.
		lcdHW.draw = ImageDraw.Draw(lcdHW.image)
		# Draw a white filled box to clear the image.
		#draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
		# Load default font.
		lcdHW.font = ImageFont.load_default()
		# Alternatively load a TTF font.
		# Some nice fonts to try: http://www.dafont.com/bitmap.php
		#lcdHW.font = ImageFont.truetype('Minecraftia.ttf', 8)
		#lcdHW.font = ImageFont.load("arial.pil")
		

	
        
    @staticmethod
    def displayInfo(Ll, Rl):
        #return 
        if _GPIO_:
                #lcd.gotorc(1,0)
                #lcd.text("              ")
                #lcd.gotorc(1,0)
                #lcd.text("L [mm]: " + str(Ll))
                #lcd.gotorc(2,0)
                #lcd.text("              ")
                #lcd.gotorc(2,0)
                #lcd.text("R [mm]: " + str(Rl))
                #lcd.gotorc(3,0)
                #lcd.text("              ")
                #lcd.gotorc(3,0)
                #lcd.text("X [mm]: " + str(int(v_plotter.getX(Ll, Rl))))
                #lcd.gotorc(4,0)
                #lcd.text("              ")
                #lcd.gotorc(4,0)
                #lcd.text("Y [mm]: " + str(int(v_plotter.getY(Ll, Rl))))
                # Create blank image for drawing.
                
		lcdHW.draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
		#lcdHW.draw.ellipse((2,2,22,22), outline=0, fill=255)
		lcdHW.draw.text((0,0), 'v_plotter', font=lcdHW.font)
		lcdHW.draw.text((0,10), 'Ll: ' + str(Ll) , font=lcdHW.font)
		lcdHW.draw.text((0,20), 'Rl: ' + str(Rl) , font=lcdHW.font)
		lcdHW.disp.image(lcdHW.image)
  		lcdHW.disp.display()
  	
  	
    @staticmethod
    def displayInfo1():
        #return 
        if _GPIO_:
               
                
		lcdHW.draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
		lcdHW.draw.ellipse((2,2,12,12), outline=0, fill=255)
		lcdHW.draw.ellipse((LCD.LCDWIDTH - 14,2,LCD.LCDWIDTH - 2,12), outline=0, fill=255)
		lcdHW.draw.line((7,7,int(LCD.LCDWIDTH / 2) ,30), fill=0)

		lcdHW.draw.line((LCD.LCDWIDTH -7,7,int(LCD.LCDWIDTH / 2) ,30), fill=0)		
		lcdHW.draw.text((12,30), 'v_plotter', font=lcdHW.font)
		lcdHW.disp.image(lcdHW.image)
  		lcdHW.disp.display()
  		
    @staticmethod
    def cls():
        #return 
        if _GPIO_:
	  lcdHW.disp.clear()
	  lcdHW.disp.display()
# ---------------------------------------------------------
# GUI
# ---------------------------------------------------------
class gui:
    

  
        
        
    
    @staticmethod
    def printInfo(option = 0):
        if option == 0:
            print
            #print 
            print "> Info"
            print "X_BASE # distance between drives (width) [mm]:            ", X_BASE
            print "Y_BASE # distance between drives and ground (height) [mm]:", Y_BASE
            print "X_0 # X offset from drive L [mm]:                         ", X_0
            print "Y_0 # Y offset from drive L [mm]:                         ", Y_0
            print "X_SIZE # X size of drawing area [mm]:                     ", X_SIZE
            print "Y_SIZE # X size of drawing area [mm]:                     ", Y_SIZE
            print "D_SIZE # drawing area diagonal size[mm]:                  ", D_SIZE
            print "D_0 # distance to X0, Y0 from L [mm]:                     ", D_0
            print "D_1 # distance to Xmax, Ymax from L [mm]:                 ", D_1
            print "D_2 # distance  to X0, Y0 from R [mm]:                    ", D_2
            print
            print "PRU_ENABLE:                                               ", PRU_ENABLE
            print "DRIVE_IN_PARALLEL:                                        ", DRIVE_IN_PARALLEL
            print "SPRAY_IN_PARALLEL:                                        ", SPRAY_IN_PARALLEL
            print
            print "SPRAY_TIME [ms]:                                          ", SPRAY_TIME
            print "L_STEP_DISTANCE:                                          ", L_STEP_DISTANCE
        print
        print "L [mm]:         ", v_plotterHW.driveL.l
        print "R [mm]:         ", v_plotterHW.driveR.l
        print "X from X_0 [mm]:", int(v_plotter.getX(v_plotterHW.driveL.l, v_plotterHW.driveR.l))
        print "Y from Y_0 [mm]:", int(v_plotter.getY(v_plotterHW.driveL.l, v_plotterHW.driveR.l))
        print

    @staticmethod
    def displayMenu():
            global DRIVE_STEP_TIME
            global DRIVE_STEP_DISTANCE
            global DRIVE_STEP_ANGLE
            global DRIVE_WHEEL_DIAMETER
            global DRIVE_STEP_MULT
            global GPIO_TIME2
        #if _PYGAME_:
        #    for event in pygame.event.get(): 
        #        if event.type == pygame.QUIT: 
        #                #sys.exit(0) 
        #                break
            print
            print
            print ">--------------------------------"
            print "0 - exit"        
            print "1 - info"
            print "2 - calibrate dots"
            print "3 - home"
            print "4 - goto"
            print "5 - gotoXY"
            print "6 - plott"
            print "7"
            print "8 - reset outputMap"
            print "9 - save outputMap"
            print "10 - save log"
            print "11 - draw tension outputMap"
            print
            print "12 - GPIO False"
            print "13 - GPIO True"
            print
            print "14 - plottSVG"
            print "15 - plottSVGlines"
            print "16 - calibrate lines"
            print "17 - test speed"
            print "18 - set drive step delay"
            print "19 - set H bridge sub steps"
            print "20 - gotoXY L&R parallel"
            print "21 - measure GPIO (spray output)"
            print
            print "30 - config HW"
            print "31 - config draw setting"
            
            
            print
        
            try:
                displayMenu = int(raw_input("> Select option: "))
            except:
                return
        
            if displayMenu == 0:
                print "> Go home [mm] L: ", DRIVE_L_START_DISTANCE, "R: ", DRIVE_R_START_DISTANCE
                print "> Exit"
                return 0
        
            if displayMenu == 1:
                gui.printInfo()
        
            if displayMenu == 2:
                print "> Calibrate, print dots grid"
                v_plotter.calibrate()
                
            if displayMenu == 3:
                print "> Go home [mm] L: ", DRIVE_L_START_DISTANCE, "R: ", DRIVE_R_START_DISTANCE
                v_plotterHW.scrollTo(DRIVE_L_START_DISTANCE, DRIVE_R_START_DISTANCE)
                
            if displayMenu == 4:
                gui.printInfo()
                
                print
                try:
                        Ll = int(raw_input("> Distance from L [mm]: "))
                except:
                        Ll = v_plotterHW.driveL.l
                try:
                        Rl = int(raw_input("> Distance from R [mm]: "))
                except:
                        Rl = v_plotterHW.driveR.l
                        
                if Ll + Rl < math.sqrt((X_BASE * 0.5) ** 2  + (X_BASE * 0.25) ** 2) * 2:
                    print "> Distance is shorter than X_BASE, not allowed!"
                    return   
                
                if Ll < D_0 or Rl < D_0:
                        try:
                                if raw_input("> Distance is outside area, y to continue: ") != "y":
                                        return
                        except:
                                pass
                
                print  "> Goto [mm] L =", Ll, " R =", Rl
                v_plotterHW.scrollTo(Ll, Rl)
                
            if displayMenu == 5:
                gui.printInfo()
                
                print
                try:
                        x = int(raw_input("> X from X_0 [mm]: "))
                except:
                        x = int(v_plotter.getX())
                try:
                        y = int(raw_input("> Y from Y_0 [mm]: "))
                except:
                        y = int(v_plotter.getX())
                        
                Ll = int(v_plotter.getLl(x, y))
                Rl = int(v_plotter.getRl(x, y))
                
                if Ll + Rl < math.sqrt((X_BASE * 0.5) ** 2  + (X_BASE * 0.25) ** 2) * 2:
                    print "> Distance is shorter than X_BASE, not allowed!"
                    return            
                
                if Ll < D_0 or Rl < D_0:
                        try:
                                if raw_input("> Distance is outside area, y to continue: ") != "y":
                                        return
                        except:
                                pass
                print  "> Goto [mm] X =", x, " Y =", y
                
                print  "> Goto [mm] L =", Ll, " R =", Rl
                v_plotterHW.scrollTo(Ll, Rl)    
                
            
                
            if displayMenu == 6:
                
                filename = inputPattern.getFilename('./data') 
                if filename == 0:
                    return
                
                
      
                outputMap.init()
                pygameGui.reset()
                print
                print "> Plott"
                print "> Press Enter to pause"
                
                v_plotter.vPlott(inputPattern.getImage(filename), 150, 150)
                
            if displayMenu == 11:
                outputMap.calculate()
        
            if displayMenu == 8:
                outputMap.init()
                pygameGui.reset()
            
            if displayMenu == 9:
                #fileName = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_v.png"
                fileName = "v.png"
                outputMap.save(fileName)
                #print "> File created: "+ fileNamePrefix + "_" + v_tensionFileName
                print "> File saved: " + fileName

            if displayMenu == 10:
                #fileName = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_v.png"
                if LOG:
                    global logFile
                    logFile.close()
                    logFile = open('log.csv', 'a+')
                    logFile.write('drive;time;i/o;time;steps;time/steps\n')
                    print "> Log saved"
                else:
                    print "> Log is disabled in v_conf"

            if displayMenu == 11:
                fileName = "v_tension.png"
                v_tension.setup(fileName, X_BASE, Y_BASE)
                v_tension.draw()
                outputMap.init()
            
            
            if displayMenu == 12:
                v_plotterHW.setOutputs(False)

            if displayMenu == 13:
                v_plotterHW.setOutputs(True)
                
            if displayMenu == 14:
                
                filename = inputPatternSVG.getFilename('./data-svg') 
                if filename == 0:
                    return
                
                outputMap.init()
                pygameGui.reset()
                v_plotter.vPlottSVG(inputPatternSVG.getSVGpaths(filename))
                
            if displayMenu == 15:
                
                filename = inputPatternSVG.getFilename('./data-svg') 
                if filename == 0:
                    return
                
                outputMap.init()
                pygameGui.reset()
                v_plotter.vPlottSVGlines(inputPatternSVG.getSVGpaths(filename))
                
            if displayMenu == 16:
                v_plotter.calibrateLines()
                
            if displayMenu == 17:
                #v_plotterHW.testSpeed(1000, GPIO_DRIVE_R_DIR)
                
                n = 10000
                l = n * DRIVE_STEP_DISTANCE
                print '> drive step distance: ' + str(DRIVE_STEP_DISTANCE) + ' l: ' + str(l)
                if (v_plotterHW.driveL.l - l) > D_0:
                    dl =  v_plotterHW.driveL.l - l
                else:
                    dl =  v_plotterHW.driveL.l + l
                t0 = time.time()
                v_plotterHW.driveL.scrollTo(dl, DRIVE_STEP_TIME)
                t1 = time.time()
                print '> GPIO time per step: ' + str((t1 - t0)  / n - DRIVE_STEP_TIME) + ' total time: ' + str(t1 - t0) + ' calculated time: ' +  str((GPIO_TIME2 + DRIVE_STEP_TIME) * n) + ' step time: ' + str(DRIVE_STEP_TIME) + ' steps: ' + str(n)
              
            if displayMenu == 18:
             
                print "> step motor time [ms]: " + str(DRIVE_STEP_TIME * 1000)
                try:
                    d = float(raw_input("> set step motor time [ms]: "))
                    DRIVE_STEP_TIME = d / 1000
                    print "> step motor time [ms]: " + str(DRIVE_STEP_TIME * 1000)
                except:
                    d = DRIVE_STEP_TIME

            if displayMenu == 19:

                print ">  drive step mult: " + str(DRIVE_STEP_MULT)
                try:
                    d = float(raw_input("> set H bridge drive step mult: "))
                    print "> drive step mult: " + str(d)
                    DRIVE_STEP_MULT = d
                except:
                    d = 1
                    
                DRIVE_STEP_DISTANCE = (DRIVE_STEP_ANGLE / DRIVE_STEP_MULT) * DRIVE_WHEEL_DIAMETER 
                
            if displayMenu == 20:
                gui.printInfo()
                
                print
                try:
                        x = int(raw_input("> X from X_0 [mm]: "))
                except:
                        x = int(v_plotter.getX())
                try:
                        y = int(raw_input("> Y from Y_0 [mm]: "))
                except:
                        y = int(v_plotter.getX())
                        
                
                v_plotterHW.scrollToXY(x, y) 

            if displayMenu == 21:
                gui.printInfo()  
                v_plotterHW.measureGPIO() 
                
            if displayMenu == 30:
                gui.printInfo()  
                conf() 
                
            if displayMenu == 31:
                gui.printInfo()
                global SPRAY_TIME
                global L_STEP_DISTANCE
                global SVG_RATIO
                SPRAY_TIME = v_conf.confFloat("> Set spray time", SPRAY_TIME)
                L_STEP_DISTANCE = int(v_conf.confFloat("> Set svg step distance", L_STEP_DISTANCE))  
                SVG_RATIO = int(v_conf.confFloat("> Set svg ratio", SVG_RATIO))  
   
# ---------------------------------------------------------
#outputMap
# --------------------------------------------------------- 
class outputMap:
    
    img = None
    draw = None
    
    fileName = "v_tension.png"
    
    @staticmethod
    def calculate():
        v_tension.setup(outputMap.fileName, X_BASE, X_BASE)
    
    @staticmethod
    def init():
        outputMap.img = Image.open(outputMap.fileName)
        outputMap.draw = ImageDraw.Draw(outputMap.img)
    
    @staticmethod
    def spray(x, y):
        outputMap.draw.ellipse((x-SPRAY_D, y-SPRAY_D, x+SPRAY_D, y+SPRAY_D), fill = 'blue', outline ='blue')

    @staticmethod
    def writeInfo():
        f = ImageFont.load_default()
        
        text =  "X_BASE=" + str(X_BASE) + " Y_BASE=" + str(Y_BASE) + " X_0=" + str(X_0) + " Y_0=" + str(Y_0) + " X_SIZE=" + str(X_SIZE) + " Y_SIZE=" + str(Y_SIZE) + " SVG RATIOE=" + str(SVG_RATIO)
        
        
        outputMap.draw.text((10, 10), text,  font=f, fill=255)
        
        
    @staticmethod
    def save(fileName):
        outputMap.writeInfo()
        outputMap.img.save(fileName, "PNG")
        if _GPIO_:
            outputMap.img.save("/var/www/" + fileName, "PNG")

    @staticmethod
    def sprayLine(x0, y0, x1, y1):
        outputMap.draw.line((x0, y0, x1, y1), fill ='black')
        
# ---------------------------------------------------------
#inputPattern
# --------------------------------------------------------- 

class inputPattern:
    imageIndex = 0
    fileNames = None
    
    @staticmethod
    def getImage(filemane):
        #img = Image.open(os.path.join('data', filemane))
        img = Image.open(filemane)
        return img.convert('RGB')
    
    @staticmethod
    def init():
        inputPattern.fileNames = []
        for (dirpath, dirnames, filenames) in walk(os.path.join('data')):
            inputPattern.fileNames.extend(filenames)
        
    
    @staticmethod
    def getFilename(path):
        i = 1
        filenames = next(os.walk('./data'))[2]
        for file in filenames:
            print  i, ': ', file
            i = i + 1
        
        try:
            i = int(raw_input("> Select file: "))
            if i == 0:
                return 0
            return path + '/' + filenames[i - 1]
            
        except:
            return 0
            
# ---------------------------------------------------------
#inputPatternSVG
# --------------------------------------------------------- 

class inputPatternSVG:
   
    @staticmethod
    def getFilename(path):
        i = 1
        filenames = next(os.walk(path))[2]
        for file in filenames:
            print  i, ': ', file
            i = i + 1
        try:
            i = int(raw_input("> Select file: "))
            if i == 0:
                return 0
            return path + '/' + filenames[i - 1]
            
        except:
            return 0
   
    @staticmethod
    def getSVGpaths(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
            
        paths = []
        for elem in tree.iter():
            print "TAG:  ", elem.tag
            if elem.tag == "{http://www.w3.org/2000/svg}path":
                paths.append(parse_path(elem.attrib.get('d')))
           
        #for path in paths:
        #    print path 
        #sys.exit(0)  
        return paths   
    
# ---------------------------------------------------------
#PYGAME WRAPPER
# ---------------------------------------------------------
 
class pygameGui:
    
    window = None
    
    PYGAME_THREAD_RUN  = True
    
    @staticmethod
    def spray(x, y):
        if _PYGAME_:
            x = int(round(x * PYGAME_RATIO))
            y = int(round(y * PYGAME_RATIO))
            pygame.draw.circle(pygameGui.window, WHITE, (x, y), int(SPRAY_D * 2))
            pygame.display.flip() 
    
    @staticmethod
    def reset():
	if _PYGAME_:
        	pygameGui.window.fill(BLACK)
            
    @staticmethod
    def drawPreviews():
        if _PYGAME_:
            pygameGui.window.fill(BLACK)
            x_offset = 0
            for fileName in inputPattern.fileNames:
                image = pygame.image.load(os.path.join('data', fileName))
                #imagerect = image.get_rect()
                pygameGui.window.blit(image, (x_offset, 0))
                x_offset = x_offset + image.get_width()
                pygame.display.flip() 
    
    @staticmethod
    def pygameProc():
        global X_BASE
        global Y_BASE  
        global PYGAME_RATIO     
        pygame.init()
        pygameGui.window = pygame.display.set_mode((int(X_BASE * PYGAME_RATIO), int(Y_BASE * PYGAME_RATIO))) 
        #pygameGui.drawPreviews()
        while pygameGui.PYGAME_THREAD_RUN:
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    # sys.exit(0) 
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit(0) 
                    elif event.key == pygame.K_RIGHT:
                        if inputPattern.imageIndex < (len(inputPattern.fileNames) - 1):
                            inputPattern.imageIndex = inputPattern.imageIndex + 1
                            # drawPreviews(fileNames)
                            # vPlott(rgb_image, 200, 100)
                    elif event.key == pygame.K_LEFT:
                        if inputPattern.imageIndex > 1 :
                            inputPattern.imageIndex = inputPattern.imageIndex - 1
                        # drawPreviews(fileNames)
                        # vPlott(rgb_image, 200, 100)
                    #print
                    #print "> ImageIndex: " + str(inputPattern.imageIndex)
                  
    
    @staticmethod
    def pygameProcStart():
        if _PYGAME_:
            thread.start_new_thread(pygameGui.pygameProc, ())
        
    @staticmethod
    def pygameProcStop():
        if _PYGAME_:
            pygameGui.PYGAME_THREAD_RUN = False
     
            
    @staticmethod
    def sprayLine(x0, y0, x1, y1):
        if _PYGAME_:
            x0 = int(round(x0 * PYGAME_RATIO))
            y0 = int(round(y0 * PYGAME_RATIO))
            x1 = int(round(x1 * PYGAME_RATIO))
            y1 = int(round(y1 * PYGAME_RATIO))
            
            pygame.draw.line(pygameGui.window, WHITE, (x0, y0), (x1, y1), int(SPRAY_D * 2))
            pygame.display.flip() 
               
# ---------------------------------------------------------
#
# --------------------------------------------------------- 
            
def heardEnter():
    if _GPIO_:
        i,o,e = select.select([sys.stdin],[],[],0.0001)
        for s in i:
            if s == sys.stdin:
                input = sys.stdin.readline()
                return True
    return False
        



                                                
                                              
# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------

lcdHW.init()
lcdHW.displayInfo1()
        
v_plotterHW.init()

outputMap.init()

inputPattern.init()

#create the pygame screen
pygameGui.pygameProcStart()

while gui.displayMenu() != 0:
    continue

pygameGui.pygameProcStop()

v_plotterHW.scrollTo(DRIVE_L_START_DISTANCE, DRIVE_R_START_DISTANCE)

time.sleep(0.1)                                      



if _PYGAME_:
    pygame.quit()

if _GPIO_:
    lcdHW.cls()
    GPIO.cleanup()
    if PRU_ENABLE:
        moveStepper.cleanup()

if LOG:
    logFile.close()
