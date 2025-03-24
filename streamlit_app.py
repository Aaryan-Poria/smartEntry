import streamlit as st
import cv2
import sqlite3
from simple_facerec import SimpleFacerec
from admin import admin_page

st.set_page_config(page_title="SmartEntry", layout="wide")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Sidebar for Admin Access
with st.sidebar:
    if st.button("Admin", key="admin_btn"):
        st.session_state["page"] = "admin"

# Admin Page
if st.session_state.get("page") == "admin":
    admin_page()
    st.stop()

# Main Page (Face Recognition)
st.title("Smart Entry System")
st.write("Please face the camera to verify your identity.")

# Load face recognition model
sfr = SimpleFacerec()
sfr.load_encoding_images("known_images/")

# Open Camera Stream
cap = cv2.VideoCapture(0)
frame_placeholder = st.empty()
result_placeholder = st.empty()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to grab frame. Please check your camera.")
        break

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)

    verification_result = ""
    for name in face_names:
        conn = sqlite3.connect("smart_entry.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, apartment_number, entry_time, exit_time FROM domestic_help WHERE unique_id = ?", (name,))
        result = cursor.fetchone()
        conn.close()

        if result:
            verification_result = f"✅ **Verified:** {result[0]}<br>🏠 **Apartment:** {result[1]}<br>🕒 **Entry Time:** {result[2]}<br>🚪 **Exit Time:** {result[3]}"
            result_placeholder.markdown(f'<p style="color: green; font-size: 20px;">{verification_result}</p>', unsafe_allow_html=True)
        else:
            verification_result = "❌ **No match found!** Please contact building management."
            result_placeholder.markdown(f'<p style="color: red; font-size: 20px;">{verification_result}</p>', unsafe_allow_html=True)

    # Display Camera Feed
    frame_placeholder.image(frame, channels="BGR")

# Release Camera when Streamlit stops
cap.release()
cv2.destroyAllWindows()
