import cv2
import pickle
import sqlite3
import os

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

trainer_path = os.path.join(BASE_DIR, "SmartCampus_AI", "trainer")

# ----------------------------
# Load Model
# ----------------------------
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(os.path.join(trainer_path, "trainer.yml"))

# ----------------------------
# Load Label Map
# ----------------------------
with open(os.path.join(trainer_path, "labels.pkl"), "rb") as f:
    labels = pickle.load(f)

# ----------------------------
# Face Detector
# ----------------------------
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# ----------------------------
# Database
# ----------------------------
connection = sqlite3.connect(
    os.path.join(BASE_DIR, "smartcampus.db")
)

cursor = connection.cursor()

# ----------------------------
# Camera
# ----------------------------
camera = cv2.VideoCapture(1, cv2.CAP_MSMF)

cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Face Recognition",900,700)

while True:

    ret, frame = camera.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        1.2,
        5
    )

    for (x,y,w,h) in faces:

        face = gray[y:y+h,x:x+w]

        label, confidence = recognizer.predict(face)

        student_id = labels[label]

        cursor.execute("""
        SELECT Name
        FROM Students
        WHERE StudentID=?
        """,(student_id,))

        student = cursor.fetchone()

        if student:

            name = student[0]

        else:

            name = "Unknown"

        cv2.rectangle(
            frame,
            (x,y),
            (x+w,y+h),
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
            f"Confidence: {confidence:.1f}",
            (x,y+h+25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,255),
            2
        )

    cv2.imshow("Face Recognition",frame)

    if cv2.waitKey(1)==27:
        break

camera.release()
connection.close()
cv2.destroyAllWindows()