import cv2 as cv
import numpy as np
from image_processor import Image_Processor


noiseRange = np.array([[20,0,100],[95,75,150]])
yellowRange = np.array([[20,0, 100],[95,255, 255]])

protocol = {
	'crop': ([0,.45,1,1], True),
	'rgb2hsv': 0, 
	'bilateral-blur': (10, 75, 75),
	'bitwise-and': (noiseRange, yellowRange),
	'canny': (0, 500),
	'find-lines': np.array([[100, 1, 0, 500, 0], 3]),
	'draw-indicator': 40}

processor = Image_Processor(protocol=protocol, display_steps=[0,1,2,3,4,5,6,7])
processor.process(cv.imread('images/img0.jpg'))
