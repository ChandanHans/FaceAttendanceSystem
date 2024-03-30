from customtkinter import *
from PIL import Image

from multiprocessing import freeze_support
from add_data_frame import AddDataFrame
from database import Database
from home_frame import HomeFrame
from data_frame import DataFrame

from utility import *

config = get_config()

class FaceAttendanceSystem(CTk):
    def __init__(self):
        super().__init__()
        self.connect_db()
        self.title("FaceAttendanceSystem")
        self.minsize(900, 600)
        self.create_widgets()
        self.after(100, self.show_home_frame)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def connect_db(self):
        self.db = Database()
    
    def create_widgets(self):
        self.logo1_image = CTkImage(Image.open(resource_path("src/checked-user.png")), size=(50, 50))
        self.back_button_image = CTkImage(Image.open(resource_path("src/back.png")), size=(50, 50))
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
            command=self.back,
            fg_color="#B188A8",
            bg_color="#B188A8",
            hover_color="#886981",
        )
        self.back_button.place(x=10, y=10)

        # Initialize frames
        self.home_frame = HomeFrame(self, self.db)
        self.add_data_frame = AddDataFrame(self, self.db)
        self.data_frame = DataFrame(self, self.db)
    
    def show_frame(self,frame_to_show):
        for widget in self.home_frame.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=NORMAL)
        for widget in self.winfo_children():
            if widget != self.title_label:
                widget.pack_forget()
        frame_to_show.pack(fill="both", expand=True)
    
    def show_home_frame(self):
        self.show_frame(self.home_frame)
     
    def show_add_data_frame(self):
        self.show_frame(self.add_data_frame)
    
    def show_data_frame(self):
        self.show_frame(self.data_frame)
        self.data_frame.show_table()
        
    def back(self):
        self.home_frame.stop_attendance()
        self.show_frame(self.home_frame)

    def on_closing(self):
        self.add_data_frame.show_camera_frame.stop_camera()
        self.destroy()


if __name__ == "__main__":
    freeze_support()
    app = FaceAttendanceSystem()
    app.after(0, lambda: app.state('zoomed'))
    app.mainloop()
    sys.exit()