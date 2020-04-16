import smbus
import time
from picamera import PiCamera

bus = smbus.SMBus(1)
i2c_add = 0x04
m_speed = 100
camera = PiCamera(resolution=RESOLUTION, framerate=FRAME_RATE)
frame = PiRGBArray(camera, RESOLUTION)
camera.start_preview()
time.sleep(.5)
print("Initiated")

try:
	i = 0
	while 1:
		mode = input("Drive Command: ")
		if mode == 'a':
			drive_state = 0
		elif mode == 'w':
			drive_state = 1
		elif mode == 'd':
			drive_state == 2
		else:
			drive_state = 3
		duration = input('Enter Duration of drive: ')
		bus.write_i2c_block_data(i2c_add, 1, [m_speed, m_speed, drive_state])
		time.sleep(duration)
		bus.write_i2c_block_data(i2c_add, 0, [m_speed, m_speed, drive_state])
		camera.capture('images/img' + i + '.jpg', format='rgb', use_video_port=True)
		heading = input('Enter Drive Heading: ')
		with open('images/headings.txt', a+) as f:
			f.write(heading + ',')
		i += 1
		
except:
	print("Quiting")
