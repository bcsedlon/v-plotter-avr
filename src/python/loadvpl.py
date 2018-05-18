import time
import csv
from datetime import datetime
import serial

class growmat_easy:
    
    # configure the serial connections (the parameters differs on the device you are connecting to)
    port='/dev/ttyUSB1'
    port='COM2'

    ser = None
    
    def connect(self, port):
        '''
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts=0
        )
        '''
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 115200 #9600
        self.ser.parity=serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        #self.ser.timeout = 1
        self.ser.setDTR(False)
        self.ser.open()
    
        self.ser.setDTR(False)
        print('Connected to: ' + self.ser.portstr)
        
    def disconnect(self):
        if self.ser != None:
            self.ser.close()
            self.ser = None
        print('Disconnected')
        
    def read(self):
        #self.ser.flushInput() #flush input buffer, discarding all its contents
        #self.ser.flushOutput()#flush output buffer, aborting current output 
        #data = '#?' #+ '\r\n'
        #print('> ' + data)
        #self.ser.write(data + '\r\n') 
        self.sendCmd('#?')
        time.sleep(2)
        emptyLineCnt = 0
        data = ''
        while self.ser.inWaiting() > 0:
            line = self.ser.readline()
            #print('< ' + line)
            if line == '':
                emptyLineCnt = emptyLineCnt + 1
            if emptyLineCnt > 1:
                break 
            data = data + line
        
        return data
        
    def getValue(self, name, data):
        for line in data.splitlines():
            #print(line)
            if line.find(name) > -1:
                try:
                    line.replace('.', ',')
                    value = float(line[line.find(name) + len(name):])
                    return value
                except Exception as e:
                    print(e)
        return float('nan')

    def getControlValue(self, name, data):
        for line in data.splitlines():
            #print(line)
            pos = line.find(name)
            if pos > -1:
                try:
                    control = line[pos + len(name):pos + len(name) +1]
                    mode = line[pos + len(name) + 1:pos + len(name) + 1 + 1]
                    #print control
                    #print mode
                    return (control, mode)
                except Exception as e:
                    print(e)
        return ('?', '?')
     
    def sendCmd(self, cmd):
        self.ser.flushInput() #flush input buffer, discarding all its contents
        self.ser.flushOutput()#flush output buffer, aborting current output 
        data = cmd
        print('> ' + data)
        self.ser.write(data + '\r\n') 

    
    def getParamInt(self, address):
        address = '%04d' % address
        self.sendCmd('#PRI' + address)
        while self.ser.inWaiting() == 0:
            pass
        time.sleep(0.2)
        #if self.ser.inWaiting() > 0:
        data = self.ser.readline()
        data = data[:data.find('\n')]
        #print('--%d--' % data)
        print data
        return int(data)    
 
    def getParamFloat(self, address):
        address = '%04d' % address
        self.sendCmd('#PRF' + address)
        while self.ser.inWaiting() == 0:
            pass
        time.sleep(0.2)
        #if self.ser.inWaiting() > 0:
        data = self.ser.readline()
        data = data[:data.find('\n')]
        print data
        return float(data)   
                
    def setParamInt(self, address, data):
        address = '%04d' % address
        self.sendCmd('#PWI' + address + ':' + str(data))
 
    def setParamFloat(self, address, data):
        address = '%04d' % address
        self.sendCmd('#PWF' + address + ':' + str(data))

    def reloadParam(self):
        self.sendCmd('#PLD')

#print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

import os.path

import sys


if __name__ == "__main__":
    
    # configure the serial connections (the parameters differs on the device you are connecting to)
    port='/dev/ttyUSB1'
    port='COM2'
    
    g = growmat_easy() 
    g.connect(port)
    

    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        exit()
    
    g.ser.write('#F')
    time.sleep(2)
    print(fileName)
    #fo = open('out.vpl', 'wb')
    with open(fileName, 'rb') as file:
        data = file.read(255)    
        while data != '':
            #print(data)
            g.ser.write(data)
            #fo.write(data)
            data = file.read(255)    
            time.sleep(0.1)
        