import cv2
import pickle
import sqlite3
import os
from datetime import datetime

ROOM_CAMERAS = {

    "AC-1": 1,
    "AC-2": 1,
    "AC-3": 1,
    "AC-4": 1,
    "AC-5": 1,
    "AC-6": 1,

    "AC-7": 1,
    "AC-8": 1,
    "AC-9": 1,
    "AC-10": 1,
    "AC-11": 1,
    "AC-12": 1,

    "CS Lab 1": 12,
    "CS Lab 2": 13,

    "Electronics Lab 1": 14,
    "Electronics Lab 2": 15

}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -------------------------
# Load AI Model
# -------------------------

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(
    os.path.join(
        BASE_DIR,
        "SmartCampus_AI",
        "trainer",
        "trainer.yml"
    )
)

# -------------------------
# Load Labels
# -------------------------

with open(
    os.path.join(
        BASE_DIR,
        "SmartCampus_AI",
        "trainer",
        "labels.pkl"
    ),
    "rb"
) as f:

    labels = pickle.load(f)

# -------------------------
# Face Detector
# -------------------------

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def start_attendance(session_id):

    connection = sqlite3.connect(
        os.path.join(BASE_DIR, "smartcampus.db")
    )

    cursor = connection.cursor()
    cursor.execute("""
    SELECT Room
    FROM Sessions
    WHERE SessionID=?
    """,(session_id,))

    room = cursor.fetchone()[0]
    marked_students = set()

    camera_number = ROOM_CAMERAS.get(room, 0)

    camera = cv2.VideoCapture(camera_number, cv2.CAP_MSMF)

    cv2.namedWindow("Smart Campus Attendance")

    while True:

        # Check if session has ended
        cursor.execute("""
        SELECT EndTime
        FROM Sessions
        WHERE SessionID=?
        """, (session_id,))

        result = cursor.fetchone()

        if result is not None:
            end_time = result[0]

            if end_time != "":
                print("Session ended. Closing camera...")
                break

        ret, frame = camera.read()

        if not ret:
            break

        faces = face_detector.detectMultiScale(
            gray,
            1.2,
            5
        )

        for (x, y, w, h) in faces:

            face = gray[y:y+h, x:x+w]

            label, confidence = recognizer.predict(face)

            student_id = labels[label]

            # Ignore poor matches
            if confidence > 80:
                continue

            cursor.execute("""
            SELECT Name
            FROM Students
            WHERE StudentID=?
            """,
            (student_id,)
            )

            result = cursor.fetchone()

            if result:
                name = result[0]
            else:
                name = "Unknown"

            status = ""

            if student_id not in marked_students:

                cursor.execute("""
                SELECT *
                FROM Attendance
                WHERE SessionID=? AND StudentID=?
                """,
                (
                    session_id,
                    student_id
                )
                )

                record = cursor.fetchone()

                if record is None:

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
                    )
                    )

                    connection.commit()

                    marked_students.add(student_id)

                    status = "Attendance Marked"

                else:

                    status = "Already Present"

                    marked_students.add(student_id)

            else:

                status = "Already Present"

            cv2.rectangle(
                frame,
                (x, y),
                (x+w, y+h),
                (0,255,0),
                2
            )

            cv2.putText(
                frame,
                name,
                (x,y-15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,255),
                2
            )

            cv2.putText(
                frame,
                status,
                (x,y+h+25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0,255,0),
                2
            )

            cv2.putText(
                frame,
                f"{confidence:.1f}",
                (x,y+h+50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,255),
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
    connection.close()
    cv2.destroyAllWindows()