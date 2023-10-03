import urx
import numpy as np

class RobotController():
    # tcp as entry
    def __init__(self, x, y, z):
        # self.gravity = 0
        self.tcp_x = x
        self.tcp_y = y
        self.tcp_z = z
        self.payload = 0
        self.tcp = [self.tcp_x, self.tcp_y, self.tcp_z, 0, 0, 0]   
        self.rob = urx.Robot("192.168.0.100", use_rt=True)

    # set tcp, payload and gravity
    def initialize(self, payload):
        self.payload = payload
        self.rob.set_tcp(self.tcp)
        self.rob.set_payload(self.payload, (0, 0, 0.1))
        self.rob.set_gravity((0, 0, 9.81))    

    # move to start position，default position
    def start_pos(self, x, y, z):
        tmpj = self.rob.getj()
        tmp1 = tmpj[0]
        tmp5 = tmpj[5]
        tmpj = (np.array(tmpj) //10 + 0.5) * np.pi
        tmpj[0] = tmp1
        tmpj[5] = tmp5
        self.rob.movej(tmpj, 0.1, 0.09)
        pose = self.rob.getl()
        rx, ry, rz = pose[3:]
        # define target pose
        # 0.250, 0.180, 0,3
        target_pose = [x, y, z, rx, ry, rz]  # [x, y, z, rx, ry, rz]
        # 
        self.rob.movel(target_pose, acc=0.1, vel=0.1)  #
        return tmpj

    # size of reference/photographic plate
    # w: width
    # h: height
    def adjust(self, w, h):
        tmp = self.rob.getl()
        x = tmp[0]
        y = tmp[1]
        z = tmp[2]
        rx = tmp[3] 
        ry = tmp[4] 
        rz = tmp[5] 
        w = w/1000
        h = h/1000
        for i in range(2):
            self.rob.movel([x, y, z, rx, ry, rz], 0.04, 0.02)
            self.rob.movel([x+w, y, z, rx, ry, rz], 0.04, 0.02)
            self.rob.movel([x+w, y+h, z, rx, ry, rz], 0.04, 0.02)
            self.rob.movel([x, y+h, z, rx, ry, rz], 0.04, 0.02)
        self.rob.movel([x, y, z, rx, ry, rz], 0.04, 0.02)
        return [x,y,z]
 
    # to adjust the height of Robot
    # h: Height of Robot
    def height_adjust(self, h):
        pose = self.rob.getl()
        pose[2] = h
        self.rob.movel(pose, 0.04, 0.02)

    # transformation of coordinate 
    def transformation(self, contour):
        pose = self.rob.getl()
        x_b, y_b = pose[:2]

        # m2img = ((0,1),(1,0)) # transformation matrix

        # Transformation von Pixel in Roboterkoordinaten
        path = [[x_b+point[1], y_b+point[0]] for point in contour]
        return path

    # move along the contour
    # path: a series of points
    # z: Height Robot
    def move_to(self, path: list, z):
        pose = self.rob.getl()
        rx, ry, rz = pose[3:]
        self.rob.movel([path[0][0], path[0][1], z, rx, ry, rz], 0.5, 0.05)

        for i in range(len(path)):
            self.rob.movel([path[i][0], path[i][1], z, rx, ry, rz], 0.02, 0.01)
            print (i+1)
        self.rob.movel([path[0][0], path[0][1], z, rx, ry, rz], 0.02, 0.01)

        self.rob.movel([0.3, 0.2, 0.3, rx, ry, rz], 0.05, 0.05) # back to Point (0.3, 0.2, 0.3)
        print ('finished')
