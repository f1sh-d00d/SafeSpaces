import cv2

def getVideoFeed():
    capture = cv2.VideoCapture(0)
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        
        cv2.imshow('Live Video', frame)

    capture.release()


