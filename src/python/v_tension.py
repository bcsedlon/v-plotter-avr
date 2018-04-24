#!/usr/bin/env python
from PIL import Image,ImageDraw,ImageOps,ImageFont
import sys
from math import sqrt,sin,cos,acos,atan2,degrees,fabs

STEP = 2

# setup the constants
version=1.7
outputFile="v_tension.png"
width, height=1000,1000
border=32
# V line end points
v1=border/2,border/2
v2=width-border/2-1,border/2

def setup(outputFile1, width1, height1):
    global outputFile
    global width 
    global height
    global v1
    global v2
    
    outputFile = outputFile1
    width = width1
    height = height1
    v1 = border/2,border/2
    v2 = width-border/2-1,border/2


def cross(draw,p,n):
    c="#000000"
    draw.line((p[0],p[1]-n,p[0],p[1]+n),c)
    draw.line((p[0]-n,p[1],p[0]+n,p[1]),c)

def drawFixtures(draw):
    # border of calculation pixels
    draw.rectangle([border-1,border-1,width-border,height-border],"#FFFFFF","#000000")
    # V line end points
    cross(draw,v1,border/4)
    cross(draw,v2,border/4)

def lineTensions(a1,a2):
    d=cos(a1)*sin(a2)+sin(a1)*cos(a2)
    return cos(a2)/d,cos(a1)/d

def tensionOk(p):
    # find angles
    a1=atan2(p[1]-v1[1],p[0]-v1[0])
    a2=atan2(p[1]-v2[1],v2[0]-p[0])
    # strings tension check
    t1,t2=lineTensions(a1,a2)
    lo,hi=.5,1.5
    return lo<t1<hi and lo<t2<hi

def dx(p1,p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2);

def calcPointB(a,b,c):
    alpha=acos((b**2+c**2-a**2)/(2*b*c))
    return b*cos(alpha)+v1[0],b*sin(alpha)+v1[1]

def resolutionOk(p):
    maxd = 1.4
    # law of cosines calculation and nomenclature
    c=dx(v1,v2)
    b=dx(v1,p)
    a=dx(v2,p)
    # sanity check
    err=.00000001 #err=.0000000001 #err=.00000000001
    pc=calcPointB(a,b,c)
    
    #print str(p[0] - err) + " < "  + str(pc[0]) + " < " + str(p[0] + err)
    
    assert p[0]-err<pc[0]<p[0]+err
    assert p[1]-err<pc[1]<p[1]+err
    # calculate mapped differences
    db=dx(p,calcPointB(a,b+1,c)) # extend left line by 1 unit
    da=dx(p,calcPointB(a+1,b,c)) # extend right line by 1 unit
    return db<maxd and da<maxd # line pull of 1 unit does not move x,y by more than max

def calcPixel(draw,p):
    t=tensionOk(p)
    r=resolutionOk(p)
    if not t and not r:
        draw.point(p,"#3A5FBD")
    if not t and r:
        draw.point(p,"#4876FF")
    if t and not r:
        draw.point(p,"#FF7F24")
    # default to background color

def drawPixels(draw):
    for y in range(border,height-border, STEP):
        #sys.stdout.write('.')
        #sys.stdout.flush()
        for x in range(border,width-border, STEP):
            calcPixel(draw,(x,y))
    sys.stdout.write('\n')

def drawGrid(draw):
    #f = ImageFont.truetype("Arial.ttf",14)
    f = ImageFont.load_default()
    
    #draw.rectangle(((0.3 * width, 0.25 * height),(0.7 * width, 0.5 * height)), fill="lightgray") #, outline = "black")
    draw.rectangle(((0.3 * width, 0.25 * width),(0.7 * width, 0.5 * width)), fill="lightgray") #, outline = "black")

    for x in range(0,width, int(width/20)):
        draw.line((x,0, x, height), fill=128)
        draw.text((x, 0), str(x),  font=f, fill=255)
        
    for y in range(0,height, int(height/20)):
        draw.line((0,y, width, y), fill=128)
        draw.text((0, y), str(y),  font=f, fill=255)
    

def draw():
    print "> V plotter map, version", version
    
    image = Image.new("RGB",(width, height),"#D0D0D0")
    draw = ImageDraw.Draw(image)

    drawFixtures(draw)
    drawPixels(draw)

    drawGrid(draw)

    image.save(outputFile,"PNG")
    print "> V plotter map image written to", outputFile
    


