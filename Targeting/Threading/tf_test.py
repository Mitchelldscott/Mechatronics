#!/usr/bin/env python3
import tflite_runtime.interpreter as tflite
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
#from picamera import PiCamera
#from picamera.array import PiRGBArray
import serial
from time import sleep


# Image Directory
im_dir = '/home/pi/Mechatronics/Navigation/images'

# Setup interpreter
interpreter = tflite.Interpreter(model_path='Nav-Model-1.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# check the type of the input tensor
floating_model = input_details[0]['dtype']== np.float32

for i in range(0,5):
	input_data = np.asarray([cv.cvtColor(cv.imread(im_dir+'/img'+str(i)+'.jpg'),cv.COLOR_BGR2RGB)], dtype=np.float32)
	print(input_data.shape, type(input_data[0][0][0][0]))

	interpreter.set_tensor(0,input_data)
	#interpreter.set_tensor(input_details[0]['index'],input_data)

	interpreter.invoke()

	#output_data = interpreter.get_tensor(output_details[0]['index'])
	#results = np.squeeze(output_data)
	output_data = interpreter.get_tensor(37)
	print(output_data)
	print(output_details[0]['index'])
