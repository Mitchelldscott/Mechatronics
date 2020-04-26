#!/usr/bin/python3
from LuxonisFunctions import *
import threading
import time
import serial
import tflite_runtime.interpreter as tflite
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
#from picamera import PiCamera
#from picamera.array import PiRGBArray
import serial
from time import sleep

exitFlag = 0
isTarget = 0

# Pan tilt Parameters
thresh = 20 # px
xServo = '0 '
fire = '3 '
deltaP = 5 # degrees
fire_time = 6

class Target (threading.Thread):
	def __init__(self, config, p, method,ser):
		threading.Thread.__init__(self)
		self.config = config
		self.p = p
		self.method = method
		self.ser = ser
	def run(self):
		while exitFlag is 0:
			data = getImageData(self.p,self.config,self.method,None)
			global isTarget

			if data is not None:
				# Target identified
				isTarget = 1		
				
				# Check X position				
				x_pos = data[0]

				# Check if centered and Fire
				if abs(x_pos) < thresh:
				
					# Construct command
					#print(x_pos)			
					command = fire + '\n'
					self.ser.write(command.encode('utf-8'))
					init_time = time.time()
					inData0 = self.ser.readline()	# Only used for testing

					# Keep up with data queue
					while (time.time() - init_time < fire_time):
						data = getImageData(self.p,self.config,self.method,2)
						#print(time.time() - init_time, data)
						
					# Successful shot - reset navigation					
					if data is None:
						isTarget = 0
						print('reset')
						
				# Otherwise move servo by fixed amount 
				else:
					if x_pos > 0:
						move = -deltaP
					else:
						move = deltaP
					command = xServo + str(int(move)) + '\n'
					self.ser.write(command.encode('utf-8'))
					inData0 = self.ser.readline()		# Only used for testing			
					#print(inData0.decode('utf-8'))		# Only used for testing



class Nav (threading.Thread):
	def __init__(self, model):
		threading.Thread.__init__(self)
		#self.string = string 	# For testing
		self.model = model
		#self.ser = ser

	def run(self):
		# Allocate Tensors
		interpreter = tflite.Interpreter(model_path=self.model)
		interpreter.allocate_tensors()
		
		# Get input and output tensors
		input_details = interpreter.get_input_details()
		output_details = interpreter.get_output_details()
				
		# check the type of the input tensor
		floating_model = input_details[0]['dtype']== np.float32

		# Main loop
		while exitFlag is 0:
		
			# Only perform inference if there is a target
			if isTarget is 0:

				# Aquire image
				for i in range(0,5):
					input_data = np.asarray([cv.cvtColor(cv.imread(im_dir+'/img'+str(i)+'.jpg'),cv.COLOR_BGR2RGB)], dtype=np.float32)
					print(input_data.shape, type(input_data[0][0][0][0]))

					interpreter.set_tensor(0,input_data)

					interpreter.invoke()

					output_data = interpreter.get_tensor(37)
					print(output_data)
					print(output_details[0]['index'])

					# Pass to arduino to map and allocate motors
					# ser1.write()
				time.sleep(1)
			time.sleep(2)	


if __name__ == '__main__':
	# Setup Luxonis
	config, p = setupLuxonis()
	
	# Establish serial communication
	ser0 = serial.Serial('/dev/ttyACM0')
	# ser1 = serial.Serial('/dev/ttyACM1')

	# Initialize the pan-tilt
	time.sleep(2)	
	ser0.write(bytes('y','utf-8'))
	
	# Create new threads
	thread1 = Target(config,p,'CV',ser0)
	thread2 = Nav('Nav-Model-1.tflite')#,ser1)

	# Start new threads
	thread1.start()
	thread2.start()
	

#thread1.join()
#thread2.join()
