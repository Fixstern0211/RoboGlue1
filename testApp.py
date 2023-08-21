import numpy as np
from utils import image_process, controller, camera_calibration
from matplotlib import pyplot as plt
import cv2
import urx

import tkinter as tk
from tkinter import messagebox, Entry, Label, Text
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("RoboGlue")

        # Arguments and Instance
        img_processor = None
        self.w = None
        self.h = None
        self.mtx = None
        self.dist = None
        self.newcameramtx = None
        self.contours = []
        self.appro_con_list = []
        self.corrected_images = []
        self.selected_images = []
        self.check_vars = []
        self.checkbuttons = []
        self.toast_frame = None
        self.appro_con = None

        # Create a new frame for w and h inputs
        self.first_frame = tk.Frame(self.root)
        self.first_frame.grid(row=0, column=0, padx=10, pady=50)  # Place the frame in the first row and first column

        self.label_re = Label(self.first_frame, text="Size of Reference:")  # Change root to wh_frame
        self.label_re.grid(row=0, column=0, padx=1, pady=10)

        # Input for w
        self.label_w = Label(self.first_frame, text="Enter width:")  # Change root to wh_frame
        self.label_w.grid(row=1, column=0, padx=1, pady=10)
        self.entry_w = Entry(self.first_frame)  # Change root to wh_frame
        self.entry_w.grid(row=1, column=1, padx=1, pady=10)
        # default value 240
        self.entry_w.insert(0, "240")

        # Input for h
        self.label_h = Label(self.first_frame, text="Enter heigth:")  # Change root to wh_frame
        self.label_h.grid(row=2, column=0, padx=5, pady=10)
        self.entry_h = Entry(self.first_frame)  # Change root to wh_frame
        self.entry_h.grid(row=2, column=1, padx=5, pady=10)
        # default value 170
        self.entry_h.insert(0, "170")

        # # Create a frame to hold all images
        self.sec_frame = tk.Frame(self.root)
        self.sec_frame.grid(row=0, column=1, padx=1, pady=20)  # Place the frame in the first row and third column

        # addd Canvas fragment
        # self.canvas1 = tk.Canvas(self.sec_frame, bg="white", width=300, height=200)
        # self.canvas1.grid(row=0, column=0, padx=10, pady=20)

        
        # # Create a frame to hold the labels and Button for Camera Calibration
        # sec_frame = tk.Frame(self.root)
        # sec_frame.grid(row=1, column=0, padx=10, pady=10)  # Place the frame in the fourth row and first column

        # Create a frame to hold the labels and Button for Camera Calibration
        third_frame = tk.Frame(self.root)
        third_frame.grid(row=1, column=0, padx=10, pady=10)  # Place the frame in the fourth row and first column

        # Button for Camera Calibration
        self.btn_calibrate = tk.Button(third_frame, text="Camera Calibration", command=self.calibrate_camera)
        self.btn_calibrate.grid(row=0, column=0, padx=10, pady=5)

        # Create the mtx_label and place it inside the frame
        self.mtx_label = Label(third_frame, text="", wraplength=400)
        self.mtx_label.grid(row=1, column=0, padx=10, pady=20) # Use pack to place it inside the frame

        # Create the dist_label and place it inside the frame
        self.dist_label = Label(third_frame, text="", wraplength=400)
        self.dist_label.grid(row=2, column=0, padx=10, pady=20) # Use pack to place it below the mtx_label inside the frame

        
        # # Create a frame to hold Button for load and correct
        fourth_frame = tk.Frame(self.root)
        fourth_frame.grid(row=1, column=1, padx=10, pady=10)  # Place the frame in the fourth row and first column

        # Button for Images Load and Correct
        self.btn_load_correct = tk.Button(fourth_frame, text="Images Load and Correct", command=lambda: root.after(1000, self.load_correct))
        self.btn_load_correct.grid(row=0, column=0, padx=10, pady=20)

        # Button for Images Load and Correct
        
        self.btn_process = tk.Button(fourth_frame, text="Images Process", command=lambda: root.after(1000, self.process))
        self.btn_process.grid(row=0, column=1, padx=100, pady=20)

        # Button for robot
        self.btn_init_robot = tk.Button(fourth_frame, text="Start Pos", command=lambda: root.after(1000, self.init_robot))
        self.btn_init_robot.grid(row=0, column=2, padx=100, pady=20)

        # Button for movw 
        self.btn_move = tk.Button(fourth_frame, text="move", command=lambda: root.after(1000, self.move(self.contour)))
        self.btn_move.grid(row=1, column=2, padx=100, pady=20)

        # 添加Canvas小部件
        self.canvas = tk.Canvas(fourth_frame, bg="white", width=300, height=200)
        self.canvas.grid(row=1, column=1, padx=10, pady=20)

        


    # function
    def calibrate_camera(self):
        # script_dir = os.path.dirname(os.path.realpath(__file__))
        # calibration_path = os.path.join(script_dir, 'calibration/')
        # calibration_images = self.img_processor.load_images(calibration_path)
        mtx, dist, newcameramtx = camera_calibration.calibrator(27)
        self.mtx = mtx
        self.dist = dist
        self.newcameramtx = newcameramtx
        # display mtx and dist
        # self.mtx_label.config(text=f"mtx: {self.mtx}")
        # self.dist_label.config(text=f"dist: {self.dist}")
        rows = self.mtx.shape[0]
        formatted_mtx = "["
        for i in range(rows):
            row_str = ", ".join([f"{item:.3f}" for item in self.mtx[i]])
            formatted_mtx += f"  [{row_str}]"
            if i < 2:
                formatted_mtx += f"\n"

        formatted_mtx += " ]"
        self.mtx_label.config(text=f"matrix: {formatted_mtx}")

        # messagebox.showinfo("Info", "calibrate succesful!")
        self.show_toast("Calibrate Succesful!")

    def select_image(self, var):
        selected_indices = [index for index, var in enumerate(self.check_vars) if var.get()]
        # Add the selected image to the list
        self.selected_images = []

        if not selected_indices: # if no selected images
            self.canvas.delete(tk.ALL)
            self.show_toast(f"No Selected Image")
            for idx, chk in enumerate(self.checkbuttons):
                chk.config(state=tk.NORMAL)
        else:
            # messagebox.showinfo("Selected image indices:", selected_indices)
            self.show_toast(f"Selected Image {selected_indices}")

            for index in selected_indices:
                self.selected_images.append(self.corrected_images[index])
                for idx, chk in enumerate(self.checkbuttons):
                    if idx != index:
                        chk.config(state=tk.DISABLED)
                    else:
                        chk.config(state=tk.NORMAL)

        # print(f"Image selected! Index: {index}")
        # Create a frame to hold all images
        select_frame = tk.Frame(self.root)
        select_frame.grid(row=1, column=2)  # Place the frame in the first row and third column
        desired_size = (100, 100)

        # Display all corrected_images
        # for index, img in enumerate(self.selected_images):
        #     pil_img = Image.fromarray(img)  # Convert numpy array to PIL Image
        #     pil_img_resized = pil_img.resize(desired_size, Image.LANCZOS)  # Resize the image
        #     tk_img = ImageTk.PhotoImage(pil_img_resized)
            
        #     # label = tk.Label(root, image=tk_img)
        #     label = tk.Label(select_frame, image=tk_img, padx=5, pady=2)

        #     label.image = tk_img
        #     label.grid(row=3, column=index)
            
            # Add mouse click event to each image
            # label.bind("<Button-1>", lambda event, img=pil_img: self.on_image_click(index, event))



        # label.bind("<Button-1>", lambda event, img=pil_img: self.get_selected_images)


    def get_selected_images(self):
        selected_indices = [index for index, var in enumerate(self.check_vars) if var.get()]
        print("Selected image indices:", selected_indices)


    def load_correct(self):
        self.w = int(self.entry_w.get())
        self.h = int(self.entry_h.get())
        self.img_processor = image_process.ImageProcessor(self.w, self.h)
        # entry_w and entry_h as DISABLED
        self.entry_w.config(state=tk.DISABLED)
        self.entry_h.config(state=tk.DISABLED)
        images = self.img_processor.load_images("src/")

        corrected_images = camera_calibration.correct_distortion(images, self.mtx, self.dist, self.newcameramtx)
        self.corrected_images = corrected_images
        
        # img_processor.display_images(corrected_images)
        # messagebox.showinfo("Info", "load and correcct successful!")
        self.show_toast("load and correcct successful!")

        desired_size = (100, 100)

        # # Create a frame to hold all images
        # self.first_frame = tk.Frame(self.root)
        # self.first_frame.grid(row=0, column=2, padx=1, pady=20)  # Place the frame in the first row and third column

        # Display all corrected_images
        for index, img in enumerate(corrected_images):
            pil_img = Image.fromarray(img)  # Convert numpy array to PIL Image
            pil_img_resized = pil_img.resize(desired_size, Image.LANCZOS)  # Resize the image
            tk_img = ImageTk.PhotoImage(pil_img_resized)

            # position index label
            label_index = tk.Label(self.sec_frame, text=f"{index}")
            label_index.grid(row=0, column=index, padx=1, pady=10)
            # label = tk.Label(root, image=tk_img)
            # position for images
            label = tk.Label(self.sec_frame, image=tk_img, padx=5, pady=2)

            label.image = tk_img
            label.grid(row=1, column=index)
            
            # Create a BooleanVar for this Checkbutton
            var = tk.BooleanVar()
            self.check_vars.append(var)

            # position for checkboxs
            check = tk.Checkbutton(self.sec_frame, variable=var, command=lambda v=self.check_vars, idx=index, img=img: self.select_image(v))
            check.grid(row=2, column=index)  # Place it below the image
            self.checkbuttons.append(check)

            # Add mouse click event to each image
            # label.bind("<Button-1>", lambda event, idx=index,  v=self.check_vars, img=img: self.select_image(v))


    # Image Process
    def process(self):
        scale = 4

        if not self.selected_images:
            self.show_toast(f"No Selected Image")
        else:
            images, contours, areas, appro_con_list = self.img_processor.contour_for_robot(self.selected_images, scale)

            # img = corrected_images[0]
            contour = contours[0]
            img = images[0]
            self.appro_con = appro_con_list[0]/1000/scale

            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            print(len(images))
            # print(type(img))
            # print(contour)
            print(self.w, self.h)

            cv2.drawContours(mask, contours, -1, 255, 3)

            # config the isze of pil_img
            desired_size = (300, 200)
            pil_img = Image.fromarray(mask)
            pil_img_resized = pil_img.resize(desired_size, Image.LANCZOS)

            # show pil_img with new size 
            self.photo = ImageTk.PhotoImage(image=pil_img_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
            # plt.close('all')
            # messagebox.showinfo("Info", "完成!")
            self.show_toast("Contour")

    
    # back to start position
    def init_robot(self):
        self.show_toast("Start Position")
        robot_controller = controller.RobotController(0,0,0.08)
        robot_controller.initialize(2) # payload 2
        robot_controller.start_pos() # Default position

    # controll robot to move
    def move(self):
        l = len(self.appro_con)
        path = robot_controller.transformation(self.appro_con)
        robot_controller.move_to(path)
        self.show_toast("Moving", l*1000)
        self.show_toast("finished")

    
    # toast info
    def show_toast(self, message, duration=3000):
        # 如果之前的toast消息仍在显示，先销毁它
        if self.toast_frame:
            self.toast_frame.destroy()

        # 创建一个新的frame来显示toast消息
        self.toast_frame = tk.Frame(self.root, bg="#444444", padx=10, pady=5)
        toast_label = tk.Label(self.toast_frame, text=message, bg="#444444", fg="white")
        toast_label.pack()

        # 使用place方法定位toast消息
        self.toast_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # 使用after方法在指定的持续时间后销毁toast消息
        self.root.after(duration, self.toast_frame.destroy)

    # def on_button_click(self):
    #     # 这里只是一个示例，你可以根据需要更改消息内容
    #     self.show_toast("load and correct successful!")

    # def run(self):
    #     btn = tk.Button(self.root, text="Show Toast", command=self.on_button_click)
    #     btn.pack(pady=20)
    #     self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


# img_processor = image_process.ImageProcessor(240, 170)

# mtx, dist, newcameramtx = camera_calibration.calibrator(27)


# images = img_processor.load_images("src")
# corrected_images = camera_calibration.correct_distortion(images, mtx, dist, newcameramtx)
# img_processor.display_images(corrected_images)
# messagebox.showinfo("Info", "照片导入并修正完成!")
# # images = img_processor.load_images("src/")
# # corrected_images = camera_calibration.correct_distortion(images, mtx, dist, newcameramtx)

# scale = 4
# contours, areas, appro_con_list = img_processor.contour_for_robot(corrected_images, scale)
# img_processor.display_contour(corrected_images[1], contours[1], areas[1])

# # plt.close('all')
# messagebox.showinfo("Info", "完成!")