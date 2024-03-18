from multiprocessing import Pool as ThreadPool
import pickle
from threading import Thread
import time
from customtkinter import *
from PIL import Image

import face_recognition
from database import Database
from loading_animation import LoadingAnimation

from utility import *

class HomeFrame(CTkFrame):
    def __init__(self, parent, db : Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.parent = parent
        self.init_ui()
        

    def init_ui(self):
        # Load images
        self.logo2_image = CTkImage(
            Image.open(resource_path("src/add-user.png")), size=(40, 40)
        )
        self.logo3_image = CTkImage(Image.open(resource_path("src/list.png")), size=(40, 40))
        self.logo4_image = CTkImage(Image.open(resource_path("src/face-id.png")), size=(40, 40))
        self.logo5_image = CTkImage(Image.open(resource_path("src/binary-file.png")), size=(40, 40))

        self.button_add_student = CTkButton(
            self,
            command=lambda: self.parent.show_frame(self.parent.add_data_frame),
            text="  Create Profile       ",
            image=self.logo2_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_add_student.place(relx=0.5, rely=0.1, relwidth=0.3, anchor="center")

        self.button_train_data = CTkButton(
            self,
            command= lambda : self.start_thread(self.save_new_face_data),
            text="  Create Dataset     ",
            image=self.logo5_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_train_data.place(relx=0.5, rely=0.22, relwidth=0.3, anchor="center")
        
        self.button_attendance = CTkButton(
            self,
            command=lambda : self.parent.take_attendance(),
            text="  Start Attendance  ",
            image=self.logo4_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_attendance.place(relx=0.5, rely=0.34, relwidth=0.3, anchor="center")

        self.button_student_data = CTkButton(
            self,
            command=lambda: self.parent.show_frame(self.parent.student_data_frame),
            text="  View Attendance ",
            image=self.logo3_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_student_data.place(relx=0.5, rely=0.46, relwidth=0.3, anchor="center")
        
        # Frame as a container for label and combobox
        self.camera_selection_container = CTkLabel(self, text="", width=260)
        self.camera_selection_container.place(relx=0.5, rely=0.68, anchor="center")

        # ComboBox for camera selection inside the container
        self.camera_selection = CTkComboBox(
            self.camera_selection_container,
            values=[str(i) for i in range(0, 20)],
            state="readonly",
            width=60,
            command=self.save_choice,
        )
        self.camera_selection.place(y=0, x=0)
        self.camera_selection.set("0")

        # Label for camera selection inside the container
        self.camera_selection_label = CTkLabel(
            self.camera_selection_container,
            text="Select Camera",
            font=("Arial", 20, "bold"),
        )
        self.camera_selection_label.place(x=80, y=0)

        self.checkbox_auto_start = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Auto Start         ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_auto_start.place(relx=0.5, rely=0.78, anchor="center")

        # Load previous choices if any
        self.load_previous_choices()

    # Utility Functions
    def save_choice(self, *args):
        choice = [
            self.camera_selection.get(),
            self.checkbox_auto_start.get(),
        ]
        update_choice(choice)

    def get_choice(self):
        config = get_config()
        return config["CHOICE"]

    def load_previous_choices(self):
        choices = self.get_choice()
        self.camera_selection.set(choices[0])
        if choices[1]:
            self.checkbox_auto_start.select()
    
    def process_for_roll(self,folder):
        student_image_paths = [os.path.join(f"./Student_Face/{folder}", image_file) for image_file in os.listdir(f"./Student_Face/{folder}")]
        # Use ThreadPoolExecutor to execute the function in threads
        with ThreadPool() as pool:
            results = pool.map(self.get_face_encoding, student_image_paths)
        return [item for item in results if item is not None]
    
    def save_new_face_data(self):
        students_face_data = self.get_saved_encodings()
        total = len(students_face_data)
        for widget in self.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=DISABLED)
        try:
            loading_animation = LoadingAnimation(self.parent)
            for index,data in enumerate(students_face_data.items()):
                time.sleep(0.2)
                loading_animation.change_text(f"{index+1}/{total}")
                roll = data[0]
                if data[1] == None:
                    encodings = self.process_for_roll(roll)
                    self.save_encodings(roll,encodings)
                    
        except FileNotFoundError:
            showwarning("Warning", "Please all student face data.")
            
        time.sleep(2)
        loading_animation.stop()
        for widget in self.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=NORMAL)
    
    def save_encodings(self,roll,encodings):
        binary_encoding = pickle.dumps(encodings)
        self.db.execute_query("UPDATE student SET Encoding=%s WHERE ID=%s;", (binary_encoding, roll))
        
    
    def get_saved_encodings(self):
        return dict(self.db.fetch_data("SELECT ID,Encoding from student;"))
    
    @staticmethod
    def get_face_encoding(image_path):
        try:
            student_image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(student_image)
            return face_encodings[0] if face_encodings else None
        except Exception:
            return None
        
    @staticmethod
    def start_thread(function,*args):
        t1 = Thread(target=function,args=args)
        t1.daemon = True
        t1.start()