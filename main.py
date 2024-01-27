import json
from customtkinter import *
from PIL import Image
import mysql.connector


class Database:
    def __init__(self, host, user, passwd, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.connect()

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host, user=self.user, passwd=self.passwd, database=self.database
        )
        self.cursor = self.conn.cursor()

    def fetch_data(self, query, params=()):
        """Fetch data from the database using a SELECT query."""
        if self.conn is None:
            self.connect()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_query(self, query, params=()):
        """Execute a given SQL query (INSERT, UPDATE, DELETE) and return True if successful."""
        if self.conn is None:
            self.connect()
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True  # Indicates that the query and commit were successful
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()  # Roll back the transaction on error
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

class MyApp(CTk):
    def __init__(self):
        super().__init__()
        self.db = Database(
            host="localhost", user="root", passwd="8258", database="face recognizer"
        )
        self.title("FaceAttendanceSystem")
        self.geometry("900x600")
        self.minsize(900, 600)
        self.create_widgets()
        self.show_frame(self.home_frame)

    def create_widgets(self):
        self.logo1_image = CTkImage(Image.open("src/checked-user.png"), size=(50, 50))
        self.back_button_image = CTkImage(Image.open("src/back.png"), size=(50, 50))
        self.title_label = CTkLabel(
            master=self,
            text="FaceAttendanceSystem",
            text_color="black",
            image=self.logo1_image,
            font=("Arial", 30, "bold"),
            compound="left",
            height=80,
            bg_color="#B188A8",
        )
        self.title_label.pack(side="top", fill="x")

        self.back_button = CTkButton(
            self.title_label,
            image=self.back_button_image,
            text="",
            width=10,
            height=10,
            command=lambda: self.show_frame(self.home_frame),
            fg_color="#B188A8",
            bg_color="#B188A8",
            hover_color="#886981",
        )
        self.back_button.place(x=10, y=10)

        # Initialize frames
        self.home_frame = HomeFrame(self)
        self.add_student_frame = AddStudentFrame(self, self.db)
        self.train_data_frame = TrainDataFrame(self)
        self.attendance_frame = AttendanceFrame(self)

    def show_frame(self, frame_to_show: CTkFrame):
        for widget in self.winfo_children():
            if widget != self.title_label:
                widget.pack_forget()
        frame_to_show.pack(fill="both", expand=True)
        
