import cv2
import numpy as np

def detect_fire(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([18, 50, 50], dtype="uint8")
    upper_bound = np.array([35, 255, 255], dtype="uint8")
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    fire_detected = cv2.bitwise_and(frame, frame, mask=mask)
    return fire_detected, mask

cap = cv2.VideoCapture(0)  # Start video capture from the default webcam



while True:
    ret, frame = cap.read()
    if not ret:
        break  # Break the loop if the frame isn't captured properly

    # Apply the fire detection function
    fire_detected, mask = detect_fire(frame)

    # Blend the fire-detected areas with the original frame
    combined = cv2.addWeighted(frame, 0.7, fire_detected, 0.3, 0)


  

    # Show the combined frame with fire detection highlighted
    cv2.imshow("Fire Detection", combined)

    # Press 'q' to break the loop and close the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
