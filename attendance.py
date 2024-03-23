import pickle
from threading import Thread
from customtkinter import *
import cv2
import queue
import pyttsx3
from PIL import Image
from database import Database
import face_recognition

from loading_animation import LoadingAnimation
from utility import *

class Attendance():
    def __init__(self, parent, db : Database):
        self.db = db
        self.parent = parent
        self.running = False
        self.voice_queue = queue.Queue()
        self.detected_name = ""
        self.engine = pyttsx3.init()
    
    def take_attendance(self):
        self.loading = LoadingAnimation(self.parent)
        self.running = True
        Thread(target=self.camera_thread, daemon=True).start()
        Thread(target=self.say_name,daemon=True).start()
        
        
    def camera_thread(self):
        self.cap = cv2.VideoCapture(self.get_camera_choice())
        self.known_face = self.get_known_face()
        self.all_data = self.get_all_data()
        self.loading.stop()
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            processed_frame = self.process_frame(frame)
            cv2.imshow("Attendance",processed_frame)
            if cv2.waitKey(1) == ord('q'):
                break
        for widget in self.parent.winfo_children():
            if type(widget) == CTkButton:
                widget.configure(state=NORMAL)
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
        
    def process_frame(self, frame: cv2.typing.MatLike):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for face_location,face_encoding in zip(face_locations,face_encodings):
            top, right, bottom, left = face_location
            for id in self.known_face:
                if self.prediction(self.known_face[id],face_encoding):
                    name = self.all_data[id]
                    self.voice_queue.put(name)
                    if self.detected_name != name:
                        self.mark_present(id)
                        self.detected_name = name
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, name, (left, bottom - 6), font, 0.5, (0, 0, 0), 1)
                    break
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        return frame
    
    def say_name(self):
        previous = ""
        while self.running:
            if not self.voice_queue.empty():
                now =self.voice_queue.get()
                if previous != now:
                    previous = now
                    self.engine.say(now )
                    self.engine.runAndWait()
    
    def stop(self):
        self.running = False
        
    def get_camera_choice(self):
        if get_config()["CHOICE"][0] == "3":
            return get_config()["CHOICE"][2]
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
    def prediction(known_face_encodings, face_encoding_to_check, tolerance = 0.42, threshold = 70):
        guess = sum(face_recognition.compare_faces(known_face_encodings,face_encoding_to_check, tolerance))
        if guess > threshold:
            return True
        return False