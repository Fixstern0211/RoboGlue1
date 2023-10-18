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
        self.img_processor = None
        self.w = None
        self.h = None
        self.scale = None
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
        self.robot_controller = None

        bg_color = "#DCDCDC" # color of background

        # Create a new frame for w and h inputs
        self.frame1 = tk.Frame(self.root, bg=bg_color)
        self.frame1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.first_frame = tk.Frame(self.frame1, bg=bg_color, padx=30, pady=10)
        self.first_frame.grid(row=0, column=0, pady=10, sticky="W")

        self.label_re = Label(self.first_frame, text="1. Size of Reference:", bg=bg_color)
        self.label_re.grid(row=0, column=0, columnspan=2, pady=10, sticky="NW")

        # Input for w
        self.label_w = Label(self.first_frame, text="Enter width:", bg=bg_color)
        self.label_w.grid(row=1, column=0, pady=10, sticky="W")
        self.entry_w = Entry(self.first_frame)
        self.entry_w.grid(row=1, column=1, pady=10)
        self.entry_w.insert(0, "198")

        # Input for h
        self.label_h = Label(self.first_frame, text="Enter height:", bg=bg_color)
        self.label_h.grid(row=2, column=0, pady=10, sticky="W")
        self.entry_h = Entry(self.first_frame)
        self.entry_h.grid(row=2, column=1, pady=10)
        self.entry_h.insert(0, "148")

        # Frame to hold all images
        self.sec_frame = tk.Frame(self.frame1, bg=bg_color, padx=10, pady=10)
        self.sec_frame.grid(row=0, column=1, pady=10)

        # Frame for Camera Calibration and Images Process
        self.frame2 = tk.Frame(self.root, bg=bg_color)
        self.frame2.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Create a frame to hold the labels and Button for Camera Calibration
        third_frame = tk.Frame(self.frame2, bg=bg_color, padx=10, pady=10)
        third_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        Label(third_frame, text="2. Camera Calibration", bg=bg_color).grid(row=0, column=0, pady=10, columnspan=2, sticky="WN")

        # Button for Camera Calibration
        self.btn_calibrate = tk.Button(third_frame, text="Calibration", command=self.calibrate_camera)
        self.btn_calibrate.grid(row=1, column=0, padx=10, pady=10, sticky="NW")

        self.label_mtx = Label(third_frame, text="Camera Matrix:", bg=bg_color)
        self.label_mtx.grid(row=2, column=0, pady=1, sticky="W")

        # Create the mtx_label and place it inside the frame
        self.mtx_label = Label(third_frame, text="", wraplength=400)
        self.mtx_label.grid(row=3, column=0, padx=5, pady=1, sticky="NW") # Use pack to place it inside the frame

        self.label_dist= Label(third_frame, text="Distortion Coefficients:", bg=bg_color)
        self.label_dist.grid(row=4, column=0, pady=1, sticky="W")

        # Create the dist_label and place it inside the frame
        self.dist_label = Label(third_frame, text="", wraplength=400)
        self.dist_label.grid(row=5, column=0, padx=5, pady=1, sticky="NW") # Use pack to place it below the mtx_label inside the frame

        
        # # Create a frame to hold Button for load and correct
        fourth_frame = tk.Frame(self.frame2, bg="#DCDCDC")
        fourth_frame.grid(row=0, column=1, padx=30, pady=20, sticky="nsew")  # Place the frame in the fourth row and first column

        Label(fourth_frame, text="3. Load & Correct", bg=bg_color).grid(row=0, column=0, pady=10, columnspan=2, sticky="WN")
        # Button for Images Load and Correct
        self.btn_load_correct = tk.Button(fourth_frame, text="Load and Correct", command=lambda: root.after(1000, self.load_correct))
        self.btn_load_correct.grid(row=1, column=0, padx=10, pady=10, sticky="N")

        Label(fourth_frame, text="4. Images Process", bg=bg_color).grid(row=0, column=1, pady=10, columnspan=2, sticky="N")
        # Button for Images processing
        
        self.btn_process = tk.Button(fourth_frame, text="Process", command=lambda: root.after(1000, self.process))
        self.btn_process.grid(row=1, column=1, padx=80, pady=10, sticky="N")

        # add Canvas for 
        self.canvas = tk.Canvas(fourth_frame, bg="white", width=300, height=200)
        self.canvas.grid(row=2, column=1, padx=10, pady=10, sticky="NW")

        # # Create a frame to hold Button for load and correct
        fifth_frame = tk.Frame(self.frame2, bg="#DCDCDC")
        fifth_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")  # Place the frame in the fourth row and first column
        Label(fifth_frame, text="5. Robot Controller", bg=bg_color).grid(row=0, column=0, pady=10, columnspan=2, sticky="NW")
        
        # Input for Start Point
        self.label_sp = Label(fifth_frame, text="Start Point:", bg=bg_color)
        self.label_sp.grid(row=1, column=0, pady=10, sticky="W")
        self.entry_x = Entry(fifth_frame, width=10)
        self.entry_x.grid(row=1, column=1, padx=2, pady=10, sticky="W")
        self.entry_x.insert(0, "0.250")
        # y
        self.entry_y = Entry(fifth_frame, width=10)
        self.entry_y.grid(row=1, column=2, padx=2, pady=10, sticky="W")
        self.entry_y.insert(0, "0.180")
        # z
        self.entry_z = Entry(fifth_frame, width=10)
        self.entry_z.grid(row=1, column=3, padx=2, pady=10, sticky="W")
        self.entry_z.insert(0, "0.300")

        # Button for robot
        self.btn_init_robot = tk.Button(fifth_frame, text="To Start Position", command=lambda: root.after(1000, self.init_robot))
        self.btn_init_robot.grid(row=3, column=0, padx=10, pady=10, sticky="NW")

        # Button for robot
        self.btn_adjust = tk.Button(fifth_frame, text="Adjusting", command=lambda: root.after(1000, self.robot_controller.adjust(self.w, self.h)))
        self.btn_adjust.grid(row=4, column=0, padx=10, pady=10, sticky="NW")

        # Button for movw 
        self.btn_move = tk.Button(fifth_frame, text="Move", command=lambda: root.after(1000, self.move(self.contour)))
        self.btn_move.grid(row=5, column=0, padx=10, pady=10, sticky="NW")



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
        self.mtx_label.config(text=f"{formatted_mtx}")

        self.dist = self.dist[0]
        formatted_dist = "["
        for i in range(len(self.dist)):
            row_str = (f"{self.dist[i]:.3f}")
            formatted_dist += f"{row_str}"
            if i < 4:
                formatted_dist += f"\n"

        formatted_dist += " ]"
        self.dist_label.config(text=f"{formatted_dist}")

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
            self.show_toast(f"Selected Image {selected_indices}", 2000)

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

    def get_selected_images(self):
        selected_indices = [index for index, var in enumerate(self.check_vars) if var.get()]
        print("Selected image indices:", selected_indices)


    def load_correct(self):
        self.corrected_images = []
        self.w = int(self.entry_w.get())
        self.h = int(self.entry_h.get())
        self.img_processor = image_process.ImageProcessor(self.w, self.h)
        # entry_w and entry_h as DISABLED
        self.entry_w.config(state=tk.DISABLED)
        self.entry_h.config(state=tk.DISABLED)
        images = self.img_processor.load_images("src/")

        corrected_images = camera_calibration.correct_distortion(images, self.mtx, self.dist, self.newcameramtx)
        self.corrected_images = corrected_images

        self.show_toast("load and correcct successful!",len(corrected_images))

        desired_size = (100, 100)

        self.check_vars = []
        self.checkbuttons = []
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


    # Image Process
    def process(self):
        self.scale = 4

        if not self.selected_images:
            self.show_toast(f"No Selected Image")
        else:

            # Create a waiting label
            font = ("Arial", 20)  # Here, "Arial" is the font type and 20 is the font size

            # Apply the font to the label
            waiting_label = tk.Label(self.frame1, text="Please wait...", font=font)
            waiting_label.grid(row=0, column=2, padx=20, pady=10, columnspan=2, sticky="E")

            # Update the main window to show the label
            self.root.update()

            images, contours, areas, appro_con_list = self.img_processor.contour_for_robot(self.selected_images, self.scale)

            # Remove the waiting label after processing
            waiting_label.destroy()

            # img = corrected_images[0]
            # contour = contours[0]
            img = images[0]
            
            appro_con_list = appro_con_list[0] # size 2 dimension [[]]
            appro_con_list = np.squeeze(appro_con_list, axis=1) # size 2 dimension [[]]

            print(appro_con_list)
            self.appro_con = [(p[0] + 10)/1000/self.scale for p in appro_con_list] # from mm to m, return real size

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
            # messagebox.showinfo("Info", "finished!")
            self.show_toast("Contour")

    
    # back to start position
    def init_robot(self):
        self.show_toast("Start Position")
        x = float(self.entry_x.get())
        y = float(self.entry_y.get())
        z = float(self.entry_z.get())
        print(x,y,z)
        self.robot_controller = controller.RobotController(0,0,0.08) # TCP Point
        self.robot_controller.initialize(2) # payload 2
        
        self.robot_controller.start_pos(x, y, z) # Starting Point

    # controll robot to move
    def move(self):
        l = len(self.appro_con)
        path = self.robot_controller.transformation(self.appro_con)
        z = int(self.entry_z.get())
        self.robot_controller.move_to(path, z)
        self.show_toast("Moving", l*1000)
        self.show_toast("finished")

    
    # toast info
    def show_toast(self, message, duration=3000):
        # if last toast still exsist，it will be destroyed 
        if self.toast_frame:
            self.toast_frame.destroy()

        # build a new frame to show toast
        self.toast_frame = tk.Frame(self.root, bg="#444444", padx=10, pady=5)
        toast_label = tk.Label(self.toast_frame, text=message, bg="#444444", fg="white")
        toast_label.pack()

        # locate toast
        self.toast_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # after duration, the toast will be destroyed 
        self.root.after(duration, self.toast_frame.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
