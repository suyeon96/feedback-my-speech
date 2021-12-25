#Writer: suyeon woo
#Date: 21.12.18
import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

class VideoCamera(object):
	def __init__(self, resolution=(320, 240), flip = False):
		self.vs = PiVideoStream(resolution=resolution).start()
		self.flip = flip
		time.sleep(2.0)

	def __del__(self):
		self.vs.stop()

	def flip_if_needed(self, frame):
		if self.flip:
			return np.flip(frame, 0)
		return frame

	def get_img_frame(self):
		frame = self.flip_if_needed(self.vs.read())
		return frame

	# Encodes an image into a memory buffer
	def get_frame(self):
		frame = self.flip_if_needed(self.vs.read())
		ret, jpeg = cv2.imencode('.jpg', frame)
		return jpeg.tobytes()
