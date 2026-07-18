import cv2

for backend, name in [
    (cv2.CAP_DSHOW, "DirectShow"),
    (cv2.CAP_MSMF, "Media Foundation"),
    (cv2.CAP_ANY, "Default")
]:

    print(f"\nTesting {name}")

    camera = cv2.VideoCapture(1, backend)

    ret, frame = camera.read()

    print("Opened:", camera.isOpened())
    print("Frame:", ret)

    if ret:
        cv2.imshow(name, frame)
        cv2.waitKey(3000)

    camera.release()

cv2.destroyAllWindows()