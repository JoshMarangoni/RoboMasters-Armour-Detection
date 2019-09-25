# Robomaster Armour Detector
This detector can locate the center of a target given an image or the robot. I have not tested this extensively but seems to work fine for typical cases.

### Method

- use saliency to bring out the important parts of the image
- threshold the image at 210 pixels to isolate the strips
- use a shape detector to find the rectangular LED strips
- find the center coordinates of the rectangular LED strips
- find the center of the target using the two LED strips on the sides of the target


### Output
<p align="center">
  <br>
  <img src="target.jpg" width="500">
</p>