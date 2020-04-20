import numpy as np
import cv2
import depthai
import consts.resource_paths
from time import time
from time import sleep
import os

# Functions for Luxonis functionality

def setupLuxonis():
        if not depthai.init_device(consts.resource_paths.device_cmd_fpath):
                print("Error Initializing device. Try to reset it.")
                exit(1)

        config = {
                'streams': 
                [{
                        'name': 'previewout', 
                        'max_fps': 20.0
                },
                {
                        'name': 'metaout',
                        'max_fps': 20.0
                }],
                'depth':
                {
                        'calibration_file': consts.resource_paths.calib_fpath,
                        # 'type': 'median',
                        'padding_factor': 0.3
                },
                'ai': 
                {
                        'blob_file': consts.resource_paths.blob_fpath,
                        'blob_file_config': consts.resource_paths.blob_config_fpath,
                        'calc_dist_to_bb': True
                        #'blob_file': '/home/riley/depthai-python-extras/depthai-tutorials-practice/2-face-detection-retail/BadGuyFP16.blob',
                        #'blob_file_config': '/home/riley/depthai-python-extras/depthai-tutorials-practice/2-face-detection-retail/BadGuy.json',
                        #'calc_dist_to_bb': True
                },
                'board_config':
                {
                        'swap_left_and_right_cameras': True, # True for 1097 (RPi Compute) and 1098OBC (USB w/onboard cameras)
                        'left_fov_deg': 69.0, # Same on 1097 and 1098OBC
                        'left_to_right_distance_cm': 7.5, # Distance between stereo cameras
                        'left_to_rgb_distance_cm': 2.0 # Currently unused
                }}

        p = depthai.create_pipeline(config=config)
        return config, p

process_watchdog_timeout=10 #seconds
def reset_process_wd():
    global wd_cutoff
    wd_cutoff=time()+process_watchdog_timeout
    return

def getImageData(p,config,method):
    ctr = []
    entries_prev = []
    stream_names = [stream if isinstance(stream, str) else stream['name'] for stream in config['streams']]
    while True:
            #Acquire metadata
            nnet_packets, data_packets = p.get_available_nnet_and_data_packets()

            # Parse metadata
            for i, nnet_packet in enumerate(nnet_packets):
                for i, e in enumerate(nnet_packet.entries()):
                    if e[0]['id'] == -1.0 or e[0]['confidence'] == 0.0:	 # for MobileSSD entries are sorted by confidence
                        break

                    if i == 0:
                        entries_prev.clear()

                    entries_prev.append(e) # save entry for further usage

	    # Show images
            for packet in data_packets:
                if packet.stream_name not in stream_names:
                    continue # skip streams that were automatically added
                elif packet.stream_name == 'previewout':
                    data = packet.getData()
                    # the format of previewout image is CHW (Chanel, Height, Width), but OpenCV needs HWC, so we
                    # change shape (3, 300, 300) -> (300, 300, 3)
                    data0 = data[0,:,:]
                    data1 = data[1,:,:]
                    data2 = data[2,:,:]
                    frame = cv2.merge([data0, data1, data2])

                    img_h = frame.shape[0]
                    img_w = frame.shape[1]
                    if method is 'ML':
                        # iterate threw pre-saved entries & draw rectangle & text on image:
                        for e in entries_prev:
                            # the lower confidence threshold - the more we get false positives
                            if e[0]['confidence'] > 0.6:
                                x1 = int(e[0]['left'] * img_w)
                                y1 = int(e[0]['top'] * img_h)
                                x2 = int(e[0]['right'] * img_w)
                                y2 = int(e[0]['bottom'] * img_h)
                            
                                pt1 = x1, y1
                                pt2 = x2,y2
                                ctr = (x1+x2)/2 - img_w/2, img_h/2 - (y1+y2)/2  
                                cv2.rectangle(frame, pt1, pt2, (0, 0, 255))
                                #print(ctr)
                    if method is 'CV':
                        frame, ctr = processImage(frame)

                cv2.imshow('previewout', frame)
            key = cv2.waitKey(1)
            if ctr:
                 return ctr
            if key == ord('q'):
                exitClean(p)
                #break
    return []

def exitClean(p):
    del p
    print('py: DONE.')
    os._exit(0)

def processImage(image):
        ctr = []
        # Determine image shape
        img_h = image.shape[0]
        img_w = image.shape[1]
	# Determine Masks
        r_sensitivity = 10
        #g_sensitivity = 25
        blur = cv2.medianBlur(image,3)
        hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        #green_mask = cv2.inRange(hsv,(60 - g_sensitivity,100,20),(60 + g_sensitivity,255,255))
        red_lower = cv2.inRange(hsv,(0,100,100),(r_sensitivity,255,255))
        red_upper = cv2.inRange(hsv,(180-r_sensitivity,100,100),(180,255,255))
        red_mask = cv2.bitwise_or(red_lower,red_upper)		# Red is bilateral

        # Refine Masks	
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        red_mask = cv2.erode(red_mask,kernel)	
        red_mask = cv2.dilate(red_mask,kernel)
        #green_mask = cv2.erode(green_mask,kernel)
        #green_mask = cv2.dilate(green_mask,kernel)
	
        # Determine bounding box and contours - note that top left of image is (0,0)
        #g_contours,_ = cv2.findContours(green_mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        r_contours,_ = cv2.findContours(red_mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #pos = np.array([[None,None],[None,None]])
        #if len(g_contours) is not 0:
        #	c = max(g_contours,key=cv2.contourArea)
        #	x,y,width,height = cv2.boundingRect(c)
        #	color = (0,255,0)
        #	cv2.rectangle(image,(x,y),(x+width,y+height),color,2)
        #	pos[0] = (x+width/2,y+height/2)
        #	cv2.putText(image,str(pos[0]),(int(x+width+10),int(y)+10),cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)
        if len(r_contours) is not 0:
                c = max(r_contours,key=cv2.contourArea)
                x,y,width,height = cv2.boundingRect(c)
                color = (0,0,255)
                cv2.rectangle(image,(x,y),(x+width,y+height),color,2)
                x1 = int(x)
                y1 = int(y)
                x2 = int(x+width)
                y2 = int(y+height)
                #pos[1] = (x+width/2,y+height/2)
                ctr = (x1+x2)/2 - img_w/2, img_h/2 - (y1+y2)/2 
                #cv2.putText(image,str(pos[1]),(int(x+width+10),int(y)+10),cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)
        return image, ctr
