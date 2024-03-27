
import os
from queue import Queue
import shutil
import cv2
import tkinter as tk
from threading import Thread
from PIL import Image
from tkinter import ttk, messagebox
from customtkinter import *
from database import Database
from toggle_button import ToggleButton
from utility import *
import dlib

class AddDataFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.configure(border_width=4, border_color="#5665EF")

        self.ask_data_frame = AskDataFrame(self)
        self.ask_data_frame.place(relx=0, rely=0, relwidth=0.4, relheight=0.5)
        #  camera_frame
        self.show_camera_frame = ShowCameraFrame(self)
        self.show_camera_frame.place(relx=0, rely=0.5, relwidth=0.4, relheight=0.5)

        self.table_frame = TableFrame(self, self.db)
        self.table_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

    def show_student_table(self):
        self.table_frame.show_student_data()

    def show_teacher_table(self):
        self.table_frame.show_teacher_data()

    def start_camera(self):
        data = self.get_input_data()
        self.ask_data_frame.forget_status()
        if not (
            all([data["id"], data["name"], data["course"], data["sem"]])
            or all([data["id"], data["name"], data["dep"]])
        ):
            self.ask_data_frame.set_cancel_logo()
        else:
            self.ask_data_frame.submit_button.configure(state=DISABLED)
            self.show_camera_frame.start_camera(data)
            
    def show_student_data(self):
        self.table_frame.show_student_data()

    def show_teacher_data(self):
        self.table_frame.show_teacher_data()
    
    def add_profile(self):
        data = self.get_input_data()
        if data["student"]:
            success = self.db.execute_query(
                """INSERT INTO student (ID, Name, Course, Sem)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Name = VALUES(Name), Course = VALUES(Course), Sem = VALUES(Sem);""",
                (data["id"], data["name"], data["course"], data["sem"]),
            )
            self.show_student_data()
        else:
            success = self.db.execute_query(
                """INSERT INTO teacher (ID, Name, Dep)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Name = VALUES(Name), Dep = VALUES(Dep);""",
                (data["id"], data["name"], data["dep"]),
            )
            self.show_teacher_data()
        if success:
            self.ask_data_frame.set_success_logo()
        else:
            self.ask_data_frame.set_cancel_logo()

    def get_input_data(self):
        return self.ask_data_frame.get_data()


