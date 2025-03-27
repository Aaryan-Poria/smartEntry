import cv2
from simple_facerec import SimpleFacerec
import sqlite3
from datetime import datetime

# Initialize SimpleFacerec and load known faces
sfr = SimpleFacerec()
sfr.load_encoding_images("known_images/")  # Load known faces

# Connect to database (check_same_thread=False for threading issues)
conn = sqlite3.connect("smart_entry.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure access_logs table exists (if not already created via database.py)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        timestamp DATETIME,
        status TEXT
    )
""")
conn.commit()

# Dictionary to store last logged time for each user (to prevent duplicate logging)
last_logged = {}

# Open Webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    face_locations, face_names = sfr.detect_known_faces(frame)

    for face_loc, user_id in zip(face_locations, face_names):
        # Fetch user details from the database
        cursor.execute("SELECT name, entry_time, exit_time FROM domestic_help WHERE unique_id = ?", (user_id,))
        result = cursor.fetchone()

        current_time = datetime.now().time()
        access_status = "Denied"
        display_name = "Unknown"
        if result:
            name, entry_time_str, exit_time_str = result
            allowed_start = datetime.strptime(entry_time_str, "%H:%M").time()
            allowed_end = datetime.strptime(exit_time_str, "%H:%M").time()

            if allowed_start <= current_time <= allowed_end:
                display_name = name  # Access granted
                access_status = "Granted"
            else:
                display_name = "Access Denied"
                access_status = "Denied"
        else:
            display_name = "Unknown"
            access_status = "Denied"

        # Log the event (only once every 10 seconds per user)
        now = datetime.now()
        last_time = last_logged.get(user_id)
        if last_time is None or (now - last_time).total_seconds() > 10:
            cursor.execute(
                "INSERT INTO access_logs (user_id, name, timestamp, status) VALUES (?, ?, ?, ?)",
                (user_id, result[0] if result else "Unknown", now, access_status)
            )
            conn.commit()
            last_logged[user_id] = now

        # Draw rectangle and display access status on the frame
        y1, x2, y2, x1 = face_loc
        cv2.putText(frame, display_name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

    cv2.imshow("Smart Entry", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
