import cv2
import os
from head_direction import get_head_direction 
student_id = input("Enter Student ID: ")

folder = f"dataset/{student_id}"

if not os.path.exists(folder):
    os.makedirs(folder)

camera = cv2.VideoCapture(1)   # <-- Replace with your DroidCam number

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

count = 0

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

    for (x, y, w, h) in faces:

        face = gray[y:y+h, x:x+w]

        count += 1

        cv2.imwrite(
            f"{folder}/{count}.jpg",
            face
        )

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Images: {count}/100",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    cv2.imshow("Register Student", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if count >= 100:
        break

camera.release()
cv2.destroyAllWindows()

print("Registration Complete!") 