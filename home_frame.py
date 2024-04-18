from multiprocessing import Event, Pool as ThreadPool, Process
import pickle
from threading import Thread
import time
from customtkinter import *
from PIL import Image

import face_recognition
import attendance 
from database import Database
from loading_animation import LoadingAnimation

from utility import *

class HomeFrame(CTkFrame):
    def __init__(self, parent, db : Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.parent = parent
        self.stop_event = Event()
        self.init_ui()      
        self.after(5000,self.auto_start)
        
    def init_ui(self):
        # Load images
        self.logo2_image = CTkImage(
            Image.open(resource_path("assets/add-user.png")), size=(40, 40)
        )
        self.logo3_image = CTkImage(Image.open(resource_path("assets/list.png")), size=(40, 40))
        self.logo4_image = CTkImage(Image.open(resource_path("assets/face-id.png")), size=(40, 40))
        self.logo5_image = CTkImage(Image.open(resource_path("assets/binary-file.png")), size=(40, 40))

        self.button_add_student = CTkButton(
            self,
            command= self.parent.show_add_data_frame,
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
            command = self.take_attendance,
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
            command=self.parent.show_data_frame,
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
        self.camera_selection_container.place(relx=0.5, rely=0.58, anchor="center")

        # ComboBox for camera selection inside the container
        self.camera_selection = CTkComboBox(
            self.camera_selection_container,
            values=["0","1","2","3"],
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
        
        self.checkbox_audio = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Audio                ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_audio.place(relx=0.5, rely=0.68, anchor="center")
        
        self.checkbox_auto_start = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Auto Start         ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_auto_start.place(relx=0.5, rely=0.78, anchor="center")

        self.credit_label = CTkLabel(
            self,
            text="Developed By: Chandrakanta Hans",
            font=("Arial", 15, "bold")
        )
        self.credit_label.place(relx=0.97, rely=0.97,anchor="se")
        
        # Load previous choices if any
        self.load_previous_choices()

    def auto_start(self):
        if self.checkbox_auto_start.get() == 1:
            self.take_attendance()
    
    def stop_attendance(self):
        self.stop_event.set()
    
    
    def take_attendance(self):
        for widget in self.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=DISABLED)
        self.stop_event.clear()
        process = Process(target=attendance.take_attendance, args=(self.stop_event,))
        process.daemon = True
        process.start()
    
    # Utility Functions
    def save_choice(self, *args):
        choice = [
            int(self.camera_selection.get()),
            self.checkbox_audio.get(),
            self.checkbox_auto_start.get(),
        ]
        update_choice(choice)

    def load_previous_choices(self):
        config = get_config()
        self.camera_selection.set(config["camera_choice"])
        if config["audio_choice"]:
            self.checkbox_audio.select()
        if config["auto_start"]:
            self.checkbox_auto_start.select()
    
    def process_for_folder(self,folder):
        student_image_paths = [os.path.join(folder, image_file) for image_file in os.listdir(folder)]
        with ThreadPool() as pool:
            results = pool.map(self.get_face_encoding, student_image_paths)
        return [item for item in results if item is not None]
    
    def save_new_face_data(self):
        for widget in self.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=DISABLED)
        
        self.loading_animation = LoadingAnimation(self.parent, radius=90)
        students_face_data = self.get_student_encodings()
        total = len(students_face_data)
        max_processes = os.cpu_count()
        for index,profile in enumerate(students_face_data):
            try:
                time.sleep(0.05)
                self.loading_animation.change_text(f"{max_processes}\nstudent\n{index+1}/{total}")
                id = profile[0]
                if profile[2] == None:
                    folder = "./Student_face/" + id
                    encodings = self.process_for_folder(folder)
                    self.save_student_encodings(id,encodings)
                    temp = list(profile)
                    temp[2] = pickle.dumps(encodings)
                    students_face_data[index] = temp
            except FileNotFoundError:
                showwarning("Warning", f"Missing folder for {id}")
        
        staff_face_data = self.get_staff_encodings()
        total = len(staff_face_data)
        for index,profile in enumerate(staff_face_data):
            try:
                time.sleep(0.05)
                self.loading_animation.change_text(f"{max_processes}\nstaff_face\n{index+1}/{total}")
                id = profile[0]
                if profile[2] == None:
                    folder = "./Staff_face/" + id
                    encodings = self.process_for_folder(folder)
                    self.save_staff_encodings(id,encodings)
                    temp = list(profile)
                    temp[2] = pickle.dumps(encodings)
                    staff_face_data[index] = temp
            except FileNotFoundError:
                showwarning("Warning", f"Missing folder for {id}")
                
        self.loading_animation.change_text(f"Saving Data")
        self.save_encodings_locally(students_face_data + staff_face_data)
        time.sleep(2)
        self.loading_animation.stop()
        for widget in self.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=NORMAL)
    
    def save_encodings_locally(self, all_profiles):
        filter_data = []
        for profile in all_profiles:
            if profile[2] is not None:
                id, name, encoding, role = profile[0], profile[1], pickle.loads(profile[2]), profile[3]
                filter_data.append((id, name, encoding, role))
        with open('face_data.pkl', 'wb') as file:
            pickle.dump(filter_data, file)
    
    def save_student_encodings(self,id,encodings):
        binary_encoding = pickle.dumps(encodings)
        self.db.execute_query("UPDATE student_face SET Encoding=%s WHERE ID=%s;", (binary_encoding, id))
    
    def save_staff_encodings(self,id,encodings):
        binary_encoding = pickle.dumps(encodings)
        self.db.execute_query("UPDATE staff_face SET Encoding=%s WHERE ID=%s;", (binary_encoding, id))
        
    
    def get_student_encodings(self) -> list[tuple]:
        data = []
        chunk_size = 10  # Rows per chunk
        offset = 0
        # Assume these methods return the total row count for each table
        total_rows = self.db.fetch_data("SELECT COUNT(*) FROM student_face")[0][0]
        while offset < total_rows:
            self.loading_animation.change_text(f"Fetching\nStudent Data\n{offset}/{total_rows}")
            # Fetch a chunk from the student_face table
            student_profiles = self.db.fetch_data(
                f"""
                SELECT ID, Name, Encoding, 'student' AS Role 
                FROM student_face 
                LIMIT {chunk_size} OFFSET {offset}
                """
            )
            data += student_profiles
            offset += chunk_size      
        return data
    
    def get_staff_encodings(self) -> list[tuple]:
        data = []
        chunk_size = 10  # Rows per chunk
        offset = 0

        # Assume these methods return the total row count for each table
        total_rows = self.db.fetch_data("SELECT COUNT(*) FROM staff_face")[0][0]
        now = 0
        while offset < total_rows:
            now += chunk_size
            if now > total_rows:
                now = total_rows
            self.loading_animation.change_text(f"Fetching\nStaff Data\n{offset}/{total_rows}")
            
            # Fetch a chunk from the staff_face table
            staff_profiles = self.db.fetch_data(
                f"""
                SELECT ID, Name, Encoding, 'staff' AS Role 
                FROM staff_face 
                LIMIT {chunk_size} OFFSET {offset}
                """
            )
            data += staff_profiles
            offset += chunk_size
        return data
    
    @staticmethod
    def get_face_encoding(image_path):
        try:
            student_image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(student_image)
            print(image_path)
            return face_encodings[0] if face_encodings else None
        except Exception:
            return None
        
    @staticmethod
    def start_thread(function,*args):
        t1 = Thread(target=function,args=args)
        t1.daemon = True
        t1.start()