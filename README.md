# RoboGlue1
The aim of the project is to use robotics and computer vision to detect and track the edges of paper fragments. It focuses on analysing the images captured by the camera through computer vision and converting the coordinate information of the pictures into information that can be understood by the robot through coordinate transformation.

Team Members:
Huaiyi Dai
Ruoxiao Wang
Hui Wang
Heng Zhang

# 1. calibration of camera
Basler Camera will be used to capture the pictures
First calibrate the camera
'''python
calibration_images = img_processor.load_images("calibration/")
size = len(calibration_images)
mtx, dist, newcameramtx = camera_calibration.calibrator(size)
'''

# 2. load the images 
the images will be loaded and processed
## 2.1 correction of distorted images
'''python
corrected_images = camera_calibration.correct_distortion(images, mtx, dist, newcameramtx)

'''
## 2.2 get the internal contour
'''python
con_list = img_processor.contour_for_robot(corrected_images, scale)
<!-- select a image -->
con = con_list[index]
con = [ele/scale/1000 for ele in con]
'''

# 3. instance of robot
'''python
robot_controller = controller.RobotController(0,0,0.08)
robot_controller.initialize(2) # payload 2
'''
## 3.1 
'''python
robot_controller.start_pos() # Default start position
'''

## 3.2 move along the contour
'''python
path = robot_controller.transformation(con)
robot_controller.move_to(path)
'''