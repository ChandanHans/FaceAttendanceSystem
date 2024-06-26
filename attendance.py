import pickle
from queue import Queue
import socket
import threading
from time import sleep
from customtkinter import *
import cv2
from database import Database
import face_recognition
from multiprocessing import Event, freeze_support
from utility import *
import pyttsx3
import dlib
from flask import Flask, Response
from datetime import datetime



stop = False
latest_frame = None
latest_stream_frame = None
frame_lock = threading.Lock()
detected_id_queue = Queue()


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = str(s.getsockname()[0])
        s.close()
    except Exception as e:
        ip = "ERROR"
    return ip


streaming_ip = get_local_ip() + ":5000"


def capture_frames(stream_url):
    global latest_frame, cap
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
    threading.Thread(
        target=capture_frames, args=(get_camera_choice(),), daemon=True
    ).start()
    threading.Thread(target=mark_present, daemon=True).start()
    start_streaming()
    frame_set = False
    stop = False
    while not stop_event.is_set():
        frame = get_latest_frame()
        if frame is not None:
            if not frame_set:
                scale = get_config()["scale"]
                frame_height = int(frame.shape[0] * scale)
                frame_width = int(frame.shape[1] * scale)
            frame = cv2.resize(frame, (frame_width, frame_height))
            face_detected = detector(frame)
            if face_detected:
                face_in_frame = []
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                for face_location, face_encoding in zip(face_locations, face_encodings):
                    top, right, bottom, left = face_location
                    for profile in known_face:
                        if prediction(profile[2], face_encoding):
                            name = profile[1]
                            face_in_frame.append((profile[0], profile[1], profile[3]))
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(
                                frame,
                                name,
                                (left, bottom + 20),
                                font,
                                1 * scale,
                                (0, 0, 255),
                                1,
                            )
                            break
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 1)
                detected_id_queue.put(face_in_frame)
            latest_stream_frame = frame
            cv2.imshow(streaming_ip, frame)
            if not frame_set:
                cv2.namedWindow(streaming_ip, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(streaming_ip, cv2.WND_PROP_TOPMOST, 1)
                frame_set = True
        if cv2.waitKey(1) == ord("q"):
            break
    stop = True


def get_camera_choice():
    camera_choice = get_config()["camera_choice"]
    if camera_choice == 3:
        return get_config()["camera_ip"]
    return int(camera_choice)


def mark_present():
    global detected_id_queue, stop
    max_checkin = datetime.strptime(get_config()["max_checkin"], "%H:%M:%S").time()
    min_checkout = datetime.strptime(get_config()["min_checkout"], "%H:%M:%S").time()
    last_ten_frame = []
    engine = pyttsx3.init()
    audio_choice = get_config()["audio_choice"]
    while not stop:
        if not detected_id_queue.empty():
            current_time = datetime.now()
            date = current_time.strftime("%Y-%m-%d")
            time = current_time.strftime("%H:%M:%S")
            recent_detection = detected_id_queue.get()    # [(ID, Name, Role),]
            recently_detected = False
            for person in recent_detection:
                for i in last_ten_frame:
                    for j in i:
                        if j == person:
                            recently_detected = True
                            break
                if not recently_detected:
                    if audio_choice:
                        engine.say(person[1])
                        engine.runAndWait()
                    try:
                        if person[2] == "student":
                            db.execute_query(
                                """
                                INSERT IGNORE INTO 
                                    student_attendance (ID, Date, CheckIn) 
                                VALUES
                                    (%s, %s, %s)
                                """,
                                (person[0], date, time),
                            )
                        else:
                            if current_time.time() < max_checkin:
                                db.execute_query(
                                    """
                                    INSERT IGNORE INTO 
                                        staff_attendance (ID, Date, CheckIn) 
                                    VALUES
                                        (%s, %s, %s)
                                    ON DUPLICATE KEY 
                                    UPDATE 
                                        CheckIn = VALUES(CheckIn);
                                    """,
                                    (person[0], date, time),
                                )
                            elif current_time.time() > min_checkout:
                                db.execute_query(
                                    """
                                    INSERT INTO 
                                        staff_attendance (ID, Date, CheckOut) 
                                    VALUES 
                                        (%s, %s, %s) 
                                    ON DUPLICATE KEY 
                                    UPDATE 
                                        CheckOut = VALUES(CheckOut);
                                    """,
                                    (person[0], date, time),
                                )
                    except:
                        pass
            if len(last_ten_frame) == 10:
                last_ten_frame.pop()
            last_ten_frame.insert(0,recent_detection)
        sleep(0.1)


def get_known_face():
    try:
        with open("face_data.pkl", "rb") as file:
            data = pickle.load(file)
            return data
    except:
        data = []
        profiles = db.fetch_data(
            """
            SELECT
                ID,
                Name,
                Encoding, 
                'student' as Role 
            FROM
                student_face 
            UNION ALL 
            SELECT 
                ID, 
                Name, 
                Encoding, 
                'staff' as Role 
            FROM
                staff_face;
            """)
        for profile in profiles:
            if profile[2] is not None:
                id, name, encoding, role = (
                    profile[0],
                    profile[1],
                    pickle.loads(profile[2]),
                    profile[3],
                )
                data.append((id, name, encoding, role))
        with open("face_data.pkl", "wb") as file:
            pickle.dump(data, file)
        return data


def prediction(
    known_face_encodings, face_encoding_to_check, tolerance=0.42, threshold=70
):
    guess = sum(
        face_recognition.compare_faces(
            known_face_encodings, face_encoding_to_check, tolerance
        )
    )
    if guess > threshold:
        return True
    return False


def generate_video_stream():
    global latest_stream_frame
    while True:
        if latest_stream_frame is not None:
            ret, buffer = cv2.imencode(".jpg", latest_stream_frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


app = Flask(__name__)


@app.route("/")
def video_feed():
    return Response(
        generate_video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def start_streaming():
    threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0", port=5000, debug=False, use_reloader=False
        ),
        daemon=True,
    ).start()


if __name__ == "__main__":
    freeze_support()
    stop_event = Event()
    take_attendance(stop_event)
