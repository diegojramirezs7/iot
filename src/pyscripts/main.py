from picamera import PiCamera
import time
import os
import sys
import serial
from datetime import datetime

camera = PiCamera()

##def get_weight():
##    ser = serial.Serial('/dev/ttyACM0',9600)
##    try:
##        read_serial=ser.readline()
##        st = read_serial.decode('utf-8')
##        weight = float(st)
##        return weight
##    except:
##        print("error")
##    
##    return 0

def read_arduino(weight = False, ht = False):
    """not tested yet,
       passing the true value to only one argument will return only that value
       calling method with no arguments will return all 3 values and calling
       True on both arguments will return all 3 values"""
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600)
        data = ser.readline()
        if data:
            dataString = data.decode("utf-8")
            dataArray = dataString.split(",")
            #xor weight and ht, only return true if both are false or both are true
            if not (weight ^ ht):    
                weight = dataArray[0]
                humidity = dataArray[1]
                temperature = dataArray[2]
                return weight, humidity, temperature
            elif weight == True:
                weight = dataArray[0]
                return weight
            elif ht == True:
                humidity = dataArray[1]
                temperature = dataArray[2]
                return humidity, temperature
    except:
        print("error")
    
    return None

def take_pictures(directory, n = 5):
    camera.start_preview(alpha = 200)
    for i in range(n):
        path = directory+"pic%s.jpg" % i
        camera.capture(path)
        time.sleep(1)
        print("take_pictures called")
	
    camera.stop_preview()

def save_weight(directory, weightIn = 0):
    ls = []
    total = 0
    for i in range(10):
        dt = get_weight()
        ls.append(dt)
        total += dt
    
    average = dt / 10
        
    with open(directory+"/weight.csv", 'w+') as f:
        counter = 1
        for item in ls:
            st = "%s, %s"%(counter, item)
            f.write(st)
            counter += 1
        
        tx = "average, %s"%average
        f.write(tx)

def main():
    while True:
        previousTime = datetime.now()
        weight = get_weight()
        #weight is greater than 5.3 grams
        if weight > 5.3:
            currentTime = datetime.now()
            diff = currentTime - previousTime
            #more than 5 minutes from last measurement
            if diff.seconds > 5:
                #for each animal a folder is created, folder name is the time.
                #in folder there will be 5 pictures and weight.csv file
                dir = "/home/pi/Documents/logs/"+str(currentTime)
                os.mkdir(dir)
                take_pictures(dir, n = 5)
                save_weight(dir, weight)
main()

