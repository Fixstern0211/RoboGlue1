import cv2
import numpy as np
import glob
from matplotlib import pyplot as plt
import os

def ls(path):
    files =  os.listdir(path)
    return [os.path.join(path,x) for x in files]

def getContours(img):
    kernel = np.ones((5,5))
    img = cv2.Canny(img,50,150) #minVal, maxVal
    img = cv2.dilate(img,kernel,iterations=3) #dilatieren
    img = cv2.erode(img,kernel,iterations=2) #erodieren
    return img

def kmeans(img, k):
    data = img.reshape((-1,2))
    data = np.float32(data)
    criteria = (cv2.TERM_CRITERIA_EPS +
                cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_PP_CENTERS
    compactness, labels, centers = cv2.kmeans(data, k, None, criteria, 10, flags)
    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    dst = res.reshape((img.shape))
    return dst

def vorbe(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows,cols = img.shape[:2]
    for row in range(rows):
        for col in range(cols):
            if img[row,col] > 190:
                img[row,col] = 190
    img = cv2.medianBlur(img,5)
    img = cv2.bilateralFilter(img, d = 100, sigmaColor= 20, sigmaSpace= 100)
    k_img = kmeans(img, 3)
    c_img = cv2.Canny(k_img,100,110)
    kernel = np.ones((5,5))
    c_img = cv2.dilate(c_img,kernel,iterations=3) #dilatieren
    c_img = cv2.erode(c_img,kernel,iterations=2) #erodieren
    return c_img

def boundingRect(img, filter):
    contours, hiearchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    finalCountours = []
    area_list = []
    for i in contours:
        area = cv2.contourArea(i)
        if area> 100: #minimale Fläche
            area_list.append(area)
            peri = cv2.arcLength(i,True)
            appprox = cv2.approxPolyDP(i,0.02*peri,True)
            bbox = cv2.boundingRect(appprox)
            if filter > 0 :
                if(len(appprox))==filter:
                    finalCountours.append([len(appprox),area,appprox,bbox,i])
            else:
                finalCountours.append([len(appprox),area,appprox,bbox,i])
    finalCountours = sorted(finalCountours, key=lambda x: x[1], reverse=True)
    for con in finalCountours:
        cv2.drawContours(img, con[4], -1, 255, 3)
    maxArea = np.max(area_list)
    return img, finalCountours, maxArea

def reorder(myPoints):
    myPointsNew = np.zeros_like(myPoints)
    myPoints = myPoints.reshape((4,2))
    add = myPoints.sum(1)
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints,axis=1)
    myPointsNew[1]= myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    return myPointsNew

def warpImg (img,points,w,h,pad=10):
    points =reorder(points)
    pts1 = np.float32(points)
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    imgWarp = cv2.warpPerspective(img,matrix,(w,h))
    imgWarp = imgWarp[pad:imgWarp.shape[0]-pad,pad:imgWarp.shape[1]-pad]
    return imgWarp

def print_inner_cons(img, th, scale):
    contours, hiearchy = cv2.findContours(img,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    contours = [ele for ele in contours if cv2.contourArea(ele) > th * scale**2]
    area_list = [cv2.contourArea(ele) / scale**2 for ele in contours]
    index = np.argmin(area_list)
    mask = np.zeros_like(img)
    cv2.drawContours(mask, contours[index], -1, 255, 3)
    plt.imshow(mask, cmap = "gray")
    plt.title("Größe= %1.2f mm" % area_list[index])
    plt.axis('off')
    return contours[index]

def print_approx_cons(img, th, scale):
    contours, hiearchy = cv2.findContours(img,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    contours = [ele for ele in contours if cv2.contourArea(ele) > th * scale**2]
    
    area_list = [cv2.contourArea(ele) / scale**2 for ele in contours]
    index = np.argmin(area_list)
    epsilon = 0.01*cv2.arcLength(contours[index],True)

    # print (index)
    mask = np.zeros_like(img)
    approx = cv2.approxPolyDP(contours[index], epsilon, True)
    cv2.drawContours(mask, approx, -1, 255, 3)
    plt.imshow(mask, cmap = "gray")
    plt.title("approxPolyDP")
    plt.axis('off')
    return approx