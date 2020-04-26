#!/usr/bin/python3
from LuxonisFunctions import *
import threading
import time
import serial
import tflite_runtime.interpreter as tflite
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from picamera import PiCamera
from picamera.array import PiRGBArray
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
				print("Centering...")		
				
				# Check X position				
				x_pos = data[0]

				# Check if centered and Fire
				if abs(x_pos) < thresh:
				
					# Construct command
					#print(x_pos)			
					print("Fire!")					
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
	def __init__(self, model,camera):
		threading.Thread.__init__(self)
		#self.string = string 	# For testing
		self.model = model
		self.camera = camera
		self.frame = PiRGBArray(self.camera, size=(640,720))
		self.cut = [-54, -18, 18, 54]
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
				camera.start_preview()
				self.camera.capture(self.frame,'rgb')
				input_data = np.array([self.frame.array],dtype=np.float32)
				interpreter.set_tensor(0,input_data)
				interpreter.invoke()
				heading = interpreter.get_tensor(37)
				print(heading)
				heading_id = int(np.digitize(x=heading, bins=self.cut))	
				print(heading_id)
				#self.ser.write(bytearray([1, heading_id])	
				self.frame.truncate(0)
				time.sleep(1)
				
			else:
				#self.ser.write(disable_msg)
				time.sleep(2)	


if __name__ == '__main__':
	# Setup Navigation
	camera = PiCamera(resolution=(640,720))	
	# ser1 = serial.Serial('/dev/ttyACM1')
	navigation = Nav('Nav-Model-1.tflite',camera)#,ser1)
	navigation.start()
	
	# Setup Targeting
	ser0 = serial.Serial('/dev/ttyACM0')
	time.sleep(2) # Initialize the pan-tilt	
	ser0.write(bytes('y','utf-8'))
	config, p = setupLuxonis()	
	target = Target(config,p,'CV',ser0)
	target.start()
	

#thread1.join()
#thread2.join()
