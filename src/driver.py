import random
from datetime import datetime

def get_weight():
	weight = random.randint(0, 10)
	return weight

def main():
	previousTime = datetime.now()
	counter = 0
	while True:
		weight = get_weight()
		if weight > 5.3:
			currentTime = datetime.now()
			diff = currentTime - previousTime
			if  diff.seconds > 3:
				counter += 1
				#save_weight(currentTime, weigth)
				#take_pictures(currentTime)
				previousTime = currentTime
				st = "we got here: "+str(counter)+", weight: "+str(weight)+", diff: "+str(diff.seconds)
				print(st)

def save_weight(timestamp, weight = 0):
	ls = []
	total = 0
	
	for i in range(10):
		dt = get_weight()
		total += weight
		ls.append(dt)

	average = total / 10
	path = "somepath"
	with open(path, 'w+') as f:
		f.write()


#threading
main()