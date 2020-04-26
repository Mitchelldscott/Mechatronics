import numpy as np
import cv2
import depthai
import consts.resource_paths
import argparse
import os

'''
Script for acquiring images for annotation
- Press spacebar to capture image 

'''
# Parse command line to get save directory
parser = argparse.ArgumentParser(description='Script for image acquisition from Luxonis, press spacebar to capture, "q" to quit')
parser.add_argument("--directory","-d",help="\t save directory by default uses current directory\n",default=os.getcwd())
args = parser.parse_args()
save_directory = args.directory

if not os.path.exists(save_directory):
	os.makedirs(save_directory)


if not depthai.init_device(consts.resource_paths.device_cmd_fpath):
	print("Error Initializing device. Try to reset it.")
	exit(1)

# create pipeline for previewout stream

p = depthai.create_pipeline(config={
	'streams': 
	{
		'name': 'previewout', 
		#'max_fps': 12.0
	}, # {'name': 'depth_sipp', "max_fps": 12.0}, 
	'depth':
    	{
        	'calibration_file': consts.resource_paths.calib_fpath,
        	# 'type': 'median',
        	'padding_factor': 0.3
    	},
	'ai': 
	{
		'blob_file': consts.resource_paths.blob_fpath
	},
	'board_config':
    	{
        	'swap_left_and_right_cameras': True, # True for 1097 (RPi Compute) and 1098OBC (USB w/onboard cameras)
        	'left_fov_deg': 69.0, # Same on 1097 and 1098OBC
        	'left_to_right_distance_cm': 7.5, # Distance between stereo cameras
        	'left_to_rgb_distance_cm': 2.0 # Currently unused
    	}
})

if p is None:
	print("Error creating pipeline")
	exit(2)

# initialize starting image number
ind = 0		# starting file
N = 4 			# Number of digits 
fname = str(ind).rjust((N+1)-np.size(ind),'0')
while os.path.isfile(fname +".jpg"):		# fname now represents first available image in set
	#i = ord(ind)
	ind += 1
	#ind = chr(i)
	fname = str(ind).rjust((N+1)-np.size(ind),'0')
	
fname = fname + '.jpg'

while True:
	data_packets = p.get_available_data_packets()
	
	for packet in data_packets:
		if packet.stream_name == 'previewout':
			data = packet.getData()
			data0 = data[0,:,:]
			data1 = data[1,:,:]
			data2 = data[2,:,:]
			frame = cv2.merge([data0,data1,data2])
			cv2.imshow('previewout',frame)
	key = cv2.waitKey(1);
	if key == ord('q'):
		break
	if key == ord(' '):
		cv2.imwrite(os.path.join(save_directory,fname),frame)
		#i = ord(ind)
		ind += 1
		#ind = chr(i)
		fname = str(ind).rjust((N+1)-np.size(ind),'0') + '.jpg'

del p