class HomeFrame(CTkFrame):
    def __init__(self, parent: MyApp, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # Load images
        self.logo2_image = CTkImage(
            Image.open("src/student-registration.png"), size=(40, 40)
        )
        self.logo3_image = CTkImage(Image.open("src/binary.png"), size=(40, 40))
        self.logo4_image = CTkImage(Image.open("src/face-id.png"), size=(40, 40))

        self.button_add_student = CTkButton(
            self,
            command=lambda: self.parent.show_frame(self.parent.add_student_frame),
            text="  Add Student      ",
            image=self.logo2_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_add_student.place(relx=0.5, rely=0.2, relwidth=0.3, anchor="center")

        self.button_save_data = CTkButton(
            self,
            command=lambda: self.parent.show_frame(self.parent.train_data_frame),
            text="  Save Face Data",
            image=self.logo3_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_save_data.place(relx=0.5, rely=0.35, relwidth=0.3, anchor="center")

        self.button_attendance = CTkButton(
            self,
            command=lambda: self.parent.show_frame(self.parent.attendance_frame),
            text="  Attendance        ",
            image=self.logo4_image,
            corner_radius=5,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
        )
        self.button_attendance.place(relx=0.5, rely=0.5, relwidth=0.3, anchor="center")

        # Checkboxes for options
        self.checkbox_show_camera = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Show camera   ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_show_camera.place(relx=0.5, rely=0.65, anchor="center")

        self.checkbox_auto_start = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Auto Start         ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_auto_start.place(relx=0.5, rely=0.75, anchor="center")

        # Load previous choices if any
        self.load_previous_choices()

    # Utility Functions
    def save_choice(self):
        choice = [self.checkbox_show_camera.get(), self.checkbox_auto_start.get()]
        with open("choice.json", "w") as f:
            json.dump(choice, f)

    def get_choice(self):
        try:
            with open("choice.json", "r") as f:
                choice = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            choice = [
                0,
                0,
            ]  # Default values if the file doesn't exist or contains errors
        return choice

    def load_previous_choices(self):
        choices = self.get_choice()
        if choices[0]:
            self.checkbox_show_camera.select()
        if choices[1]:
            self.checkbox_auto_start.select()

class AddStudentFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.configure(border_width=4, border_color="#5665EF")
        self.create_widgets()

    def create_widgets(self):
        self.ask_data_frame = CTkFrame(self, border_width=4, border_color="#5665EF",corner_radius=0)
        self.ask_data_frame.place(relx=0, rely=0, relwidth=0.4, relheight=0.5)

        self.name_label = CTkLabel(self.ask_data_frame, text="Name:")
        self.name_label.place(relx=0.1, rely=0.1)
        self.name_entry = CTkEntry(self.ask_data_frame)
        self.name_entry.place(relx=0.4, rely=0.1, relwidth=0.5)

        self.roll_label = CTkLabel(self.ask_data_frame, text="Roll Number:")
        self.roll_label.place(relx=0.1, rely=0.25)
        self.roll_entry = CTkEntry(self.ask_data_frame)
        self.roll_entry.place(relx=0.4, rely=0.25, relwidth=0.5)

        self.course_label = CTkLabel(self.ask_data_frame, text="Course:")
        self.course_label.place(relx=0.1, rely=0.4)
        self.course_entry = CTkComboBox(
            self.ask_data_frame, values=["BSC", "BCA", "BBA"], state="readonly"
        )
        self.course_entry.place(relx=0.4, rely=0.4, relwidth=0.5)

        self.sem_label = CTkLabel(self.ask_data_frame, text="Semester:")
        self.sem_label.place(relx=0.1, rely=0.55)
        self.sem_entry = CTkComboBox(
            self.ask_data_frame,
            values=["1st", "2nd", "3rd", "4th", "5th", "6th"],
            state="readonly",
        )
        self.sem_entry.place(relx=0.4, rely=0.55, relwidth=0.5)

        self.submit_button = CTkButton(
            self.ask_data_frame, text="Add Student", command=lambda: self.add_student()
        )
        self.submit_button.place(relx=0.5, rely=0.87, anchor="center")

        #  camera_frame
        self.show_camera_frame = CTkFrame(self, border_width=4, border_color="#5665EF",corner_radius=0)
        self.show_camera_frame.place(relx=0, rely=0.5, relwidth=0.4, relheight=0.5)

        self.show_data_frame = ShowDataFrame(self, self.db,corner_radius=0)
        self.show_data_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        self.ok_logo = CTkImage(Image.open("src/ok.png"), size=(30, 30))
        self.cancel_logo = CTkImage(Image.open("src/cancel.png"), size=(30, 30))
        self.status_label = CTkLabel(
            self.ask_data_frame, text="", fg_color="transparent"
        )

    def add_student(self):
        roll = self.roll_entry.get()
        name = self.name_entry.get()
        cource = self.course_entry.get()
        sem = self.sem_entry.get()
        if roll == "" or name == "" or cource == "" or sem == "":
            self.status_label.configure(image=self.cancel_logo)
        else:
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
        self.status_label.place(relx=0.5, rely=0.75, anchor="center")

class ShowDataFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.configure(border_width=4, border_color="#5665EF")
        self.create_widgets()
        self.show_data()

    def create_widgets(self):
        # Frame for filter options
        self.filter_logo = CTkImage(Image.open("src/filter.png"), size=(25, 25))

        self.filter_frame = CTkFrame(self, fg_color="#B188A8", corner_radius=3)
        self.filter_frame.pack(side="top", fill="x", padx=6, pady=(6,1))
        
        
        
        self.table_frame = CTkScrollableFrame(self, corner_radius=3)
        self.table_frame.pack(fill="both",expand=True,padx=6,pady=(1,6))

        # Course filter widgets
        self.course_frame = CTkFrame(self.filter_frame, bg_color="#B188A8")
        self.course_frame.pack(side="left", padx=10, pady=10)

        self.filter_course_label = CTkLabel(
            self.course_frame, text="Course:  ", bg_color="#B188A8", text_color="black"
        )
        self.filter_course_label.pack(side="left")

        self.filter_course_entry = CTkComboBox(
            self.course_frame,
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
            values=["ALL", "1st", "2nd", "3rd", "4th", "5th", "6th"],
            bg_color="#B188A8",
            state="readonly",
        )
        self.filter_sem_entry.set("ALL")
        self.filter_sem_entry.pack(side="left")

        self.filter_button = CTkButton(
            self.filter_frame,
            text="",
            image=self.filter_logo,
            command=self.show_data,
            width=20,
            height=20,
            fg_color="#B188A8",
            bg_color="#B188A8",
            hover_color="#886981",
        )
        self.filter_button.pack(side="left", padx=5, pady=5)

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

            query = base_query + " WHERE " + " AND ".join(conditions)
        return self.db.fetch_data(query, params)
    
    
    def show_data(self):
        data = self.get_filter_data()
        for row in data:
            frame = CTkFrame(self.table_frame,height=20,fg_color="#363636")
            frame.pack(fill='x', padx=10, pady=1)

            for col_idx, item in enumerate(row):
                label = CTkLabel(master=frame, text=item,height=15,corner_radius=5, anchor='w')
                label.place(relx = self.xr[col_idx], rely = 0.49,anchor="center",relwidth = self.wr[col_idx])
                
class TrainDataFrame(CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Initialize your train data frame widgets here

class AttendanceFrame(CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Initialize your attendance frame widgets here

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
