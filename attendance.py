import pickle
from queue import Queue
from threading import Thread
from customtkinter import *
import cv2
import pyttsx3
from database import Database
import face_recognition
from multiprocessing import freeze_support
from utility import *

        
engine = pyttsx3.init() 
voice_queue = Queue()

def take_attendance():
    global db
    
    db = Database() 
    
    cap = cv2.VideoCapture(get_camera_choice())
    known_face = get_known_face()
    all_data = get_all_data()

    detected_name = ""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for face_location,face_encoding in zip(face_locations,face_encodings):
            top, right, bottom, left = face_location
            for id in known_face:
                if prediction(known_face[id],face_encoding):
                    name = all_data[id]
                    voice_queue.put(name)
                    if detected_name != name:
                        mark_present(id)
                        detected_name = name
                    Thread(target=say_name,args=(name,)).start()
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, name, (left, bottom - 6), font, 0.5, (0, 0, 0), 1)
                    break
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.imshow("Attendance",frame)
        if cv2.waitKey(1) == ord('q'):
            break
        
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()

        
def say_name(name):
    try:
        engine.say(name)
        engine.runAndWait()
    except:
        pass

    
def get_camera_choice():
    if get_config()["CHOICE"][0] == "3":
        return get_config()["CHOICE"][2]
    return int(get_config()["CHOICE"][0])

def get_all_data():
    query = "SELECT ID, Name FROM student UNION ALL SELECT ID, Name from teacher;"
    data = db.fetch_data(query)
    return dict(data)

def mark_present(id):
    def temp():
        db.execute_query(f"INSERT IGNORE INTO attendance (ID) VALUES('{id}')")
    Thread(target=temp,daemon=True).start()

def get_known_face():
    data = {}
    profiles = db.fetch_data("SELECT ID,Encoding from student UNION ALL SELECT ID,Encoding from teacher;")
    for profile in profiles:
        if profile[1] != None:
            data[profile[0]] = pickle.loads(profile[1])
    return data

def prediction(known_face_encodings, face_encoding_to_check, tolerance = 0.42, threshold = 70):
    guess = sum(face_recognition.compare_faces(known_face_encodings,face_encoding_to_check, tolerance))
    if guess > threshold:
        return True
    return False


if __name__ == '__main__':
    freeze_support()