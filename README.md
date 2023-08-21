# RoboGlue1
The aim of the project is to use robotics and computer vision to detect and track the edges of paper fragments. It focuses on analysing the images captured by the camera through computer vision and converting the coordinate information of the pictures into information that can be understood by the robot through coordinate transformation.

Team Members:
```
Huaiyi Dai
Ruoxiao Wang
Hui Wang
Heng Zhang
```

# Used Packages
Here are all the packages required for this project:
```python
import cv2
import numpy as np
import glob
from matplotlib import pyplot as plt
import os
import urx
from pypylon import pylon
```

# Example use -> General steps 
## 1. Calibration of Camera
Basler Camera will be used to capture the pictures  
First calibrate the camera
```python
# load the images for camera calibration
calibration_images = img_processor.load_images("calibration/")
size = len(calibration_images) # number of images
mtx, dist, newcameramtx = camera_calibration.calibrator(size) # calibration parameters
```

## 2. Load the Images 
The images will be loaded and processed
## 2.1 Instance and load the Images
```python
# size of reference
w = 240 # width
h = 170 # heigth
img_processor = image_process.ImageProcessor(w, h) # instance of ImageProcesser()
images = img_processor.load_images("src/") # load the image to be processed
```
## 2.2 Correction of Distorted Images
```python
corrected_images = camera_calibration.correct_distortion(images, mtx, dist, newcameramtx)
```

## 2.3 Get the inner Contour
```python
# usually the inner contour is the contour we want
con_list = img_processor.contour_for_robot(corrected_images, scale)
# select an image, or skip this step if there is only one image
con = con_list[index]
con = [ele/scale/1000 for ele in con]
```

## 3. Instance of Robot
```python
robot_controller = controller.RobotController(0,0,0.08) # the tcp piont (0, 0, 0.08) in metre
robot_controller.initialize(2) # payload 2 in kg
```
## 3.1 Move to the Default Start Position
```python
robot_controller.start_pos() # Default start position
```

## 3.2 Transformation and Move along the Contour
```python
path = robot_controller.transformation(con) # coordinaten transformation from image to robot
robot_controller.move_to(path) # Robot moves along a path
```


# Specific Modul and Classes
## Modul camera_calibration
The purpose of these functions is to perform camera calibration, compute distortion parameters, and correct distortion in images.
```python
calibrator(n)
    Parameters:
        n: An integer representing the number of images to process.

para_stu(n)
distortion parameter
    Parameters:
        n: An integer representing the number of images to process.

correct_distortion(images, mtx, dist, newcameramtx)
    Parameters:
        images: A list of images.
        mtx: The intrinsic matrix of the camera.
        dist: Distortion coefficients of the camera.
        newcameramtx: The optimized camera matrix.
```

## ImagePreocessor
```python
init(self, w, h)
    Parameters:
        w: Width of the reference.
        h: Height of the reference.

load_images(self, path: str) -> list
    Parameters:
        path: Directory path of the images.

display_images(self, images: list, figsize=(15, 4))
    Parameters:
        images: List of images to display.
        figsize: Size of the displayed image.

get_contours(self, image)
    Parameters:
        image: Image on which contours are to be detected.

kmeans(self, image, clusters: int) -> any
    Parameters:
        image: Image to perform k-means clustering on.
        clusters: Number of clusters.

preprocess(self, image) -> any
    Parameters:
        image: Image to preprocess.

bounding_rect(self, image, filter)
    Parameters:
        image: Image to draw bounding rectangles on.
        filter: Filter parameter.

reorder(self, myPoints)
    Parameters:
        myPoints: Points to reorder.

warp_img(self, image: any, points: any, w, h, pad = 10) -> any
    Parameters:
        image: Image to perform perspective transformation on.
        points: Reference points for perspective transformation.
        w: Width of the reference.
        h: Height of the reference.
        pad: Padding size.

find_internal_conturs(self, image: any, threshold: int, scale: float)
    Parameters:
        image: Image to find internal contours on.
        threshold: Threshold value.
        scale: Scale factor.

display_contour(self, image: any, contour, area)
    Parameters:
        image: Image to be displayed.
        contour: Contour to display.
        area: Area of the contour.

approx_contour(self, contour)
    Parameters:
        contour: Contour to approximate.

display_approx_contour(self, image: any, approx_contour) -> list
    Parameters:
        image: Image to be displayed.
        approx_contour: Contour to display.

```

## RobotController
The purpose of this class is to control a robot to enable it to move along a given contour.
More details about Python-urx, https://github.com/SintefManufacturing/python-urx
```python
init(self, x, y, z)
    Parameters:
        x: Position of the TCP (Tool Center Point) on the x-axis.
        y: Position of the TCP on the y-axis.
        z: Position of the TCP on the z-axis.

initialize(self, payload)
    Parameters:
        payload: Payload of the robot.

start_pos(self)
    Parameters: None

transformation(self, contour)
    Parameters:
        contour: A list of points that define a contour.

move_to(self, contour)
    Parameters:
        contour: A list of points that define a contour.


```



