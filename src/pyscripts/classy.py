from picamera import PiCamera
import time
import os
import sys
import serial
from datetime import datetime
import lightsensor

class Driver:
	def __init__(self):
		self.camera = PiCamera()
		self.ser = serial.Serial('/dev/ttyACM0', 9600)
		self.previousTime = datetime.now()

	def read_arduino(self, weight = False, ht = False):
		"""not tested yet, passing the true value to only one argument will return only that value
		calling method with no arguments will return all 3 values and calling
		True on both arguments will return all 3 values"""
		try:
			data = self.ser.readline()
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

	def take_pictures(self, directory, n = 5):
		"""
		Camera library already included in PI, take a default of 5 pictures when called
		save all the pictures in director passed as argument
		"""
		camera.start_preview(alpha = 200)
		for i in range(n):
			path = directory+"pic%s.jpg" % i
			camera.capture(path)
			time.sleep(1)
	
		camera.stop_preview()

	#just in case only weight is to be read, not actually used in script
	def save_weight(self, directory, weight):
		"""
		save weight in a weight.csv file
		"""
		ls = []
		total = 0
		for i in range(1, 11):
			dt = read_arduino(weight = True)
			ls.append(dt)
			total += float(dt)

		average = total / 10.0

		with open(directory+"/weight.csv", "w+") as f:
			counter = 1
			f.write("count, weight")
			for item in ls:
				st = "%s, %s\n"%(counter, item)
				f.write(st)
				counter += 1

			tx = "average, %s"%average
			f.write(tx)

	#just in case only temp and humidity want to be read, not actually used in script
	def save_th(self, directory):
		ls = []
		totalHumidity = 0
		totalTemp = 0
		for i in range(1, 11):
			humidity, temp = read_arduino(ht = True)
			totalHumidity += float(humidity)
			totalTemp += float(temp)
			ls.append((humidity, temp))

		averageHumidity = totalHumidity / 10
		averageTemp = totalTemp / 10

		with open(directory+"/temp_humidity.csv") as f:
			counter = 1
			f.write("humidity, temperature")
			for item in ls:
				st = st = "%s, %s\n"%item
				f.write(st)
				counter += 1

			tx = "average, %s, %s"%(averageHumidity, averageTemp)
			f.write(tx)

	def save_lightlevel(self, directory):
		with open(directory+"/light_level.csv") as f:
			f.write("count, light level")
			for i in range(1, 11):
				lightLevel = lightsensor.readLight()
				st = "%s,  %s\n"%(i, lightLevel)
				f.write(st)

	def save_wth(self, directory):
		ls = []
		totalHumidity = 0
		totalTemp = 0
		totalWeight = 0
		for i in range(1, 11):
			weight, humidity, temp = read_arduino()
			totalWeight += float(weight)
			totalHumidity += float(humidity)
			totalTemp += float(temp)
			ls.append((weight, humidity, temp))

		averageWeight = totalWeight / 10
		averageHumidity = totalHumidity / 10
		averageTemp = totalTemp / 10

		with open(directory+"/data.csv") as f:
			counter = 1
			f.write("count, weight, humidity, temperature\n")
			for item in ls:
				line = (counter, item[0], item[1], item[2])
				st = st = "%s, %s, %s, %s\n"%line
				f.write(st)
				counter += 1

			tx = "average, %s, %s, %s"%(averageWeight, averageHumidity, averageTemp)
			f.write(tx)

	def run(self):
		"""
		daemon thread, constantly running on the background and getting weight
		if weight received is more than 5 grams, it checks that last time recorded was 
		more than 5 minutes ago. Then calls all helper methods
		"""
		while True:
			#get weight from arduino serial com
			weight = self.read_arduino(weight = True)
			if weight > 5.3:
				#update current time every time weight scale is more than 5 grams
				currentTime = datetime.now()
				diff = currentTime - previousTime
				#more than 5 minutes from last measurement
				if diff.seconds > 7:
					#for each animal a folder is created, folder name is the time.
					#in folder there will be 5 pictures and weight.csv file
					dir = "/home/pi/Documents/logs/"+str(currentTime)
					os.mkdir(dir)
					take_pictures(dir, n = 5)
					save_wth(dir)
					save_lightlevel(dir)
					previousTime = datetime.now()

if __name__ == '__main__':
	driver = Driver()
	driver.run()
