
from shapeDetector import ShapeDetector
import numpy as np
import argparse
import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("--save", required=True, 
	help="Path to saved image directory")
args = vars(ap.parse_args())

def saveToDisk(img, imgName): 
	idx = imgName.find('image-')
	if args['image'][len(args['image'])-1] == '/':
		path = args["save"] + imgName[idx:]
	else: 
		path = args["save"] + '/' + imgName[idx:]
	cv2.imwrite(path, img)

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
width = 600  #seems to be optimum for shape detector
image = cv2.imread(args["image"])
image = imutils.resize(image, width=width)

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
lower_red = np.array([0,0,240])
upper_red = np.array([50,5,255])

mask = cv2.inRange(hsv, lower_red, upper_red)
res = cv2.bitwise_and(image,image, mask=mask)

cv2.imshow("mask", mask)
cv2.waitKey(0)
cv2.imshow("res", res)
cv2.waitKey(0)

gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)[1]
cv2.imshow("blurred", blurred)
cv2.waitKey(0)

cv2.imshow("thresh", thresh)
cv2.waitKey(0)
 
# find contours in the thresholded image 
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# initialize shape detector, quadrilateral count, and list of quadrilateral 
# coordinates
sd = ShapeDetector()
quadrilaterals = []

# loop over the contours
for c in cnts:
	# compute the center of the contour, then detect the name of the
	# shape using only the contour
	M = cv2.moments(c)
	if M["m00"] == 0.0:
		cX = int(M["m10"] / 0.00001)
		cY = int(M["m01"] / 0.00001)
	else:
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
	shape = sd.detect(c)
 
	# find rectangular contours,add the center coordinates to list, and 
	# increase the quadrilateral count
	#if shape == "rectangle" or shape == "pentagon":
	c = c.astype("float")
	c = c.astype("int")
	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
	coord = [cX, cY]
	quadrilaterals.append(coord)

	# show the output image
	cv2.imshow("Image", image)
	print(shape)
	cv2.waitKey(0)

print("quadrilaterals: " + str(len(quadrilaterals)))

i = 0
while i < len(quadrilaterals)-1:
	# determine if two *adjacent* quadrilaterals exist with a flat slope between them
	dx = abs(quadrilaterals[i][0] - quadrilaterals[i+1][0])
	if dx == 0:
		dx = 0.0001
	print("\ndx: " + str(dx))
	dy = abs(quadrilaterals[i][1] - quadrilaterals[i+1][1])
	if dy == 0: 
		dy = 0.0001
	print("dy: " + str(dy))

	slope = float(dy/dx)
	print("dy/dx: " + str(slope))
	print("dx/dy: " + str(dx/dy))

	# if slope is close to flat, then matching quadrilaterals found
	if slope < 0.3 and dx<1/11*width: 
		# average the two quadrilaterals' center coordinates
		targetcX = int((quadrilaterals[i][0] + quadrilaterals[i+1][0]) / 2.0)
		targetcY = int((quadrilaterals[i][1] + quadrilaterals[i+1][1]) / 2.0)
		cv2.circle(image, (targetcX, targetcY), 3, (0, 255, 0), -1)
		cv2.putText(image, "center", (targetcX-25, targetcY+20), 
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		print('CENTER')
		# show the output image
		cv2.imshow("Image", image)
		cv2.waitKey(0)
		saveToDisk(image, args['image'])
		break

	i+=1
