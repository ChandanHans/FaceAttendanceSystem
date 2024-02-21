import os
import pickle
import shutil
import threading
import cv2
import tkinter as tk
from PIL import Image
from tkinter import ttk
import face_recognition
from customtkinter import *
from database import Database
from utility import *

class AddStudentFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.entry1 = StringVar()
        self.entry2 = StringVar()
        self.configure(border_width=4, border_color="#5665EF")
        self.create_widgets()

    def create_widgets(self):
        self.ask_data_frame = CTkFrame(
            self, border_width=4, border_color="#5665EF", corner_radius=0
        )
        self.ask_data_frame.place(relx=0, rely=0, relwidth=0.4, relheight=0.5)

        self.name_label = CTkLabel(self.ask_data_frame, text="Name:")
        self.name_label.place(relx=0.1, rely=0.1)
        self.name_entry = CTkEntry(self.ask_data_frame, textvariable=self.entry1)
        self.name_entry.place(relx=0.4, rely=0.1, relwidth=0.5)

        self.roll_label = CTkLabel(self.ask_data_frame, text="Roll Number:")
        self.roll_label.place(relx=0.1, rely=0.25)
        self.roll_entry = CTkEntry(self.ask_data_frame, textvariable=self.entry2)
        self.roll_entry.place(relx=0.4, rely=0.25, relwidth=0.5)

        self.course_label = CTkLabel(self.ask_data_frame, text="Course:")
        self.course_label.place(relx=0.1, rely=0.4)
        self.course_entry = CTkComboBox(
            self.ask_data_frame,
            command=self.on_entry_update,
            values=["BSC", "BCA", "BBA"],
            state="readonly",
        )
        self.course_entry.place(relx=0.4, rely=0.4, relwidth=0.5)

        self.sem_label = CTkLabel(self.ask_data_frame, text="Semester:")
        self.sem_label.place(relx=0.1, rely=0.55)
        self.sem_entry = CTkComboBox(
            self.ask_data_frame,
            command=self.on_entry_update,
            values=["1st", "2nd", "3rd", "4th", "5th", "6th"],
            state="readonly",
        )
        self.sem_entry.place(relx=0.4, rely=0.55, relwidth=0.5)

        self.submit_button = CTkButton(
            self.ask_data_frame, text="Add Student", command=self.start_camera
        )
        self.submit_button.place(relx=0.5, rely=0.87, anchor="center")

        #  camera_frame
        self.show_camera_frame = ShowCameraFrame(self)
        self.show_camera_frame.place(relx=0, rely=0.5, relwidth=0.4, relheight=0.5)

        self.student_table_frame = StudentTableFrame(self, self.db)
        self.student_table_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        self.ok_logo = CTkImage(Image.open(resource_path("src/ok.png")), size=(30, 30))
        self.cancel_logo = CTkImage(Image.open(resource_path("src/cancel.png")), size=(30, 30))
        self.status_label = CTkLabel(
            self.ask_data_frame, text="", fg_color="transparent"
        )
        self.entry1.trace_add("write", self.on_entry_update)
        self.entry2.trace_add("write", self.on_entry_update)

    def on_entry_update(self, *args):
        self.status_label.place_forget()

    def start_camera(self):
        self.status_label.place_forget()
        roll = self.roll_entry.get().strip()
        name = self.name_entry.get().strip()
        cource = self.course_entry.get()
        sem = self.sem_entry.get()
        if roll == "" or name == "" or cource == "" or sem == "":
            self.status_label.configure(image=self.cancel_logo)
        else:
            self.submit_button.configure(state=DISABLED)
            self.show_camera_frame.start_camera()
        

    def add_student(self):
        roll = (self.roll_entry.get().strip()).upper()
        name = self.name_entry.get().strip()
        cource = self.course_entry.get()
        sem = self.sem_entry.get()
        success = self.db.execute_query(
            """INSERT INTO Students (Roll, SName, Course, Sem)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                SName = VALUES(SName), Course = VALUES(Course), Sem = VALUES(Sem);""",
            (roll, name, cource, sem),
        )

        if success:
            self.status_label.configure(image=self.ok_logo)
        else:
            self.status_label.configure(image=self.cancel_logo)

    def save_images(self, roll: str):
        # Corrected indentation
        student_folder_path = "Student_Face/" + str(roll.upper())
        if not os.path.exists(student_folder_path):
            os.makedirs(student_folder_path)


