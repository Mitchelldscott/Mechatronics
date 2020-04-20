import argparse
from LuxonisFunctions import * # Custom functions to make more readable

'''
Script for getting the location relative to the center of the image of the bad guy targets
Utilizes custom nn to recognize target offloaded to Luxonis 

'''
if __name__ == '__main__':
	# Setup Luxonis
	config, p = setupLuxonis()

	# Establish serial communication
	# ser0 = serial.Serial('/dev/ttyACM0')
	# ser1 = serial.Serial('/dev/ttyACM1')

	if p is None:
	        print("Error creating pipeline")
	        exit(2)

	# Setup Watchdog
	# reset_process_wd() # Currently not used
	method = 'CV'
	while True:
		data = getImageData(p,config,method)
		if data is not None:
			print(data)


	
