import argparse
from LuxonisFunctions import * # Custom functions to make more readable
from time import sleep
import serial
'''
Script for getting the location relative to the center of the image of the bad guy targets
Utilizes custom nn to recognize target offloaded to Luxonis 

'''
thresh = 20 # px
xServo = '0 '
fire = '3 '
deltaP = 5 # degrees

if __name__ == '__main__':
	# Setup Luxonis
	config, p = setupLuxonis()

	# Establish serial communication
	ser0 = serial.Serial('/dev/ttyACM0')
	# ser1 = serial.Serial('/dev/ttyACM1')

	# Initialize the pan-tilt
	sleep(2)	
	ser0.write(bytes('y','utf-8'))
	
	if p is None:
	        print("Error creating pipeline")
	        exit(2)

	# Setup Watchdog
	# reset_process_wd() # Currently not used
	method = 'CV'
	while True:
		data = getImageData(p,config,method)
		if data is not None:
			# Centering operation from Luxonis vision			
			x_pos = data[0]
			#print(data[0])
			if abs(x_pos) < thresh:
				print(x_pos)				
				command = fire + '\n'
			else:
				if x_pos > 0:
					move = -deltaP
				else:
					move = deltaP
				command = xServo + str(int(move)) + '\n'
			ser0.write(command.encode('utf-8'))
			inData0 = ser0.readline()		# Only used for testing
			#inData1 = ser0.readline()			
			print(inData0.decode('utf-8'))		# Only used for testing
			#print(inData1.decode('utf-8'))

	
