# Robomaster Armour Detector
This detector is intended to locate the center of the robot's armour panel. It works reasonably well given the panel is facing directly at the camera and the camera is not tilted. It struggles in situations where the LED strips are not vertical or are obstructed.

### Run 
```
python detectArmour_image.py -i dataset/RoboMasterLabelledImagesSet1/image-550.jpg --save ./output/
```

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