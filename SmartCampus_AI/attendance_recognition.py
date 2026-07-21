import cv2
import pickle
import os
import requests
from datetime import datetime

RENDER_URL = "https://smart-campus-tn0o.onrender.com"
ROOM_CAMERAS = {

    "AC-1":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"

    },

    "AC-2":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"

    },

    "AC-3":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"
    },

    "AC-4":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"

    },

        "AC-5":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"

    },

        "AC-6":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"

    },

        "AC-7":{

        "type":"ip",

        "source":"http://10.172.59.40:8080/video"

    },
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


TRAINER = os.path.join(
    BASE_DIR,
    "SmartCampus_AI",
    "trainer",
    "trainer.yml"
)

LABELS = os.path.join(
    BASE_DIR,
    "SmartCampus_AI",
    "trainer",
    "labels.pkl"
)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(TRAINER)

with open(LABELS, "rb") as f:
    labels = pickle.load(f)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def session_active(session_id):

    try:

        response = requests.get(
            f"{RENDER_URL}/session_status",
            params={
                "session_id": session_id
            }
        )

        data = response.json()

        return data["active"]

    except Exception as e:

        print("Session check error:", e)

        return False

def student_name(student_id):

    try:

        response = requests.get(
            f"{RENDER_URL}/student_name",
            params={
                "student_id": student_id
            }
        )

        data = response.json()

        return data["name"]

    except:

        return "Unknown"


def attendance_exists(session_id, student_id):

    try:

        response = requests.get(
            f"{RENDER_URL}/attendance_exists",
            params={
                "session_id": session_id,
                "student_id": student_id
            }
        )

        data = response.json()

        return data["exists"]

    except Exception as e:

        print("Attendance check error:", e)

        return False


def insert_attendance(session_id, student_id):

    current_time = datetime.now().strftime("%I:%M:%S %p")

    try:

        response = requests.post(
            f"{RENDER_URL}/mark_attendance",
            json={
                "session_id": session_id,
                "student_id": student_id,
                "time": current_time
            }
        )

        print(response.json())

        print(
            f"{student_id} attendance sent"
        )


    except Exception as e:

        print("Attendance sending error:", e)

def start_attendance(session_id, room):
    camera_source = ROOM_CAMERAS[room]["source"]
    camera = cv2.VideoCapture(camera_source)

    cv2.namedWindow("Smart Campus Attendance")

    marked_students = set()

    while True:

        # -------------------------
        # Stop if teacher ended session
        # -------------------------

        if not session_active(session_id):
            print("Session Ended")
            break

        ret, frame = camera.read()

        if not ret:
            continue

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(120,120)
        )

        for (x,y,w,h) in faces:

            face = gray[y:y+h, x:x+w]

            try:

                label, confidence = recognizer.predict(face)

            except:

                continue

            # Ignore poor recognitions
            if confidence > 80:
                continue

            # Unknown label
            if label not in labels:
                continue

            student_id = labels[label]

            name = student_name(student_id)

            status = ""

            # --------------------------------
            # Already marked in THIS run
            # --------------------------------

            if student_id in marked_students:

                status = "Already Present"

            else:

                # ----------------------------
                # Already present in database?
                # ----------------------------

                if attendance_exists(
                    session_id,
                    student_id
                ):

                    marked_students.add(student_id)

                    status = "Already Present"

                else:

                    insert_attendance(
                        session_id,
                        student_id
                    )

                    marked_students.add(student_id)

                    status = "Attendance Marked"

                    print(f"{student_id} Marked")

            # -----------------------------
            # Draw Face Box
            # -----------------------------

            cv2.rectangle(
                frame,
                (x,y),
                (x+w,y+h),
                (0,255,0),
                2
            )

            # Name

            cv2.putText(

                frame,

                name,

                (x,y-15),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (255,255,255),

                2

            )

            # Status

            cv2.putText(

                frame,

                status,

                (x,y+h+25),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0,255,0),

                2

            )

            # Confidence

            cv2.putText(

                frame,

                f"{confidence:.1f}",

                (x,y+h+50),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0,255,255),

                2

            )

        cv2.putText(

            frame,

            "ESC = End Camera",

            (20,35),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255,255,255),

            2

        )

        cv2.imshow(

            "Smart Campus Attendance",

            frame

        )

        key = cv2.waitKey(1)

        if key == 27:
            break

    camera.release()

    cv2.destroyAllWindows()

    print("Attendance Engine Closed")
