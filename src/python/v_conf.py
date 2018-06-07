X_BASE = 1800 #1500 #3000 #3000 # 4000 #1400 # distance between drives (width) [mm]
Y_BASE = 2000 #1400 # distance between drives and ground (height) [mm], only limitation, all parameters are calculated from X_BASE

DRIVE_L_START_DISTANCE = 2500 #1100 #X_BASE # initial distance for drive A [mm]
DRIVE_R_START_DISTANCE = 2500 #1100 #X_BASE # initial distance for drive B [mm]

#matrix print
S_STEP_DISTANCE = 20 #10 #10 # static step distance [mm], for passive drive 
D_STEP_DISTANCE = 20 # 10 #10 # dynamic step distance [mm], for active drive 

#vector print
L_STEP_DISTANCE = 2#5 #10 #step for curve drawings [mm]

#X_BASE =3000, SVG vikipan1
SVG_RATIO = 0.75

SPRAY_TIME = 0.14 #0.14 #0.13 # 0.15#0.2#1#0.1
SPRAY_D = 1 #5 # 1 #0.5 # spray diameter for simulation (outputMap)

#spray in separated thread (no waiting)
#SPRAY_IN_PARALLEL = True 
SPRAY_IN_PARALLEL = False


PRU_ENABLE = False
#PRU_ENABLE = True

#move in separated thread, in case PRU disabled
#MOVE_IN_PARALLEL = False
DRIVE_IN_PARALLEL =True

#LOG = False
LOG = False

LOGHEX = True
     
_PYGAME_ = True     
_GPIO_ = False     


#automatic calculated printing area for best resolution
X_SIZE = int(X_BASE * 0.4)      # X size of drawing area [mm]
Y_SIZE = int(X_BASE * 0.25) # Y size of drawing area [mm]
if Y_SIZE > Y_BASE:
        Y_SIZE = Y_BASE
        
X_0 = int(X_BASE * 0.3) # X offset from drive L [mm]
Y_0 = int(X_BASE * 0.25) # Y offset from drive L [mm]

X_0 = 350

if Y_0 > Y_BASE:
        print "Error: Y_BASE is lower than optimal printing area offset!"
        exit

#manual setting of printig area
#vikipan1a 3m
SVG_RATIO = 1.0
#X_BASE = 3000
#X_SIZE = X_BASE
#Y_SIZE
#X_0 = 1000
#Y_0
#vikipan1a



def conf(msg, var):
    if var:
        msg = msg + " (Y/n):"
    else:
        msg = msg + " (y/N):"
    i = raw_input(msg)
    if i  == "n":
        return False
    if i  == "y":
        return True
    return var
        
def confFloat(msg, var):
    msg = msg + " (" + str(var) + "): "
    i = raw_input(msg)
    if i  == "":
        return float(var)
    try:
        return float(i)
    except:
        return float(var)
