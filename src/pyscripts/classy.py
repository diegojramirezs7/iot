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
		self.lastTimeWeightSaved = datetime.now()
		self.lastEnvTime = datetime.now()
		self.envTime = datetime.now()
		self.count = 0

	def read_arduino(self, weight = False, ht = False):
		"""passing the true value to only one argument will return only that value
		calling method with no arguments will return all 3 values and calling
		True on both arguments will return all 3 values
		Read data from /dev/ttyACM0 file which is constantly received data from arduino """
		try:
			data = self.ser.readline()
			if data:
				dataString = data.decode("utf-8")
				dataArray = dataString.replace("\n", "").split(",")
				#xor weight and ht, only return true if both are false or both are true
				if len(dataArray) == 3:
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
			print("Error Reading from Arduino")

		return None

	def take_pictures(self, directory, n = 5):
		"""
		Camera library already included in PI, take a default of 5 pictures when called
		save all the pictures in director passed as argument
		"""
		self.camera.start_preview(alpha = 200)
		for i in range(n):
			path = directory+"pic%s.jpg" % i
			self.camera.capture(path)
			time.sleep(1)
	
		self.camera.stop_preview()
	
	#if only weight needs to be saved
	def save_weight(self, directory):
		"""
		save weight in a weight.csv file
		"""
		try:
			ls = []
			total = 0
			for i in range(1, 11):
				dt = self.read_arduino(weight = True)
				if dt != None:
					ls.append(dt)
					total += float(dt)

			average = total / 10.0

			with open(directory+"/weight.csv", "w+") as f:
				ctr = 1
				f.write("count, weight")
				for item in ls:
					st = "%s, %s\n"%(ctr, item)
					f.write(st)
					ctr += 1

				tx = "average, %s"%average
				f.write(tx)
		except:
			print("error saving weight")

	#if only temp and humidity want to be read and saved
	def save_th(self, path, timestamp):
		try:
			totalHumidity = 0
			totalTemp = 0
			for i in range(1, 11):
				humidity, temp = self.read_arduino(ht = True)
				totalHumidity += float(humidity)
				totalTemp += float(temp)

			averageHumidity = totalHumidity / 10
			averageTemp = totalTemp / 10

			with open(path, "a") as f:
				if os.stat(path).st_size == 0:
					f.write("count, humidity, temperature, timestamp\n")
				
				st = "%s, %s, %s, %s\n"%(self.count+1, averageHumidity, averageTemp, timestamp)
				f.write(st)
		except:
			print("Error saving temp and humidity")

	def save_lightlevel(self, path, timestamp):
		try:
			with open(path, "a") as f:
				if os.stat(path).st_size == 0:
					f.write("count, light level, timestamp\n")
				
				lightLevel = lightsensor.readLight()
				#lightLevel = 3
				st = "%s,  %s, %s\n"%(self.count+1, lightLevel, timestamp)
				f.write(st)
		except:
			print("error saving light level")
		
	#save all three to a same file, not actually used in script
	def save_wth(self, directory):
		ls = []
		totalHumidity = 0
		totalTemp = 0
		totalWeight = 0
		for i in range(1, 11):
			weight, humidity, temp = self.read_arduino()
			totalWeight += float(weight)
			totalHumidity += float(humidity)
			totalTemp += float(temp)
			ls.append((weight, humidity, temp))

		averageWeight = totalWeight / 10
		averageHumidity = totalHumidity / 10
		averageTemp = totalTemp / 10

		with open(directory+"/data.csv", "w+") as f:
			ctr = 1
			f.write("count, weight, humidity, temperature\n")
			for item in ls:
				line = (ctr, item[0], item[1], item[2])
				st = st = "%s, %s, %s, %s\n"%line
				f.write(st)
				ctr += 1

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
			try:
				weight = self.read_arduino(weight = True)
				if weight == None:
					weight = 0.0
			except:
				weight = 0.0

			if weight > 5.3:
				#update current time every time weight scale is more than 5 grams
				lastTimeWeightDetected = datetime.now()
				diff = lastTimeWeightDetected - self.lastTimeWeightSaved
				#more than 5 minutes from last measurement
				if diff.seconds >= 7:
					#for each animal a folder is created, folder name is the time.
					#in folder there will be 5 pictures and weight.csv file
					directory = "/home/pi/Documents/logs/"+str(lastTimeWeightDetected)
					os.mkdir(directory)
					self.take_pictures(directory, n = 5)
					self.save_weight()
					self.lastTimeWeightSaved = datetime.now()

			self.envTime = datetime.now()
			envDiff = self.envTime - self.lastEnvTime
			if envDiff.seconds >= 300:
				lightpath = "/home/pi/Documents/logs/light_data.csv"
				thPath = "/home/pi/Documents/logs/temp_humidity.csv"
				self.save_lightlevel(lightpath, str(self.envTime))
				self.save_th(thPath, str(self.envTime))
				self.lastEnvTime = datetime.now()
				self.count += 1

if __name__ == '__main__':
	driver = Driver()
	driver.run()