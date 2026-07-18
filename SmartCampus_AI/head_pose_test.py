import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True
)

camera = cv2.VideoCapture(1, cv2.CAP_MSMF)

while True:

    ret, frame = camera.read()

    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb)

    direction = "No Face"

    if results.multi_face_landmarks:

        landmarks = results.multi_face_landmarks[0]

        nose = landmarks.landmark[1]
        left_cheek = landmarks.landmark[234]
        right_cheek = landmarks.landmark[454]

        nose_x = nose.x
        left_x = left_cheek.x
        right_x = right_cheek.x

        face_center = (left_x + right_x) / 2

        difference = nose_x - face_center

        if difference < -0.03:
            direction = "Looking Left"

        elif difference > 0.03:
            direction = "Looking Right"

        else:
            direction = "Looking Straight"

    cv2.putText(
        frame,
        direction,
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Head Pose Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()