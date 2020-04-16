import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt


def get_end_points(line, x1, x2):
	y1 = int(line[0] * x1 + line[1])
	y2 = int(line[0] * x2 + line[1])
	return (x1, y1), (x2, y2)

class Image_Processor():
	def __init__(self, protocol={}, display_steps=[], resolution=(640, 480)):
		self.protocol = protocol
		self.display_steps = display_steps
		self.width = resolution[0]
		self.height = resolution[1]
		self.results = []
	
	def parse_regions(self, houghp_args, partition):
		
		line_img = np.zeros((self.height, self.width, 3), dtype=np.uint8,)
		lines = cv.HoughLinesP(self.results[-1], houghp_args[0], houghp_args[1], houghp_args[2], houghp_args[3], houghp_args[4])
		left_lines = []
		center_lines = []
		right_lines = []
		l_bound = int(self.width * ( 1 / partition))
		r_bound = int(self.width * (1 - (1 / partition)))
		print(l_bound)
		# creates a slope-Int form of each hough line
		# and sorts into regions
		for line in lines:
			for x1, y1, x2, y2 in line:
				if x1 != x2:
					fit = np.polyfit((x1, x2), (y1, y2), 1)
					slope = fit[0]
					intercept = fit[1]
					if x1 < l_bound:
						print('left')
						left_lines.append((slope, intercept))
					elif x1 > r_bound:
						right_lines.append((slope, intercept))
					elif x1 > l_bound and x1 < r_bound:
						#print('center')
						center_lines.append((slope, intercept))

		# average each region
		# and draw lines
		if len(left_lines) > 0:
			print('left found')
			left_avg = np.nanmean(left_lines, axis=0)
			ep = get_end_points(left_avg, 0, l_bound)
			cv.line(line_img, ep[0], ep[1], (0,255,0), 3)
		if len(center_lines) > 0:
			print('center found')
			center_avg = np.nanmean(center_lines, axis=0)
			ep = get_end_points(center_avg, l_bound, r_bound)
			cv.line(line_img, ep[0], ep[1], (0,255,0), 3)
		if len(right_lines) > 0:
			print('right found')
			right_avg = np.nanmean(right_lines, axis=0)
			ep = get_end_points(right_avg, r_bound, self.width)
			cv.line(line_img,  ep[0], ep[1], (0,255,0), 3)
		return line_img

	def display(self):
		cols = 4
		rows = int(len(self.display_steps) / cols)
		step = 0
		fig, axes = plt.subplots(rows, cols, figsize=(15,7))
		for r in range(rows):
			for c in range(cols):
				axes[r][c].imshow(self.results[self.display_steps[step]])
				axes[r][c].set_title('Step: ' + str(self.display_steps[step]))
				step += 1
		plt.show()
		cv.waitKey()

	def process(self, frame, protocol={}, display_steps=[]):
		self.results = [frame]
		self.width = frame.shape[1]
		self.height = frame.shape[0]

		if len(protocol) == 0:
			protocol = self.protocol
		if len(display_steps) == 0:
			display_steps = self.display_steps

		for step in protocol:
			if step == 'crop': # 'crop': bounds, set as original
				y_min = int(protocol[step][0][1] * self.height)
				y_max = int(protocol[step][0][3] * self.height)
				x_min = int(protocol[step][0][0] * self.width)
				x_max = int(protocol[step][0][2] * self.width)
				self.width = x_max - x_min
				self.height = y_max - y_min
				if protocol[step][1]:
					self.results[0] = self.results[0][y_min:y_max,x_min:x_max]
				else:
					self.results.append(self.results[-1][y_min:y_max,x_min:x_max])

			if step == 'rgb2hsv': # 'rgb2hsv': any value
				self.results.append(cv.cvtColor(self.results[-1], cv.COLOR_RGB2HSV))

			if step == 'bilateral-blur': # 'bilateral-blur': [bound1, bound2, bound3]
				self.results.append(cv.bilateralFilter(self.results[-1], protocol[step][0], protocol[step][1], protocol[step][2]))

			if  step == 'bitwise-and': # 'bitwise_and': [bound1, bound2... boundn]
				# generate masks
				mask = cv.inRange(self.results[-1], np.array(protocol[step][0][0]), np.array(protocol[step][0][1]))
				for bound in protocol[step][1:]:
					mask = mask ^ cv.inRange(self.results[-1], np.array(bound[0]), np.array(bound[1]))
				self.results.append(mask)
				# apply masks
				self.results.append(cv.bitwise_and(self.results[-1], self.results[-1], mask=mask))

			if step == 'canny': # 'canny': [bound1, bound2]
				self.results.append(cv.Canny(self.results[-1], protocol[step][0], protocol[step][1]))
			
			if step == 'find-lines': # 'find-lines': [[houghp args], step, partition]
				line_img = self.parse_regions(protocol[step][0], protocol[step][1])
				self.results.append(cv.addWeighted(self.results[0], 0.8, np.array(line_img), 1.0, 0.0))

			if step == 'draw-indicator': # 'draw-indicator': length
				center_point = (int(self.width/2),int(self.height/2))
				end_point = (center_point[0] - protocol[step], center_point[1] - protocol[step])
				annotated_img = self.results[-1].copy()
				cv.line(annotated_img, center_point, end_point, (255,0,0), 2)
				cv.circle(annotated_img, end_point, 1, (0,255,0), -1)
				self.results.append(annotated_img)

		self.display()
