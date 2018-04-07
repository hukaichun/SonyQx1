import os
import serial
import struct
import time ,threading
"""@package PhysicalController
Communicate with Arduino via USB port
"""



def getDevName():
    os.system('ls /dev/ | grep ttyUSB > devName')
    line = ""
    with open('devName') as f:
        line = f.readline().rstrip()
    print "Device Name: " + line
    return line

class PhysicalController(serial.Serial):
    def __init__(self, devName, baudRate):
        print '[Arduino] Connecting ...',
        super(PhysicalController, self).__init__(devName, baudRate)
        print 'done'
        self.turnTableIO = True;
        self.turnTableDir= True;



    def __call__(self, pid = None, action =None , io = None):
        if(pid == None):
            self.resp = str()
            while(self.in_waiting>0):
                self.resp += self.read()
            return self.resp

        self.write(struct.pack('s1s1s1',chr(pid),chr(action),chr(io)))
        self.flush()
        time.sleep(0.05) # 0.03
 
    def actShutter(self):
        self(12,0xff,0)
        print "[Arduino] actShutter"

    def releaseShutter(self):
        self(12,0xff,1)
        print "[Arduino] releaseShutter"

    def turnTable(self):
        self.turnTableIO = not self.turnTableIO;
        self(9,0xff,self.turnTableIO)
    
    def changeTurnTableDir(self):
        self.turnTableDir = not self.turnTableDir
        self(10,0xff,self.turnTableDir)

def printNum(num):
    for i in range(num):
        print i*0.05
        time.sleep(0.05)

if __name__ == "__main__":
    ser = PhysicalContraller('/dev/'+getDevName(), 9600)
    time.sleep(1)
    ser()
    time.sleep(1)
    ser(0,0xf0,ord('a'))
    time.sleep(1)
    _ = ser()
    for i in _:
        print ord(i),
    print ";"

    time.sleep(1)
    ser(0,0xf0,ord('b'))
    time.sleep(1)
    _ = ser()
    for i in _:
        print ord(i),
    print ";"
    
else:
    pass
    #ser = PhysicalContraller('/dev/'+getDevName(), 9600)
