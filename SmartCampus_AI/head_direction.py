import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True
)

def get_head_direction(frame):

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return "No Face"

    landmarks = results.multi_face_landmarks[0]

    nose = landmarks.landmark[1]

    left_cheek = landmarks.landmark[234]

    right_cheek = landmarks.landmark[454]

    face_center = (left_cheek.x + right_cheek.x) / 2

    difference = nose.x - face_center

    if difference < -0.03:
        return "Left"

    elif difference > 0.03:
        return "Right"

    else:
        return "Straight"