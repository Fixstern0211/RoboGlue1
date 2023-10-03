import numpy as np
import glob
import cv2
import os

def calibrator(n):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    w = 9   # 10 - 1
    h = 6   # 7  - 1
    objp = np.zeros((w*h,3), np.float32)
    objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
    objp = objp*18.1  # 18.1 mm
    objpoints = []
    imgpoints = []
    # images_k = glob.glob(r'calibration/*.png')
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get parent directory
    parent_dir = os.path.dirname(script_dir)
    # Build a path to the 'calibration' directory
    path = os.path.join(parent_dir, 'calibration')
    # path = "f:/TUB/SS/SS23/APJ/RoBOGlueI/RoBOGlueI/calibration/"
    files = os.listdir(path)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    images_k = [os.path.join(path, x) for x in files if os.path.isfile(os.path.join(path, x)) and os.path.splitext(x)[1].lower() in image_extensions]

    i=0
    for fname in images_k[:n]:
        img = cv2.imread(fname)
        h1, w1 = img.shape[0], img.shape[1]
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        u, v = img.shape[:2]
        ret, corners = cv2.findChessboardCorners(gray, (w,h),None)
        if ret == True:
            # print("i:", i)
            i = i+1
            cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            objpoints.append(objp)
            imgpoints.append(corners)
            cv2.drawChessboardCorners(img, (w,h), corners, ret)
            cv2.namedWindow('findCorners', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('findCorners', 640, 480)
            cv2.imshow('findCorners',img)
            cv2.waitKey(200)
    cv2.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = \
        cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
    return mtx, dist, newcameramtx

# distortion parameters 
def para_stu(n):
    x = []
    cam = []
    y = np.linspace(3,n,n-2)
    for i in range(3,n+1):
        mtx,dist, newcameramtx = calibrator(i)
        x.append(dist[0])
        cam.append([newcameramtx[0][0], newcameramtx[1][1], newcameramtx[0][2], newcameramtx[1][2]])
    return x,y,cam

# Correcting distortion
# mtx: Camera matrix
# dist: distortion parameter
def correct_distortion(images: list, mtx, dist, newcameramtx) -> list:
    dst = []
    for ele in images:
        tmp = cv2.undistort(ele, mtx, dist, None, newcameramtx)
        dst.append(tmp)
    return dst
    