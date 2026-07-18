import cv2

for i in range(10):
    camera = cv2.VideoCapture(i)
    success, frame = camera.read()

    if success:
        print(f"Camera {i} is working")
    else:
        print(f"Camera {i} not available")

    camera.release()