import pickle
from threading import Thread
from customtkinter import *
import cv2
import queue
import pyttsx3
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
        self.name_queue = queue.Queue()
        
        self.configure(border_width=4, border_color="#5665EF")
        self.image_label = CTkLabel(self, text="")
    
    def take_attendance(self):
        self.image_label.pack(padx=6, pady=6, fill="both")
        self.cap = cv2.VideoCapture(self.get_camera_choice())
        self.running = True
        Thread(target=self.camera_thread, daemon=True).start()
        Thread(target=self.say_name,daemon=True).start()
        
        
    def camera_thread(self):
        self.known_face = self.get_known_face()
        self.all_data = self.get_all_data()
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
            for id in self.known_face:
                if self.prediction(self.known_face[id],face_encoding):
                    name = self.all_data[id]
                    self.name_queue.put(name)
                    self.mark_present(id)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, name, (left, bottom - 6), font, 0.5, (0, 0, 0), 1)
                    break
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        return frame
    
    def say_name(self):
        previous = ""
        while self.running:
            if not self.name_queue.empty():
                now =self.name_queue.get()
                if previous != now:
                    previous = now
                    engine = pyttsx3.init()
                    engine.say(now )
                    engine.runAndWait()
    
    def stop(self):
        self.running = False
        
    def get_camera_choice(self):
        return int(get_config()["CHOICE"][0])
    
    def get_all_data(self):
        query = "SELECT ID, Name FROM student UNION ALL SELECT ID, Name from teacher;"
        data = self.db.fetch_data(query)
        return dict(data)
    
    def mark_present(self,id):
        def temp():
            self.db.execute_query(f"INSERT IGNORE INTO attendance (ID) VALUES('{id}')")
        Thread(target=temp,daemon=True).start()

    def get_known_face(self):
        data = {}
        profiles = self.db.fetch_data("SELECT ID,Encoding from student UNION ALL SELECT ID,Encoding from teacher;")
        for profile in profiles:
            if profile[1] != None:
                data[profile[0]] = pickle.loads(profile[1])
        return data
    
    @staticmethod
    def prediction(known_face_encodings, face_encoding_to_check, tolerance = 0.4, threshold = 70):
        guess = sum(face_recognition.compare_faces(known_face_encodings,face_encoding_to_check, tolerance))
        print(guess)
        if guess > threshold:
            return True
        return False