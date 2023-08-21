import urx
import numpy as np

class RobotController():
    def __init__(self, x, y, z):
        # self.gravity = 0
        self.tcp_x = x
        self.tcp_y = y
        self.tcp_z = z
        self.payload = 0
        self.tcp = [self.tcp_x, self.tcp_y, self.tcp_z, 0, 0, 0]        

    def initialize(self, payload):
        self.payload = payload
        rob = urx.Robot("192.168.0.100", use_rt=True)
        rob.set_tcp(self.tcp)
        rob.set_payload(self.payload, (0, 0, 0.1))
        rob.set_gravity((0, 0, 9.81))    

    # move to start position，default position
    def start_pos(self):
        tmpj = rob.getj()
        tmp1 = tmpj[0]
        tmp5 = tmpj[5]
        tmpj = (np.array(tmpj)*0 + 0.5) * pi
        tmpj[0] = tmp1
        tmpj[5] = tmp5
        rob.movej(tmpj, 0.1, 0.09)
        return tmpj

    # transformation of coordinate 
    def transformation(self, contour):
        pose = rob.getl()
        x_b, y_b = pose[:2]
        # x_b, y_b = [0.2, 0.2]
        b2m = (x_b, y_b) # x,y
        # print(b2m)

        m2img = ((0,1),(1,0)) # transformation matrix

        # Transformation von Pixel in Roboterkoordinaten
        new_con = [[x_b+(m2img[0][0]*ele[0]+m2img[0][1]*ele[1]), y_b+(m2img[1][0]*ele[0]+m2img[1][1]*ele[1])] for point in contour]
        return new_con

    # move along the contour
    def move_to(self, path: list):
        pose = rob.getl()
        rx, ry, rz = pose[3:]
        for i in range(len(con_new)):
            rob.movel([contour[i][0], contour[i][1], 0.1, rx, ry, rz], 0.005, 0.005)
            print ('%i. point' %i+1)
        start_pos = self.start_pos()
        rob.movel([start_pos, rx, ry, rz], 0.05, 0.05)
        print ('finished')
