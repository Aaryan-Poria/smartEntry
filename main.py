import cv2
from simple_facerec import SimpleFacerec
import sqlite3
import os
from datetime import datetime

# Initialize SimpleFacerec
sfr = SimpleFacerec()
sfr.load_encoding_images("known_images/")  # Load known faces

# Connect to database
conn = sqlite3.connect("smart_entry.db")
cursor = conn.cursor()

# Open Webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    face_locations, face_names = sfr.detect_known_faces(frame)

    for face_loc, user_id in zip(face_locations, face_names):
        # Fetch name and access time from DB
        cursor.execute("SELECT name, entry_time, exit_time FROM domestic_help WHERE unique_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            name, entry_time, exit_time = result
            current_time = datetime.now().strftime("%H:%M")

            # Check if the current time is within allowed time range
            if entry_time <= current_time <= exit_time:
                display_name = name  # Access granted
            else:
                display_name = "Access Denied"
        else:
            display_name = "Unknown"

        # Draw rectangle and name/status
        y1, x2, y2, x1 = face_loc
        cv2.putText(frame, display_name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

    cv2.imshow("Smart Entry", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