class ShowCameraFrame(CTkFrame):
    def __init__(self, parent: AddStudentFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.cap = None
        self.running = False
        self.frame_count = 0
        self.start = False
        self.configure(border_width=4, border_color="#5665EF", corner_radius=0)
        
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
    
    
    def start_camera(self):
        self.create_widgets()
        self.student_folder_path = "Student_Face/" + str(
            self.parent.roll_entry.get().strip().upper()
        )
        if not os.path.exists(self.student_folder_path):
            os.makedirs(self.student_folder_path)

        self.cap = cv2.VideoCapture(self.get_camera_choice())
        self.running = True
        self.camera_process_thread = threading.Thread(target=self.camera_thread)
        self.camera_process_thread.start()


    def camera_thread(self):
        self.frame_count = 0
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            processed_frame = self.process_frame(frame)
            self.after(10, lambda: self.update_frame(processed_frame))
            if self.frame_count >= 100:
                self.parent.add_student()
                break
        if self.cap is not None:
            self.cap.release()
        if self.frame_count < 100:
            shutil.rmtree(self.student_folder_path)
            self.parent.status_label.configure(image=self.parent.cancel_logo)
        self.start = False
        self.delete_widgets()
        self.parent.student_table_frame.show_data()
        self.parent.status_label.place(relx=0.5, rely=0.75, anchor="center")

    def process_frame(self, frame: cv2.typing.MatLike):
        face_locations = face_recognition.face_locations(frame)
        for face_location in face_locations:
            if len(face_locations) == 1:
                top, right, bottom, left = face_locations[0]
                # Save the face
                margin = 50  # You can adjust this value
                top1 = max(top - margin, 0)
                right1 = min(right + margin, frame.shape[1])
                bottom1 = min(bottom + margin, frame.shape[0])
                left1 = max(left - margin, 0)
                face = frame[top1:bottom1, left1:right1]
                if self.start:
                    self.frame_count += 1
                    file_name_path = (
                        f"{self.student_folder_path}/{str(self.frame_count)}.jpg"
                    )
                    cv2.imwrite(file_name_path, face)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    str(self.frame_count),
                    (100, 200),
                    cv2.FONT_HERSHEY_COMPLEX,
                    2,
                    (0, 255, 0),
                    2,
                )
            elif len(face_locations) > 1:
                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
        return frame

    def update_frame(self, frame):
        try:
            image_height = self.winfo_height()
            image_width = self.winfo_width()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = CTkImage(
                img, size=(image_width, image_height)
            )
            self.image_label.configure(image=imgtk)
        except:
            pass

    def save_face(self):
        self.start = True
        
    def delete_widgets(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.image_label.pack_forget()
        self.button_frame.pack_forget()
        self.parent.submit_button.configure(state="normal")
        
    def stop_camera(self):
        self.running = False

    def get_camera_choice(self):
        return int(get_config()["CHOICE"][0])


class StudentTableFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.trash_logo = CTkImage(Image.open(resource_path("src/delete.png")), size=(30, 30))
        self.configure(border_width=4, border_color="#5665EF", corner_radius=0)
        self.create_widgets()
        self.show_data()

    def create_widgets(self):
        # Frame for filter options
        self.filter_frame = CTkFrame(self, fg_color="#B188A8", corner_radius=3)
        self.filter_frame.pack(side="top", fill="x", padx=6, pady=(6, 1))

        self.create_table()

        # Course filter widgets
        self.course_frame = CTkFrame(self.filter_frame, bg_color="#B188A8")
        self.course_frame.pack(side="left", padx=10, pady=10)

        self.filter_course_label = CTkLabel(
            self.course_frame, text="Course:  ", bg_color="#B188A8", text_color="black"
        )
        self.filter_course_label.pack(side="left")

        self.filter_course_entry = CTkComboBox(
            self.course_frame,
            command=self.show_data,
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
            command=self.show_data,
            values=["ALL", "1st", "2nd", "3rd", "4th", "5th", "6th"],
            bg_color="#B188A8",
            state="readonly",
        )
        self.filter_sem_entry.set("ALL")
        self.filter_sem_entry.pack(side="left")

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
        tree_scroll = tk.Scrollbar(self, width=15)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(1, 8))

        # Create the Treeview
        self.tree = ttk.Treeview(
            self, yscrollcommand=tree_scroll.set, selectmode="extended"
        )
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(1, 8))

        self.trash_button = CTkButton(
            self.tree,
            command=self.remove_data,
            image=self.trash_logo,
            text="",
            width=30,
            height=30,
            bg_color="#363636",
            fg_color="#1B1B1B",
            hover_color="#4C4C4C",
        )
        self.trash_button.place(rely=0.98, relx=0.98, anchor="se")

        # Configure the Scrollbar
        tree_scroll.config(command=self.tree.yview)

        # Define columns
        self.tree["columns"] = ("Roll", "Name", "Course", "Sem")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Roll", anchor=tk.W, width=120)
        self.tree.column("Name", anchor=tk.W, width=120)
        self.tree.column("Course", anchor=tk.W, width=120)
        self.tree.column("Sem", anchor=tk.W, width=120)
        # Define headings
        self.tree.heading("Roll", text="Roll", anchor=tk.W)
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Course", text="Course", anchor=tk.W)
        self.tree.heading("Sem", text="Sem", anchor=tk.W)

    def remove_data(self):
        for selected_item in self.tree.selection():
            roll = str(self.tree.item(selected_item)["values"][0]).upper()
            self.db.execute_query("DELETE FROM Students WHERE roll = %s;", (roll,))
            try:
                shutil.rmtree(f"{os.getcwd()}/Student_Face/{roll}")
            except Exception:
                pass
            try:
                with open("known_faces.pkl", "rb") as file:
                    previous_data: dict = pickle.load(file)
                previous_data.pop(roll)
                with open("known_faces.pkl", "wb") as file:
                    pickle.dump(previous_data, file)
            except Exception:
                pass
        self.after(10, lambda: self.show_data())

    def get_filter_data(self):
        course = self.filter_course_entry.get()
        sem = self.filter_sem_entry.get()
        base_query = "SELECT * FROM Students"

        params = ()
        if course == "ALL" and sem == "ALL":
            query = base_query
        else:
            conditions = []
            params = []
            if course != "ALL":
                conditions.append("course = %s")
                params.append(course)
            if sem != "ALL":
                conditions.append("sem = %s")
                params.append(sem)

            query = base_query + " WHERE AND ".join(conditions)
        query += " ORDER BY roll"
        return self.db.fetch_data(query, params)

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def show_data(self, *args):
        data = self.get_filter_data()
        self.clear_tree()
        for row in data:
            self.tree.insert("", "end", values=row)