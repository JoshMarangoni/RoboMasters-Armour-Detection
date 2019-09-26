# usage
# python detectArmour_image.py -i dataset/RoboMasterLabelledImagesSet1/image-550.jpg --save ./

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
	idx = imgName.find('image-')
	if args['image'][len(args['image'])-1] == '/':
		path = args["save"] + imgName[idx:]
	else: 
		path = args["save"] + '/' + imgName[idx:]
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

#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#thresh = cv2.threshold(blurred, 250, 255,cv2.THRESH_BINARY)[1]

thresh = cv2.threshold(saliencyMap.astype("uint8"), 210, 255,
	cv2.THRESH_BINARY)[1]

#cv2.imshow("blurred", blurred)
#cv2.waitKey(0)

cv2.imshow("thresh", thresh)
cv2.waitKey(0)
 
# find contours in the thresholded image 
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# initialize shape detector, rectangle count, and list of rectangle 
# coordinates
sd = ShapeDetector()
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
		coord = [cX, cY]
		rectangles.append(coord)

		# show the output image
		cv2.imshow("Image", image)
		cv2.waitKey(0)

print(len(rectangles))

if len(rectangles) > 1: 
	i = 0
	while i < len(rectangles)-1:
		# determine if two rectangles exist with a flat slope between them
		dx = abs(rectangles[i][0] - rectangles[i+1][0])
		print(dx)
		dy = abs(rectangles[i][1] - rectangles[i+1][1])
		print(dy)
		slope = float(dy/dx)

		print(slope)
		print(dx/dy)

		# if slope is close to flat, then matching rectangles found
		if (slope < 0.3 or (slope > 0.7 and slope < 1.3)): 
			# average the two rectangles' center coordinates
			targetcX = int((rectangles[i][0] + rectangles[i+1][0]) / 2.0)
			targetcY = int((rectangles[i][1] + rectangles[i+1][1]) / 2.0)

			cv2.circle(image, (targetcX, targetcY), 3, (0, 255, 0), -1)
			cv2.putText(image, "center", (targetcX-25, targetcY+20), 
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

			# show the output image
			cv2.imshow("Image", image)
			cv2.waitKey(0)
			saveToDisk(image, args['image'])
			break

		i+=1
