import cv2
import numpy as np
import glob
from matplotlib import pyplot as plt
import os

class ImageProcessor:
    # Create Instance
    def __init__(self, w, h):
        #self.criteria w = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        #self.w = 9   # 10 - 1
        #self.h = 6   # 7  - 1
        #self.objp = np.zeros((self.w*self.h,3), np.float32)
        #self.objp[:,:2] = np.mgrid[0:self.w,0:self.h].T.reshape(-1,2)
        #self.objp = self.objp*18.1  # 18.1 mm
        self.filter = 0
        # size of the reference
        self.w = w # width
        self.h = h # heigth

    # read from folder
    def load_images(self, path: str) -> list:
        """Load images from a specified directory"""
        # 获取当前脚本的目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取上级目录
        parent_dir = os.path.dirname(script_dir)
        # 构建指向'calibration'目录的路径
        path = os.path.join(parent_dir, path)
        files = os.listdir(path)

        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        images_files = [os.path.join(path, x) for x in files if os.path.isfile(os.path.join(path, x)) and os.path.splitext(x)[1].lower() in image_extensions]
        images = [cv2.imread(image, 1)[:,:,::-1] for image in images_files]
        return images

    # show images
    def display_images(self, images: list, figsize=(15, 4)):
        """Display image list"""
        fig = plt.figure(figsize=figsize)
        for i, image in enumerate(images):
            if len(images) > 5:
                fig.add_subplot(3, 9, i+1)
                plt.imshow(image, cmap="gray")
                plt.axis('off')

            else:
                fig.add_subplot(1, 5, i+1)
                plt.imshow(image, cmap="gray")
                plt.axis('off')
        plt.show()


    # detect contours
    def get_contours(self, image):
        kernel = np.ones((5,5))
        image = cv2.Canny(image,50,150) #minVal, maxVal
        image = cv2.dilate(image,kernel,iterations=3) #dilatieren
        image = cv2.erode(image,kernel,iterations=2) #erodieren
        return image

    # k-means
    def kmeans(self, image, clusters: int) -> any:
        data = image.reshape((-1,2))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_PP_CENTERS
        compactness, labels, centers = cv2.kmeans(data, clusters, None, criteria, 10, flags)
        centers = np.uint8(centers)
        res = centers[labels.flatten()]
        dst = res.reshape((image.shape))
        return dst

    # preprocessing
    def preprocess(self, image) -> any:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rows,cols = img.shape[:2]
        for row in range(rows):
            for col in range(cols):
                if img[row,col] > 190:
                    img[row,col] = 190
        img = cv2.medianBlur(img,5)
        img = cv2.bilateralFilter(img, d = 100, sigmaColor= 20, sigmaSpace= 100)
        k_img = self.kmeans(img, 3)
        c_img = cv2.Canny(k_img,100,110)
        kernel = np.ones((5,5))
        c_img = cv2.dilate(c_img,kernel,iterations=3) #dilatieren
        c_img = cv2.erode(c_img,kernel,iterations=2) #erodieren
        return c_img

    
    # bounding rect
    def bounding_rect(self, image, filter):
        # self.filter = filter
        contours, hiearchy = cv2.findContours(image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        finalCountours = []
        area_list = []
        for i in contours:
            area = cv2.contourArea(i)
            if area > 100: # min. area 100
                area_list.append(area)
                peri = cv2.arcLength(i,True)
                appprox = cv2.approxPolyDP(i,0.02*peri,True)
                bbox = cv2.boundingRect(appprox)
                if self.filter > 0 :
                    if(len(appprox)) == self.filter:
                        finalCountours.append([len(appprox),area,appprox,bbox,i])
                else:
                    finalCountours.append([len(appprox),area,appprox,bbox,i])
        finalCountours = sorted(finalCountours, key=lambda x: x[1], reverse=True)
        for contour in finalCountours:
            cv2.drawContours(image, contour[4], -1, 255, 3)
        maxArea = np.max(area_list)
        return image, finalCountours, maxArea

    # reorder
    def reorder(self, myPoints):
        myPointsNew = np.zeros_like(myPoints)
        myPoints = myPoints.reshape((4,2))
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] = myPoints[np.argmax(add)]
        diff = np.diff(myPoints,axis=1)
        myPointsNew[1]= myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]
        return myPointsNew


    # Calculate the actual size of the piece of paper
    def warp_img(self, image: any, points: any, w, h, pad = 10) -> any:
        # self.points = points
        # scale = 4
        # size of the reference
        # wp=w*scale
        # hp =h*scale
        points =self.reorder(points)
        pts1 = np.float32(points)
        pts2 = np.float32([[0,0], [w,0], [0,h], [w,h]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        # imgWarp = cv2.warpPerspective(image,matrix,(int(w), int(h)))
        imgWarp = cv2.warpPerspective(image,matrix,(w, h))
        imgWarp = imgWarp[pad:imgWarp.shape[0]-pad, pad:imgWarp.shape[1]-pad]
        return imgWarp

    # find the min. area(internal contours)
    def find_internal_conturs(self, image: any, threshold: int, scale: int):
        contours, hiearchy = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        contours = [ele for ele in contours if cv2.contourArea(ele) > threshold * scale**2] # filter the contours
        area_list = [cv2.contourArea(ele) / scale**2 for ele in contours] # area for each contour
        index = np.argmin(area_list) # find out the min. contour (internal contours) 
        return contours[index], area_list[index]
        
    # show internal contours
    def display_contour(self, image: any, contour, area):
        fig=plt.figure(figsize=(10, 15))
        mask = np.zeros_like(image)
        cv2.drawContours(mask, contour, -1, 255, 3)
        plt.imshow(mask, cmap = "gray")
        plt.title("Größe= %1.2f mm" % area)
        plt.axis('off')
        
    # approximate contour
    def approx_contour(self, contour):
        epsilon = 0.002*cv2.arcLength(contour,True) # experience value
        # print(epsilon)
        approx_contour = cv2.approxPolyDP(contour, epsilon, True)
        return approx_contour


    # print an approximate contours
    def display_approx_contour(self, image: any, approx_contour) -> list:
        """show an approximate contours"""
        fig=plt.figure(figsize=(10, 5))
        # mask = np.zeros_like(image)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)

        cv2.drawContours(mask, approx_contour, -1, 255, 3)
        plt.imshow(mask, cmap = "gray")
        plt.title("approxPolyDP")
        plt.axis('off')


    def contour_for_robot(self, corrected_images: any, scale) -> list:
        images = []
        contours = []
        areas = []
        appro_contours_list = []
        filter = 4
        for i in range(len(corrected_images)):

            c_img = self.preprocess(corrected_images[i])
            imgcon, cons, maxArea = self.bounding_rect(c_img, filter)
            maxbox = cons[0][2]
            self.reorder(maxbox)
            w_img = self.warp_img(corrected_images[i], maxbox, self.w*scale, self.h*scale)
            
            w1_img = cv2.medianBlur(w_img, 5)
            w2_img = cv2.bilateralFilter(w1_img, d = 50, sigmaColor= 10, sigmaSpace= 50)

            k2_img = self.kmeans(w2_img, 3)

            c2_img = cv2.Canny(k2_img, 100, 110)
            kernel = np.ones((5,5))
            c2_img = cv2.dilate(c2_img, kernel, iterations=2) #dilatieren
            c2_img = cv2.erode(c2_img, kernel, iterations=1) #erodieren
            images.append(c2_img)

            # display contours and aprroximate contours
            # contour
            contour, area = self.find_internal_conturs(c2_img, 1000, scale) # arguments: image, threshold, scale
            contours.append(contour)
            areas.append(area)

            # approximate contours
            approx_contour = self.approx_contour(contour) # size 3 dimension [[[]]]
        
            #
            # approx_contour = np.squeeze(approx_contour, axis=1) # size 2 dimension [[]]
            appro_contours_list.append(approx_contour)

        # contours_list = np.squeeze(contours_list, axis=1) 
        return images, contours, areas, appro_contours_list

# exsample：
# img_processor = image_process.ImageProcessing()
# images = img_processor.load_images("kalibrierung/")
# img_processor.display_images(images)
