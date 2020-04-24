#!/usr/bin/python3
from LuxonisFunctions import *
import threading
import time
import serial
# import tensorflow as tf

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



class dummyThread (threading.Thread):
	def __init__(self, string):
		threading.Thread.__init__(self)
		self.string = string
		#self.model = model
		#self.ser = ser

	def run(self):
		# Allocate Tensors
		#interpreter = tf.lite.Interpreter(model_path=mdodel)
		#interpreter.allocate_tensors()
		
		# Get input and output tensors
		#input_details = interpreter.get_input_details()
		#output_details = interpreter.get_output_details()
				
		# Acquire image and perform inference
		# input_shape = input_details[0]['shape']

		while exitFlag is 0:
			if isTarget is 0:
				# Get image
				# input_data = ...
				# interpreter.set_tensor(input_details[0]['index], input_data)
				
				# Process image				
				# interpreter.invoke()
				
				# Retrieve navigation direction
				# output_data = interpreter.get_tensor(output_details[0]['index])

				# Pass to arduino to map and allocate motors
				# ser1.write()
				print(self.string);
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
	
	# Load ML model 
	# interpreter = tf.lite.Interpreter(model_path = 'Navigation.h5') # Need to be .tflite?
	# interpreter.allocate_tensors()
	# input_details = interpreter.get_input_details()
	# output_details = interpreter.get_output_details()
	# CAPTURE IMAGE
	# input_data = np.expand_dims(img,axis=0)
	# interpreter.invoke()
	# output_data = interpreter.get_tensor(output_details[0]['index'])
	# results = np.squeeze(output_data)
	
	# model = tf.keras.models.load_model('Navigation.h5')	
	
	
	# Create new threads
	thread1 = Target(config,p,'CV',ser0)
	thread2 = dummyThread('test...')

	# Start new threads
	thread1.start()
	thread2.start()
	

#thread1.join()
#thread2.join()
