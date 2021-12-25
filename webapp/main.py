#Writer: suyeon woo
#Date: 21.12.18
from flask import Flask, render_template, Response, request
from camera import VideoCamera
from gpio import Gpio
from configparser import ConfigParser
import time
import os
import io
import datetime as dt
import boto3
import json
import threading

#config
config = ConfigParser()
config.read('configuration.ini')

AWS_ACCESS_KEY_ID = config['aws_conf']['ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['aws_conf']['SECRET_ACCESS_KEY']
AWS_S3_BUCKET_NAME = config['aws_conf']['S3_BUCKET_NAME']

is_speeching = False    # speeching y/n
led_port = 23			# led output port

# picamera
pi_camera = VideoCamera(resolution=(1280, 720), flip=False)
# gpio
gpio = Gpio()
gpio.set_outport(port=led_port)


app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')


def gen(camera):
	#get camera frame
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
	return Response(gen(pi_camera), mimetype='multipart/x-mixed-replace; boundary=frame')


# Send data to s3 every 5 seconds when start speeching
@app.before_first_request
def capture():
	def run():
		global is_speeching

		print(f'is_speeching : {is_speeching}')
		while is_speeching:
			file_name = 'capture_{}.jpg'.format(dt.datetime.now().strftime('%Y%m%d_%H%M%S'))

			frame = pi_camera.get_frame()
			data = io.BytesIO(frame)
			print(f'capture frame : {data}')
			
			s3_client = boto3.client('s3',
					aws_access_key_id = AWS_ACCESS_KEY_ID,
					aws_secret_access_key = AWS_SECRET_ACCESS_KEY
					)
			response = s3_client.upload_fileobj(data, AWS_S3_BUCKET_NAME, file_name, ExtraArgs={"ContentType": "image/jpeg"})
			print(f's3 upload successful : {file_name}')

			time.sleep(5)

	thread = threading.Thread(target=run)
	thread.start()


# Start and end of speech
@app.route('/speech', methods=['POST'])
def speech():
	param_action = request.json['action']
	print(f'param action : {param_action}')

	global is_speeching

	if param_action == 'START':
		is_speeching = True
		capture()
	else:
		is_speeching = False
		capture()

	return Response(status=200)


# Called by lambda when more than half of listeners are sleeping
@app.route('/led')
def turn_led():
	gpio.led_on(port=led_port, sec=3)		# LED on for 3 seconds

	return Response(status=200)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

