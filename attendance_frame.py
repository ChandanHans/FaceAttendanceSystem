import math
import pickle
import threading
from customtkinter import *
import cv2

from PIL import Image
from database import Database
import face_recognition

from utility import *

class AttendanceFrame(CTkFrame):
    def __init__(self, parent, db : Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.parent = parent
        self.running = False
        self.configure(border_width=4, border_color="#5665EF")
        self.image_label = CTkLabel(self, text="")
    
    def take_attendance(self):
        self.known_face = self.get_known_face()
        self.all_student_data = self.get_all_student_data()
        self.image_label.pack(padx=6, pady=6, fill="both")
        self.cap = cv2.VideoCapture(self.get_camera_choice())
        self.running = True
        self.camera_process_thread = threading.Thread(target=self.camera_thread, daemon=True)
        self.camera_process_thread.start()
        
        
    def camera_thread(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            processed_frame = self.process_frame(frame)
            self.after(10, lambda: self.update_frame(processed_frame))
        if self.cap is not None:
            self.cap.release()
            self.image_label.pack_forget()
        
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
    
    def process_frame(self, frame: cv2.typing.MatLike):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for face_location,face_encoding in zip(face_locations,face_encodings):
            top, right, bottom, left = face_location
            for roll in self.known_face:
                if self.prediction(self.known_face[roll],face_encoding):
                    name = self.all_student_data[roll]
                    self.mark_present(roll)
                    # Set font face
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    # Put text on the frame
                    cv2.putText(frame, name, (left, bottom - 6), font, 0.5, (0, 0, 0), 1)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        return frame
    
    def stop(self):
        self.running = False
        
    def get_camera_choice(self):
        return int(get_config()["CHOICE"][0])
    
    def get_all_student_data(self):
        query = "SELECT Roll,SName FROM students;"
        data = self.db.fetch_data(query)
        return dict(data)
    
    def mark_present(self,roll):
        self.db.execute_query(f"INSERT IGNORE INTO attendance (Roll) VALUES('{roll}')")
    
    @staticmethod
    def get_known_face():
        try:
            with open("known_faces.pkl", "rb") as file:
                data : dict = pickle.load(file)
            return data
        except Exception:
            return {}
    
    @staticmethod
    def prediction(known_face_encodings, face_encoding_to_check, tolerance = 0.45, threshold = 70):
        guess = sum(face_recognition.compare_faces(known_face_encodings,face_encoding_to_check, tolerance))
        print(guess)
        if guess > threshold:
            return True
        return False
    
    
        