class AskDataFrame(CTkFrame):
    def __init__(self, parent: AddDataFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(self, border_width=4, border_color="#5665EF", corner_radius=0)
        self.parent = parent
        self.entry1 = StringVar()
        self.entry2 = StringVar()

        self.status_label = CTkLabel(self, text="", fg_color="transparent")
        
        self.toggle_button = ToggleButton(
            self,
            texts=("Teacher", "Student"),
            callbacks=(self.ask_student, self.ask_teacher), font=("Arial", 15, "bold")
        )
        self.toggle_button.place(relx=0.3, rely=0.87, anchor=CENTER)

        self.name_label = CTkLabel(self, text="Name")
        self.name_entry = CTkEntry(self, textvariable=self.entry1)

        self.id_label = CTkLabel(self, text="ID")
        self.id_entry = CTkEntry(self, textvariable=self.entry2)

        self.course_label = CTkLabel(self, text="Course")
        self.course_entry = CTkComboBox(
            self,
            values=["BSC", "BCA", "BBA"],
            state="readonly",
        )

        self.sem_label = CTkLabel(self, text="Semester")
        self.sem_entry = CTkComboBox(
            self,
            values=["1", "2", "3", "4", "5", "6"],
            state="readonly",
        )

        self.dep_label = CTkLabel(self, text="Dep")
        self.dep_entry = CTkComboBox(
            self,
            values=["IT", "Management"],
            state="readonly",
        )

        self.submit_button = CTkButton(
            self, text="Add Profile", command=self.parent.start_camera, font=("Arial", 15, "bold")
        )
        self.submit_button.place(relx=0.7, rely=0.87, anchor="center")

        self.ok_logo = CTkImage(Image.open(resource_path("src/ok.png")), size=(30, 30))
        self.cancel_logo = CTkImage(
            Image.open(resource_path("src/cancel.png")), size=(30, 30)
        )
        self.ask_student()

    def ask_student(self):
        self.toggle_button.configure(state=DISABLED)
        self.dep_label.place_forget()
        self.dep_entry.place_forget()
        self.dep_entry.set("")
        self.name_label.place(relx=0.1, rely=0.18)
        self.name_entry.place(relx=0.4, rely=0.18, relwidth=0.5)
        self.id_label.place(relx=0.1, rely=0.3)
        self.id_entry.place(relx=0.4, rely=0.3, relwidth=0.5)
        self.course_label.place(relx=0.1, rely=0.42)
        self.course_entry.place(relx=0.4, rely=0.42, relwidth=0.5)
        self.sem_label.place(relx=0.1, rely=0.54)
        self.sem_entry.place(relx=0.4, rely=0.54, relwidth=0.5)
        self.on_click()

    def ask_teacher(self):
        self.toggle_button.configure(state=DISABLED)
        self.sem_label.place_forget()
        self.sem_entry.place_forget()
        self.sem_entry.set("")
        self.course_label.place_forget()
        self.course_entry.place_forget()
        self.course_entry.set("")
        self.name_label.place(relx=0.1, rely=0.18)
        self.name_entry.place(relx=0.4, rely=0.18, relwidth=0.5)
        self.id_label.place(relx=0.1, rely=0.3)
        self.id_entry.place(relx=0.4, rely=0.3, relwidth=0.5)
        self.dep_label.place(relx=0.1, rely=0.42)
        self.dep_entry.place(relx=0.4, rely=0.42, relwidth=0.5)
        self.on_click()


    def on_click(self, *args):
        def temp():
            try:
                if not self.toggle_button.state:
                    self.parent.show_student_table()
                else:
                    self.parent.show_teacher_table()
                self.forget_status()
            except:
                pass
            self.toggle_button.configure(state=NORMAL)
        self.after(50,temp) 
            

    def get_data(self):
        data = {
            "student": not self.toggle_button.state,
            "id": (self.id_entry.get().strip()).upper(),
            "name": " ".join(
                word.capitalize() for word in self.name_entry.get().strip().split()
            ),
            "course": self.course_entry.get(),
            "sem": self.sem_entry.get(),
            "dep": self.dep_entry.get(),
        }
        return data

    def forget_status(self):
        self.status_label.place_forget()

    def set_cancel_logo(self):
        self.status_label.configure(image=self.cancel_logo)
        self.status_label.place(relx=0.5, rely=0.75, anchor="center")

    def set_success_logo(self):
        self.status_label.configure(image=self.ok_logo)
        self.status_label.place(relx=0.5, rely=0.75, anchor="center")


class ShowCameraFrame(CTkFrame):
    def __init__(self, parent: AddDataFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.cap = None
        self.running = False
        self.frame_count = 0
        self.start = False
        self.configure(border_width=4, border_color="#5665EF", corner_radius=0)
        self.safe_to_close = True
        
    def create_widgets(self):
        self.button_frame = CTkLabel(self, text="", height=30)
        self.button_frame.pack(fill="x", padx=6, pady=6, side="bottom")
        # Start Button
        self.start_button = CTkButton(
            self.button_frame, text="Start", command=self.save_face, width=60
        )
        self.start_button.place(rely=0.5, relx=0.3, anchor=CENTER)
        # Cancel Button
        self.cancel_button = CTkButton(
            self.button_frame, text="Cancel", command=self.stop_camera, width=60
        )
        self.cancel_button.place(rely=0.5, relx=0.7, anchor=CENTER)

        self.image_label = CTkLabel(self, text="")
        self.image_label.pack(padx=6, pady=(6, 0), fill="both")

    def start_camera(self, data):
        self.create_widgets()
        if data["student"]:
            self.profile_folder_path = "./Student_Face/" + data["id"]
        else:
            self.profile_folder_path = "./Teacher_Face/" + data["id"]

        if not os.path.exists(self.profile_folder_path):
            os.makedirs(self.profile_folder_path)
            
        self.queue = Queue(maxsize=1)
        self.running = True
        self.camera_process_thread = Thread(target=self.camera_thread,daemon=True)
        self.camera_process_thread.start()
        self.update_frame()

    def camera_thread(self):
        self.safe_to_close = False
        self.frame_count = 0
        self.cap = cv2.VideoCapture(self.get_camera_choice())
        detector = dlib.get_frontal_face_detector()
        frame_set = False
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            if self.queue.empty():
                if not frame_set:
                    frame_height = int(frame.shape[0]/3)
                    frame_width = int(frame.shape[1]/3)
                    scale_width = frame.shape[1] / frame_width
                    scale_height = frame.shape[0] / frame_height
                frame2 = cv2.resize(frame, (frame_width,frame_height))
                face_locations = detector(frame2)
                if face_locations and len(face_locations) == 1:
                    face_location = face_locations[0]
                    top, right, bottom, left = face_location.top(),face_location.right(),face_location.bottom(),face_location.left()

                    # Scale the face location coordinates
                    top_scaled = int(top * scale_height)
                    right_scaled = int(right * scale_width)
                    bottom_scaled = int(bottom * scale_height)
                    left_scaled = int(left * scale_width)

                    # Apply margin and ensure coordinates are within frame bounds for the original frame
                    margin = 50
                    top_final = max(top_scaled - margin, 0)
                    right_final = min(right_scaled + margin, frame.shape[1])
                    bottom_final = min(bottom_scaled + margin, frame.shape[0])
                    left_final = max(left_scaled - margin, 0)
                    face = frame[top_final:bottom_final, left_final:right_final]
                    if self.start:
                        self.frame_count += 1
                        file_name_path = (f"{self.profile_folder_path}/{str(self.frame_count)}.jpg")
                        cv2.imwrite(file_name_path, face)
                    cv2.rectangle(frame2, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(
                        frame2,
                        str(self.frame_count),
                        (100, 200),
                        cv2.FONT_HERSHEY_COMPLEX,
                        2,
                        (0, 255, 0),
                        2,
                    )
                if self.frame_count >= 100:
                    self.parent.add_profile()
                    break     
                self.queue.put(frame2)
                if not frame_set:
                    frame_set = True
        if self.frame_count < 100:
            shutil.rmtree(self.profile_folder_path)
            self.parent.ask_data_frame.set_cancel_logo()

        self.start = False
        self.delete_widgets()

        self.safe_to_close = True
    
    def update_frame(self):
        if not self.queue.empty():
            frame = self.queue.get()
            image_height = self.winfo_height()
            image_width = self.winfo_width()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = CTkImage(img, size=(image_width, image_height))
            self.image_label.configure(image=imgtk)
        
        if self.running:
            self.image_label.after(10, self.update_frame)

    def save_face(self):
        data = self.parent.get_input_data()
        if data["student"]:
            self.parent.db.execute_query(
                f"""UPDATE student SET Encoding = null WHERE ID = '{data["id"]}';"""
            )
        else:
            self.parent.db.execute_query(
                f"""UPDATE teacher SET Encoding = null WHERE ID = '{data["id"]}';"""
            )
        self.start = True

    def delete_widgets(self):
        if self.cap is not None:
            self.cap.release()
        self.image_label.pack_forget()
        self.button_frame.pack_forget()
        self.parent.ask_data_frame.submit_button.configure(state=NORMAL)

    def stop_camera(self):
        self.running = False

    def get_camera_choice(self):
        if get_config()["CHOICE"][0] == "3":
            return get_config()["CHOICE"][2]
        return int(get_config()["CHOICE"][0])

class TableFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.trash_logo = CTkImage(
            Image.open(resource_path("src/delete.png")), size=(30, 30)
        )
        self.up_logo = CTkImage(Image.open(resource_path("src/up.png")), size=(20, 20))
        self.down_logo = CTkImage(
            Image.open(resource_path("src/down.png")), size=(20, 20)
        )
        self.configure(border_width=4, border_color="#5665EF", corner_radius=0)
        self.create_widgets()
        self.show_student_data()

    def create_widgets(self):
        # Frame for filter options
        self.filter_frame = CTkFrame(self, fg_color="#B188A8", corner_radius=3)
        self.filter_frame.pack(side="top", fill="x", padx=6, pady=(6, 1))

        self.adjust_sem_frame = CTkFrame(self.filter_frame, fg_color="#B188A8")
        self.adjust_sem_frame.pack(side="right", padx=10, pady=10)

        self.decrement_button = CTkButton(
            self.adjust_sem_frame,
            command=self.sem_decrement,
            image=self.down_logo,
            text="",
            width=10,
            height=10,
            fg_color="#886981",
            hover_color="#4C4C4C",
        )
        self.decrement_button.pack(side="left", padx=5, pady=5)
        self.increment_button = CTkButton(
            self.adjust_sem_frame,
            command=self.sem_increment,
            image=self.up_logo,
            text="",
            width=10,
            height=10,
            fg_color="#886981",
            hover_color="#4C4C4C",
        )
        self.increment_button.pack(side="left", padx=5, pady=5)

        # Course filter widgets
        self.course_frame = CTkFrame(self.filter_frame, bg_color="#B188A8")
        self.course_frame.pack(side="left", padx=10, pady=10)

        self.filter_course_label = CTkLabel(
            self.course_frame, text="Course:  ", bg_color="#B188A8", text_color="black"
        )
        self.filter_course_label.pack(side="left")

        self.filter_course_entry = CTkComboBox(
            self.course_frame,
            command=self.show_student_data,
            values=["ALL", "BSC", "BCA", "BBA"],
            bg_color="#B188A8",
            state="readonly",
        )
        self.filter_course_entry.set("ALL")
        self.filter_course_entry.pack(side="left")

        # Semester filter widgets
        self.sem_frame = CTkFrame(self.filter_frame, bg_color="#B188A8")
        self.sem_frame.pack(side="left", padx=10, pady=10)

        self.filter_sem_label = CTkLabel(
            self.sem_frame, text="Sem:  ", bg_color="#B188A8", text_color="black"
        )
        self.filter_sem_label.pack(side="left")

        self.filter_sem_entry = CTkComboBox(
            self.sem_frame,
            command=self.show_student_data,
            values=["ALL", "1", "2", "3", "4", "5", "6"],
            bg_color="#B188A8",
            state="readonly",
        )
        self.filter_sem_entry.set("ALL")
        self.filter_sem_entry.pack(side="left")

        self.create_table()

    def create_table(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure Treeview colors
        style.configure(
            "Treeview",
            background="#363636",
            fieldbackground="#363636",
            foreground="white",
            font=("Arial", 10),
        )

        # Change selected color
        style.map("Treeview", background=[("selected", "#4a4a4a")])

        # Scrollbar for the Treeview
        self.tree_scroll = tk.Scrollbar(self, width=15)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(1, 8))

        # Create the Treeview
        self.student_tree = ttk.Treeview(
            self, yscrollcommand=self.tree_scroll.set, selectmode="extended"
        )

        # Define columns
        self.student_tree["columns"] = ("ID", "Name", "Course", "Sem")
        self.student_tree.column("#0", width=0, stretch=tk.NO)
        self.student_tree.column("ID", anchor=tk.W, width=120)
        self.student_tree.column("Name", anchor=tk.W, width=120)
        self.student_tree.column("Course", anchor=tk.W, width=120)
        self.student_tree.column("Sem", anchor=tk.W, width=120)
        # Define headings
        self.student_tree.heading("ID", text="ID", anchor=tk.W)
        self.student_tree.heading("Name", text="Name", anchor=tk.W)
        self.student_tree.heading("Course", text="Course", anchor=tk.W)
        self.student_tree.heading("Sem", text="Sem", anchor=tk.W)

        self.trash_button1 = CTkButton(
            self.student_tree,
            command=self.remove_student,
            image=self.trash_logo,
            text="",
            width=30,
            height=30,
            bg_color="#363636",
            fg_color="#1B1B1B",
            hover_color="#4C4C4C",
        )
        self.trash_button1.place(rely=0.98, relx=0.98, anchor="se")

        # Create the Treeview
        self.teacher_tree = ttk.Treeview(
            self, yscrollcommand=self.tree_scroll.set, selectmode="extended"
        )
        # Define columns
        self.teacher_tree["columns"] = ("ID", "Name", "Department")
        self.teacher_tree.column("#0", width=0, stretch=tk.NO)
        self.teacher_tree.column("ID", anchor=tk.W, width=120)
        self.teacher_tree.column("Name", anchor=tk.W, width=120)
        self.teacher_tree.column("Department", anchor=tk.W, width=120)
        # Define headings
        self.teacher_tree.heading("ID", text="ID", anchor=tk.W)
        self.teacher_tree.heading("Name", text="Name", anchor=tk.W)
        self.teacher_tree.heading("Department", text="Course", anchor=tk.W)

        self.trash_button2 = CTkButton(
            self.teacher_tree,
            command=self.remove_teacher,
            image=self.trash_logo,
            text="",
            width=30,
            height=30,
            bg_color="#363636",
            fg_color="#1B1B1B",
            hover_color="#4C4C4C",
        )
        self.trash_button2.place(rely=0.98, relx=0.98, anchor="se")

    def sem_increment(self):
        response = messagebox.askyesno("Confirm", "It will move every student to the next sem !!")
        if response:
            self.db.execute_query("UPDATE student SET sem = sem + 1")
            self.show_student_data()
            
    def sem_decrement(self):
        response = messagebox.askyesno("Confirm", "It will move every student to the previous sem !!")
        if response:
            min_sem = self.db.fetch_data("SELECT MIN(sem) FROM student")[0][0]
            if min_sem != 1:
                self.db.execute_query("UPDATE student SET sem = sem - 1")
                self.show_student_data()

    
    def remove_student(self):
        def temp():
            response = messagebox.askyesno("Confirm", "Are you sure you want to do this?")
            if response:
                for selected_item in self.student_tree.selection():
                    id = self.student_tree.item(selected_item)["values"][0]
                    self.db.execute_query("DELETE FROM student WHERE ID = %s;", (id,))
                    self.db.execute_query("DELETE FROM attendance WHERE ID = %s;", (id,))
                    try:
                        shutil.rmtree(f"{os.getcwd()}/Student_Face/{id}")
                    except Exception:
                        pass
                self.after(10, self.show_student_data)
            else:
                self.after(10, self.show_student_data)
        Thread(target=temp, daemon=True).start()
        
    def remove_teacher(self):
        def temp():
            response = messagebox.askyesno("Confirm", "Are you sure you want to do this?")
            if response:
                for selected_item in self.teacher_tree.selection():
                    id = self.teacher_tree.item(selected_item)["values"][0]
                    self.db.execute_query("DELETE FROM teacher WHERE ID = %s;", (id,))
                    self.db.execute_query("DELETE FROM attendance WHERE ID = %s;", (id,))
                    try:
                        shutil.rmtree(f"{os.getcwd()}/Teacher_Face/{id}")
                    except Exception:
                        pass
                self.after(10, self.show_teacher_data)
            else:
                self.after(10, self.show_teacher_data)
        Thread(target=temp, daemon=True).start()

    def clear_tree(self, tree: ttk.Treeview):
        # Assuming 'treeview' is your ttk.Treeview object
        items = tree.get_children()
        if items:
            tree.delete(*items)


    def show_student_data(self, *args, **kwargs):
        # Extracting keyword arguments with default values
        name = kwargs.get("name", "")
        id = kwargs.get("id", "")
        course = self.filter_course_entry.get()
        sem = self.filter_sem_entry.get()

        # Construct the basic query
        query = f"""
SELECT 
    ID, Name, Course, Sem
FROM 
    student
WHERE 
    1=1
    AND Name LIKE "{name}%"
    AND ID LIKE "{id}%"
    AND Course LIKE "{'' if course == 'ALL' else course}%"
    AND Sem LIKE "{'' if sem == 'ALL' else sem}%"
ORDER BY
    ID
"""
        data = self.db.fetch_data(query)

        self.clear_tree(self.student_tree)
        for row in data:
            self.student_tree.insert("", "end", values=row)

        self.teacher_tree.pack_forget()
        self.tree_scroll.config(command=self.student_tree.yview)
        self.student_tree.pack(
            side="left", fill="both", expand=True, padx=(8, 0), pady=(1, 8)
        )

    def show_teacher_data(self, *args, **kwargs):
        # Extracting keyword arguments with default values
        name = kwargs.get("name", "")
        id = kwargs.get("id", "")

        # Construct the basic query
        query = f"""
SELECT 
    ID, Name, Dep
FROM 
    teacher
WHERE 
    1=1
    AND Name LIKE "{name}%"
    AND ID LIKE "{id}%"
ORDER BY
    ID
"""
        data = self.db.fetch_data(query)

        self.clear_tree(self.teacher_tree)
        for row in data:
            self.teacher_tree.insert("", "end", values=row)

        self.student_tree.pack_forget()
        self.tree_scroll.config(command=self.teacher_tree.yview)
        self.teacher_tree.pack(
            side="left", fill="both", expand=True, padx=(8, 0), pady=(1, 8)
        )
