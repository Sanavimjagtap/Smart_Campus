import cv2
import pickle
import sqlite3
import os
from datetime import datetime

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

DATABASE = os.path.join(BASE_DIR, "smartcampus.db")

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

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
    SELECT EndTime
    FROM Sessions
    WHERE SessionID=?
    """, (session_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return False

    end_time = row[0]

    if end_time == "":
        return True

    return False


def student_name(student_id):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
    SELECT Name
    FROM Students
    WHERE StudentID=?
    """, (student_id,))

    row = cursor.fetchone()

    connection.close()

    if row:
        return row[0]

    return "Unknown"


def attendance_exists(session_id, student_id):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
    SELECT AttendanceID
    FROM Attendance
    WHERE SessionID=? AND StudentID=?
    """, (session_id, student_id))

    row = cursor.fetchone()

    connection.close()

    return row is not None


def insert_attendance(session_id, student_id):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    current_time = datetime.now().strftime("%I:%M:%S %p")

    cursor.execute("""
    INSERT INTO Attendance
    (
        SessionID,
        StudentID,
        TimeMarked
    )
    VALUES (?, ?, ?)
    """,
    (
        session_id,
        student_id,
        current_time
    ))
    connection.commit()

    print("Session committed!")
    print("Session ID:", session_id)
    
    cursor.execute("SELECT * FROM Sessions")
    print(cursor.fetchall())
    
    connection.close()

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
