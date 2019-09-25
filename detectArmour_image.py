# import the necessary packages
from shapeDetector import ShapeDetector
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
	path = args["save"] + '/' + imgName + '.jpg'
	cv2.imwrite(path, img)

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
image = cv2.imread(args["image"])
image = imutils.resize(image, width=600)
 
# find saliency map of image, then threshold the LEDs
saliency = cv2.saliency.StaticSaliencyFineGrained_create()
(success, saliencyMap) = saliency.computeSaliency(image)
saliencyMap = (saliencyMap * 255).astype("uint8")

cv2.imshow("saliency", saliencyMap)
cv2.waitKey(0)

thresh = cv2.threshold(saliencyMap.astype("uint8"), 210, 255,
	cv2.THRESH_BINARY)[1]

cv2.imshow("thresh", thresh)
cv2.waitKey(0)
 
# find contours in the thresholded image 
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# initialize shape detector, rectangle count, and list of rectangle 
# coordinates
sd = ShapeDetector()
numRect = 0
rectangles = []

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
	# increase the rectangle count
	if shape == "rectangle":
		c = c.astype("float")
		c = c.astype("int")
		cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
		numRect += 1
		coord = [cX, cY]
		rectangles.append(coord)

		# show the output image
		cv2.imshow("Image", image)
		cv2.waitKey(0)
    
	if numRect == 2: 
		# average the two rectangles' center coordinates
		targetcX = int((rectangles[0][0] + rectangles[1][0]) / 2.0)
		targetcY = int((rectangles[0][1] + rectangles[1][1]) / 2.0)
		cv2.circle(image, (targetcX, targetcY), 3, (0, 255, 0), -1)
		cv2.putText(image, "center", (targetcX-25, targetcY+20), 
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		# show the output image
		cv2.imshow("Image", image)
		cv2.waitKey(0)
		saveToDisk(image, "target")
