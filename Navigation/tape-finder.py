import time
import smbus
import cv2 as cv
import traceback
import numpy as np
from picamera import PiCamera
import matplotlib.pyplot as plt
from picamera.array import PiRGBArray
from matplotlib.collections import LineCollection

# this bound captures the noise in hsv
# masked with the tape bounds eliminates
# almost all noise
LOW_NOISE = np.array([20,0,100])
UPP_NOISE = np.array([95,85,140])

# tape bounds
# bound has significant noise
L_HSV = np.array([20,0, 100])
U_HSV = np.array([95,255, 255])

# default i2c address
# must be the same on arduino
i2c_add = 0x04
# initialize the bus
bus = smbus.SMBus(1)
# enables the car to drive
# set to 0 when target located
drive_enabled = 1
# helps in the case where
# drive_heading is infinite
# i.e. dX is 0
DIRECTIONAL_ERR = .5
# framerate global
FRAME_RATE = 30
# resolution global
RESOLUTION = (640, 480)
#stream port
STREAM_PORT = 8000


# finds the hough lines in the canny image
# also returns a mask with lines, matplotlib
# LineCollection and average dX, dY.
# TODO: split average m into clusters and
# 		map overlaping lines with cv.draw
def get_houghLines(edges):
	# tinker values
	threshold = 0
	min_lin_len = 200
	max_lin_gap = 0
	dX = 0
	dY = 0
	line_col = []
	# initalize blank image
	line_img = np.zeros((edges.shape[0], edges.shape[1],3), dtype=np.uint8,)
	lines = cv.HoughLinesP(edges, 1, .1, threshold, min_lin_len, max_lin_gap)
	for line in lines:
		for x1, y1, x2, y2 in line:
			# draw line on blank image
			cv.line(line_img, (x1, y1), (x2, y2), [0, 0, 255], 2)
			# summing the change in x and y
			dX += (x2-x1)
			dY += (y1-y2)
			# adds line to the collection
			line_col.append([(x1,-y1),(x2,-y2)])
	lineCollection = LineCollection(line_col)
	# divides the sum of deltas by number of lines
	return [line_img, lines, lineCollection, dX, dY]


# draws the lines on the base image
# also draws the lane heading
def draw_lines(base_image, lines):
	indicator_length = 20
	# combines the base and lines
	base_image = cv.addWeighted(base_image, 0.8, lines[0], 1.0, 0.0)
	# draw indicator line
	center_point = (int(base_image.shape[1]/2),int(base_image.shape[0]/2))
	end_point = (center_point[0] - int(indicator_length * lines[3]), center_point[1] - int(indicator_length * lines[4]))
	cv.line(base_image, center_point, end_point, (255,0,0), 2)
	# mark front of indicator
	cv.circle(base_image, end_point, 1, (0,255,0), -1)
	return base_image


# applies the base filters to perform
# image segmentation, canny and draws the hough lines
# returns the processed image and lines data
def process_image(base_image):
	# bilateral filter blurs noise and perserves edges
	blurred = cv.bilateralFilter(base_image, 10, 75, 75)
	blurred_hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
	mask1 = cv.inRange(blurred_hsv, LOW_NOISE, UPP_NOISE)
	mask2 = cv.inRange(blurred_hsv, L_HSV, U_HSV)
	mask = mask1 ^ mask2
	seg_img = cv.bitwise_and(blurred_hsv, blurred_hsv, mask=mask)
	edges = cv.Canny(seg_img, 0, 500)
	lines_data = get_houghLines(edges)
	processed_img = draw_lines(base_image, lines_data)
	return [processed_img, lines_data]


# converts lane headings into wheel speeds
# wheel speeds are percentages and must be positive
# talk to Mitch about vizualizing the mapping
# TODO: update equations to better direct the bot
#		possibilities for this are using a neural net,
#		this will improve the precision and eleminate
#		a lot of image processing
def update_wheel_speeds(dX, dY, bus):#
	if np.abs(dX) < .5:
		bus.write_i2c_block_data(i2c_add, drive_enabled, [100, 100, 1])
	direction = dY / dX
	dH = np.sqrt(dX**2 + dY**2)
	# positive m
	if direction > 0:
		l_wheel = 100
		# heading offset more than 45 to the right
		if direction < 1:
			drive_state = 2
			r_wheel = dX / dH * 100
		else:
			drive_state = 1
			r_wheel = (dY - dX) / dH * 100
	# negative m
	elif direction < 0:
		r_wheel = 100
		# heading offset more than 45 to the left
		if direction < -1:
			drive_state = 0
			l_wheel = dX / dH * 100
		else:
			drive_state = 1
			l_wheel = (dY - dX) / dH * 100
	else:
		drive_state = 1
		r_wheel, l_wheel = 100	
	# send state to bus
	bus.write_i2c_block_data(i2c_add, drive_enabled, [int(l_wheel), int(r_wheel), drive_state])
	return {'Left Wheel':int(l_wheel), 'Right Wheel':int(r_wheel), 'State':drive_state, 'Enabled':drive_enabled}


def main(camera, frame):
	while(1):
		camera.capture(frame, format='rgb', use_video_port=True)
		data = process_image(frame.array)
		state = update_wheel_speeds(data[1][3], data[1][4], bus)
		print(state)
		print('Average m:', data[1][4]/data[1][3])
		frame.truncate(0)

if __name__=="__main__":
	# initailize the camera
	print('Camera Opening:...')
	camera = PiCamera(resolution=RESOLUTION, framerate=FRAME_RATE)
	frame = PiRGBArray(camera, RESOLUTION)
	camera.start_preview()
	time.sleep(.5)
	print('Ready!')
	try:
		main(camera, frame)
	except KeyboardInterrupt:
		print("Stopping Bot:...")
		bus.write_i2c_block_data(i2c_add, 0, [0, 0, 1])
	except Exception as e:
		print("Stopping Bot:...")
		bus.write_i2c_block_data(i2c_add, 0, [0, 0, 1])
		print(e)
		print(e)

	# clean up
	print('Cleaning Windows and Camera:...')
	camera.stop_preview()
	cv.destroyAllWindows()
