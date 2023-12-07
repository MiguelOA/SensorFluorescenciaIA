import picamera


with picamera.PiCamera() as camera:
	
	camera.framerate = 30
	camera.clock_mode = 'raw'
	camera.start_preview()
	camera.start_recording('video.h264', format='h264', sps_timing=True, bitrate=25000000)
	zero = camera.timestamp
	for i in range(10):
		print(camera.timestamp - zero)
		camera.wait_recording(1)
	camera.stop_recording()
	camera.stop_preview()
	camera.close()
