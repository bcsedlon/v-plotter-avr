import os.path
import sys
import time

path = '/storage/emulated/0/btspp2file/0'

def btspp2file_write(data):
    try:
        timeout = 0
        while os.path.exists(os.path.join(path, 'tx.txt')):
            time.sleep(0.1)
            timeout = timeout + 1
            if timeout > 40:
               raise Exception('btspp2file write timeout')
        
        with open(os.path.join(path, 'tx.txt'), 'w') as outfile:
             outfile.write(data)
        return True
    except Exception as e: 
        print(e)
    return False

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

    size = os.stat(fileName).st_size / 255
    i = 0

    while not btspp2file_write('#FNAME=AQ2.BLR'):
        pass
    time.sleep(2)
    while not btspp2file_write('#FPUT'):
        pass
    time.sleep(1)

    print(fileName)
    with open(fileName) as file:  
        #for data in file: 
        data = file.read(255)
        while data != '':
            
            i = i + 1
            #print(str(i) + '/' + str(size))
            sys.stdout.write(' ' + str(i) + '/' + str(size) + '\r')
            sys.stdout.flush()
            while not btspp2file_write(data):
                    pass
            time.sleep(0.2)
            data = file.read(255)


        
