from customtkinter import *
from PIL import Image

from add_student_frame import AddStudentFrame
from attendance_frame import AttendanceFrame
from database import Database
from home_frame import HomeFrame
from train_data_frame import TrainDataFrame


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


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
