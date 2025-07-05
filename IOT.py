import cv2
import dlib
import numpy as np
import serial
import serial.tools.list_ports
import time
from imutils import face_utils
from scipy.spatial import distance as dist

# ----------- Arduino Port Auto-Detection -----------
port_input = input("Enter your Arduino port (e.g., COM3): ").strip()
if not port_input.upper().startswith("COM"):
    arduino_port = f"COM{port_input}"
else:
    arduino_port = port_input

print(f"Connecting to Arduino on {arduino_port}...")
ser = serial.Serial(arduino_port, 9600, timeout=1)


arduino_port = find_arduino_port()
print(f"Connecting to Arduino on {arduino_port}...")
ser = serial.Serial(arduino_port, 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset
COM
# ----------- Dlib & OpenCV Setup -----------
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r".\shape_predictor_68_face_landmarks.dat")

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 20
COUNTER = 0
ALARM_ON = False

cap = cv2.VideoCapture(0)
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            # Draw eye contours (for visualization)
            leftHull = cv2.convexHull(leftEye)
            rightHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightHull], -1, (0, 255, 0), 1)

            # Drowsiness detection logic
            if ear < EAR_THRESHOLD:
                COUNTER += 1
                if COUNTER >= CONSEC_FRAMES:
                    if not ALARM_ON:
                        ser.write(b'A')  # Alert: eyes closed
                        ALARM_ON = True
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                COUNTER = 0
                if ALARM_ON:
                    ser.write(b'B')  # Normal: eyes open
                    ALARM_ON = False

            cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow("Drowsiness Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    if ser.is_open:
        ser.close()
