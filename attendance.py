import pickle
from queue import Queue
import threading
from tkinter import Tk
from customtkinter import *
import cv2
import pyttsx3
from database import Database
import face_recognition
from multiprocessing import freeze_support
from utility import *
import dlib
      
engine = pyttsx3.init() 
voice_queue = Queue()
latest_frame = None
frame_lock = threading.Lock()
stop = False
def capture_frames(stream_url):
    global latest_frame , cap
    cap = cv2.VideoCapture(stream_url)
    while not stop:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                latest_frame = frame
    cap.release()

def get_latest_frame():
    with frame_lock:
        return latest_frame.copy() if latest_frame is not None else None

def take_attendance(stop_event):
    global db, stop
    db = Database() 
    known_face = get_known_face()
    all_data = get_all_data()
    detector = dlib.get_frontal_face_detector()
    detected_name = ""
    threading.Thread(target=capture_frames, args=(get_camera_choice(),), daemon=True).start()
    
    frame_set = False
    stop = False
    while not stop_event.is_set():
        frame = get_latest_frame()
        if frame is not None:
            if not frame_set:
                frame_height = int(frame.shape[0]/3)
                frame_width = int(frame.shape[1]/3)
            frame = cv2.resize(frame, (frame_width,frame_height))
            face_detected = detector(frame)
            if face_detected:
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
                            threading.Thread(target=say_name,args=(name,)).start()
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(frame, name, (left, bottom - 6), font, 0.5, (0, 0, 0), 1)
                            break
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.imshow("Attendance",frame)
            if not frame_set:
                cv2.namedWindow('Attendance', cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('Attendance', cv2.WND_PROP_TOPMOST, 1)
                center_x, center_y = get_screen_center(frame_width,frame_height)
                cv2.moveWindow('Attendance', center_x, center_y)
                frame_set = True
        if cv2.waitKey(1) == ord('q'):
            break
    stop = True
  
def say_name(name):
    try:
        engine.say(name)
        engine.runAndWait()
    except:
        pass

def get_screen_center(window_width, window_height):
    """Returns the coordinates for the window to be centered on the screen."""
    # Initialize Tkinter root
    root = Tk()
    # Calculate positions for window to be in the center
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.destroy()  # Close the Tkinter root window
    return center_x, center_y

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
    threading.Thread(target=temp,daemon=True).start()

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