import streamlit as st
import cv2
import sqlite3
from simple_facerec import SimpleFacerec
from admin import admin_page
from datetime import datetime
from database import init_db

# Initialize the database (creates tables if missing)
init_db()

st.set_page_config(page_title="SmartEntry", layout="wide")

# Custom CSS for Styling - Professional Dark Red Theme & Centered Image
st.markdown(
    """
    <style>
        /* Style the Sidebar Navigation */
        [data-testid="stSidebar"] {
            background-color: #8B0000; /* Dark Red */
        }
        
        [data-testid="stSidebarNav"] button {
            font-size: 18px !important;
            font-weight: bold !important;
            color: white !important;
            border-radius: 10px !important;
            border: 2px solid white !important;
            margin-bottom: 10px !important;
        }

        [data-testid="stSidebarNav"] button:hover {
            background-color: #A52A2A !important; /* A slightly lighter red */
            color: white !important;
        }

        /* Style the Verification Result Box */
        .result-box {
            border: 5px solid #8B0000; /* Dark Red Border */
            padding: 20px;
            border-radius: 15px;
            background-color: #F5F5F5; /* Light background for contrast */
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            text-align: center;
            margin-top: 20px;
        }

        /* Style Main Title */
        .main-title {
            font-size: 28px;
            font-weight: bold;
            color: #8B0000;
            text-align: center;
        }
        
        /* Center all images */
        img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.markdown("<h2 style='color:white; text-align:center;'>Smart Entry</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["Home", "Admin"])
st.session_state["page"] = page

# If "Admin" is selected, display the admin page and stop further execution.
if st.session_state["page"] == "Admin":
    admin_page()
    st.stop()

st.markdown("<div class='main-title'>Please Face the Camera to Verify Identity</div>", unsafe_allow_html=True)

# Initialize face recognition model
sfr = SimpleFacerec()
sfr.load_encoding_images("known_images/")

# Open the camera stream
cap = cv2.VideoCapture(0)
frame_placeholder = st.empty()
result_placeholder = st.empty()

# Dictionary to store last logged time to avoid duplicate logging
last_logged = {}

while cap.isOpened():
    # Check if user navigated away from Home; if so, break the loop immediately.
    if st.session_state.get("page") != "Home":
        break

    ret, frame = cap.read()
    if not ret:
        st.error("Failed to grab frame. Please check your camera.")
        break

    # Detect faces in the frame
    face_locations, face_names = sfr.detect_known_faces(frame)

    for face_loc, user_id in zip(face_locations, face_names):
        # Connect to DB and fetch user details
        conn = sqlite3.connect("smart_entry.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, apartment_number, entry_time, exit_time FROM domestic_help WHERE unique_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()

        current_time = datetime.now().time()
        if result:
            name, apartment, entry_time_str, exit_time_str = result
            allowed_start = datetime.strptime(entry_time_str, "%H:%M").time()
            allowed_end = datetime.strptime(exit_time_str, "%H:%M").time()
            if allowed_start <= current_time <= allowed_end:
                # Recognized and allowed
                verification_result = (
                    f"<div class='result-box'><b>✅ Recognized and Allowed</b><br>"
                    f"Name: {name}<br>"
                    f"Apartment: {apartment}<br>"
                    f"Allowed Entry: {entry_time_str}<br>"
                    f"Allowed Exit: {exit_time_str}</div>"
                )
                access_status = "Granted"
            else:
                # Recognized but not allowed
                verification_result = (
                    f"<div class='result-box' style='border-color: red;'><b>⛔ Recognized but Not Allowed</b><br>"
                    f"Name: {name}<br>"
                    f"Apartment: {apartment}<br>"
                    f"Allowed Entry: {entry_time_str}<br>"
                    f"Allowed Exit: {exit_time_str}<br>"
                    f"Current time is outside the allowed window.</div>"
                )
                access_status = "Denied"
        else:
            # Unrecognized
            verification_result = (
                "<div class='result-box' style='border-color: red;'><b>❌ Unrecognized</b><br>"
                "No matching record found! Please contact building management.</div>"
            )
            access_status = "Denied"

        # Logging: Only log once every 10 seconds per user
        now = datetime.now()
        last_time = last_logged.get(user_id)
        if last_time is None or (now - last_time).total_seconds() > 10:
            conn = sqlite3.connect("smart_entry.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO access_logs (user_id, name, timestamp, status) VALUES (?, ?, ?, ?)",
                (user_id, result[0] if result else "Unknown", now, access_status)
            )
            conn.commit()
            conn.close()
            last_logged[user_id] = now

        result_placeholder.markdown(verification_result, unsafe_allow_html=True)

    # Display the current frame
    frame_placeholder.image(frame, channels="BGR")

cap.release()
cv2.destroyAllWindows()
