import cv2
import numpy as np
import requests
from io import BytesIO
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer

# Define the HTTP request handler class
class MyHTTPRequestHandler(BaseHTTPRequestHandler):
	# Handler for GET requests
	model = load_model('keras_model.h5')
	
	base_url='http://172.20.10.2/'
	# Load the class labels from the text file
	with open('labels.txt', 'r') as f:
		labels = f.read().splitlines()
		
	def do_GET(self):
		# Set response status code
		self.send_response(200)
		# Set headers
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		# Send the response content
		self.wfile.write(b"<html><head><title>Python Web Server</title></head>")
		self.wfile.write(b"<body><h1>ESP32 Cam Python AI Server</h1></body></html>")
		# Example usage
		if self.path == '/detect':
			url = self.base_url+'cam-lo.jpg'
			self.detect_image_from_url(url)

	# Function to preprocess image
	def preprocess_img(self, img):
		img = img.resize((224, 224))  # Resize image to match model's expected sizing
		img = image.img_to_array(img)  # Convert image to numpy array
		img = np.expand_dims(img, axis=0)  # Add batch dimension
		img /= 255.  # Normalize pixel values
		return img
	
	# Function to predict image class
	def predict_image_class(self, img):
		img = self.preprocess_img(img)
		prediction = self.model.predict(img)
		return prediction
	
	# Function to detect image from URL
	def detect_image_from_url(self, url):
		response = requests.get(url)
		img = Image.open(BytesIO(response.content))
		
		# Convert PIL image to OpenCV format
		cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
	
		# Perform detection
		prediction = self.predict_image_class(img)
	
		# Get the predicted class label
		predicted_class_index = np.argmax(prediction)
		predicted_class_label = self.labels[predicted_class_index]
		print(predicted_class_label)
		predicted_class_label = predicted_class_label[2:]
		urlx=self.base_url+predicted_class_label
		response = requests.get(urlx)
		print(urlx)
		# Draw text on the image
		#cv2.putText(cv_img, predicted_class_label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
		
	
		# Display the image
		cv2.imshow('Detected Image', cv_img)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()
		
# Define the host and port
HOST = ''
PORT = 5555

# Create an instance of the HTTP server
httpd = HTTPServer((HOST, PORT), MyHTTPRequestHandler)

# Print a message indicating the server is running
print(f"Server running on {HOST}:{PORT}")

# Start the server
httpd.serve_forever()

# Load the Keras model




