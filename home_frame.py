import json
from customtkinter import *
from PIL import Image

class HomeFrame(CTkFrame):
    def __init__(self, parent, **kwargs):
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

        # Frame as a container for label and combobox
        self.camera_selection_container = CTkLabel(self, text="", width=260)
        self.camera_selection_container.place(relx=0.5, rely=0.65, anchor="center")

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

        # Checkboxes for options
        self.checkbox_show_camera = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Show Camera   ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_show_camera.place(relx=0.5, rely=0.75, anchor="center")

        self.checkbox_auto_start = CTkCheckBox(
            self,
            command=lambda: self.save_choice(),
            text="   Auto Start         ",
            font=("Arial", 20, "bold"),
        )
        self.checkbox_auto_start.place(relx=0.5, rely=0.85, anchor="center")

        # Load previous choices if any
        self.load_previous_choices()

    # Utility Functions
    def save_choice(self, *args):
        choice = [
            self.camera_selection.get(),
            self.checkbox_show_camera.get(),
            self.checkbox_auto_start.get(),
        ]
        with open("choice.json", "w") as f:
            json.dump(choice, f)

    def get_choice(self):
        try:
            with open("choice.json", "r") as f:
                choice = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            choice = [
                "0",
                0,
                0,
            ]  # Default values if the file doesn't exist or contains errors
            self.save_choice()
        return choice

    def load_previous_choices(self):
        choices = self.get_choice()
        self.camera_selection.set(choices[0])
        if choices[1]:
            self.checkbox_show_camera.select()
        if choices[2]:
            self.checkbox_auto_start.select()