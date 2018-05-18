import os.path
import sys
import time

path = 'a/btspp2file/'

def btspp2file_write(data):
    try:
        timeout = 0
        while os.path.exists(os.path.join(path, 'tx.txt')):
            time.sleep(0.1)
            timeout = timeout + 1
            if timeout > 40:
               raise Exception('btspp2file write timeout')

        with open(os.path.join(path, 'tx.txt'), 'a') as outfile:
             outfile.write(data + '\n')
    except Exception as e: 
        print(e)

def btspp2file_read():
    data = None
    try:
        timeout = 0
        while not os.path.exists(os.path.join(path, 'rx.txt')):
            time.sleep(0.1)
            timeout = timeout + 1
            if timeout > 40:
               raise Exception('btspp2file read timeout')
        with open(os.path.join(path, 'rx.txt'), 'r') as infile:
            
            for line in infile:
                data =  data + line   
        
    except Exception as e: 
        print(e)

    try:    
        os.remove(os.path.join(path, 'rx.txt'))
    except:
        pass
        
     return data   
        
if __name__ == "__main__":

    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        exit()
    
    print(fileName)
    with open(fileName) as file:  
        for data in file: 
            
            
            #g.ser.write('?') 
            btspp2file_write('?')
            line = btspp2file_read()
            print line
            while line == None or line[0:1] != '0':
                time.sleep(0.1)
                btspp2file_write('?')
                line = btspp2file_read()
                print line
            
            print data
            btspp2file_write(data)
            line = btspp2file_read()
            print line
        