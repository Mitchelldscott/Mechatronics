import argparse
from LuxonisFunctions import * # Custom functions to make more readable
import rospy
from std_msgs.msg import String

'''
Script for getting the location relative to the center of the image of the bad guy targets
Utilizes custom nn to recognize target offloaded to Luxonis 

'''
def talker(status):
	pub = rospy.Publisher("enabled",String,queue_size=10)
	rospy.init_node('talker',anonymous=True)
	rate = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		if status is not None:		
			status = "DISABLE"
		else:
			status = "ENABLE"		
		rospy.loginfo(status)
		pub.publish(status)
		rate.sleep()

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
		try:	
			talker(data) # ROS function		
		except rospy.ROSInterruptExeption:
			pass
		#if data is not None:
			#if data 
			# ser0.print(command)
	

	
