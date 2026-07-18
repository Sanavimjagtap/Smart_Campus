import cv2
import os
import numpy as np
import pickle

print("Program Started")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_path = os.path.join(BASE_DIR, "dataset")

print("Dataset:", dataset_path)

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []

label_map = {}
current_label = 0

print("Loading dataset...")

for student_id in sorted(os.listdir(dataset_path)):

    student_folder = os.path.join(dataset_path, student_id)

    if not os.path.isdir(student_folder):
        continue

    print("Reading", student_id)

    label_map[current_label] = student_id

    for image_name in os.listdir(student_folder):

        image_path = os.path.join(student_folder, image_name)

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            continue

        faces.append(image)
        labels.append(current_label)

    current_label += 1

print(f"Images Loaded: {len(faces)}")

recognizer.train(faces, np.array(labels))

trainer_folder = os.path.join(BASE_DIR, "SmartCampus_AI", "trainer")
os.makedirs(trainer_folder, exist_ok=True)

recognizer.save(os.path.join(trainer_folder, "trainer.yml"))

with open(os.path.join(trainer_folder, "labels.pkl"), "wb") as f:
    pickle.dump(label_map, f)

print("Training Complete!")