import pickle
from queue import Queue
import threading
from time import sleep
from customtkinter import *
import cv2
from database import Database
import face_recognition
from multiprocessing import freeze_support
from utility import *
import dlib
from flask import Flask, Response


stop = False
latest_frame = None
latest_stream_frame = None
frame_lock = threading.Lock()
detected_id_queue = Queue()

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
    global db, stop, latest_stream_frame
    db = Database()
    known_face = get_known_face()
    detector = dlib.get_frontal_face_detector()
    threading.Thread(target = capture_frames, args=(get_camera_choice(),), daemon=True).start()
    threading.Thread(target = mark_present ,daemon=True).start()
    start_streaming()
    frame_set = False
    stop = False
    while not stop_event.is_set():
        frame = get_latest_frame()
        if frame is not None:
            if not frame_set:
                scale = get_config()["SCALE"]
                frame_height = int(frame.shape[0] * scale)
                frame_width = int(frame.shape[1] * scale)
            frame = cv2.resize(frame, (frame_width,frame_height))
            face_detected = detector(frame)
            if face_detected:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                for face_location,face_encoding in zip(face_locations,face_encodings):
                    top, right, bottom, left = face_location
                    for profile in known_face:
                        if prediction(profile[2],face_encoding):
                            name = profile[1]
                            detected_id_queue.put(id)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(frame, name, (left, bottom + 20), font, 1 * scale, (0, 0, 255), 2)
                            break
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            latest_stream_frame = frame
            cv2.imshow("Attendance",frame)
            if not frame_set:
                cv2.namedWindow('Attendance', cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('Attendance', cv2.WND_PROP_TOPMOST, 1)
                frame_set = True
        if cv2.waitKey(1) == ord('q'):
            break
    stop = True


def get_camera_choice():
    if get_config()["CHOICE"][0] == "3":
        return get_config()["CHOICE"][2]
    return int(get_config()["CHOICE"][0])

def mark_present():
    global detected_id_queue, stop
    previous_name = ""
    while not stop:
        if not detected_id_queue.empty():
            new_name = detected_id_queue.get()
            if previous_name != new_name:
                try:
                    db.execute_query(f"INSERT IGNORE INTO attendance (ID) VALUES('{new_name}')")
                    previous_name = new_name
                except:
                    pass   
        sleep(1)

def get_known_face():
    try:
        with open('face_data.pkl', 'rb') as file:
            data = pickle.load(file)
            return data
    except:
        data = []
        profiles = db.fetch_data("SELECT ID, Name, Encoding from student UNION ALL SELECT ID, Name, Encoding from teacher;")
        for profile in profiles:
            if profile[2] is not None:
                id, name, encoding = profile[0], profile[1], pickle.loads(profile[2])
                data.append((id, name, encoding))
        with open('face_data.pkl', 'wb') as file:
            pickle.dump(data, file)
        return data

def prediction(known_face_encodings, face_encoding_to_check, tolerance = 0.42, threshold = 70):
    guess = sum(face_recognition.compare_faces(known_face_encodings,face_encoding_to_check, tolerance))
    if guess > threshold:
        return True
    return False


def generate_video_stream():
    global latest_stream_frame
    while True:
        if latest_stream_frame is not None:
            ret, buffer = cv2.imencode('.jpg', latest_stream_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

app = Flask(__name__)
@app.route('/')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_streaming():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),daemon=True).start()
    
if __name__ == '__main__':
    freeze_support()