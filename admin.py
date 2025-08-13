import streamlit as st
import sqlite3
import os
import uuid  

ADMIN_CREDENTIALS = {"admin": "password123"}

def authenticate(username, password):
    return ADMIN_CREDENTIALS.get(username) == password

def admin_page():
    st.title("Admin Dashboard")
    
    # Container for login/admin controls
    container = st.container()
    
    # Ensure authentication state exists
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        with container.form("login_form"):
            st.subheader("Please log in to continue")
            username = st.text_input("Username", key="admin_username")
            password = st.text_input("Password", type="password", key="admin_password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if authenticate(username, password):
                    st.session_state["authenticated"] = True
                    st.success("Logged in successfully!")
                    container.empty()  # Clear login form immediately after login
                else:
                    st.error("Invalid credentials!")
    
    if st.session_state["authenticated"]:
        st.success("Logged in as Admin")
        # Sidebar for admin-specific actions
        action = st.sidebar.radio("Admin Actions", ["Add Worker/Resident", "Delete Worker/Resident", "Show Logs"])

        if action == "Add Worker/Resident":
            st.subheader("Add Worker/Resident")
            # Unique ID is generated automatically
            auto_unique_id = str(uuid.uuid4())
            st.info(f"Generated Unique ID: {auto_unique_id}")
            
            name = st.text_input("Name", key="add_name")
            apartment = st.text_input("Apartment Number", key="add_apartment")
            entry_time = st.text_input("Allowed Entry Time (HH:MM)", key="add_entry_time")
            exit_time = st.text_input("Allowed Exit Time (HH:MM)", key="add_exit_time")
            # File uploader for the image
            uploaded_file = st.file_uploader("Upload User Image", type=["jpg", "jpeg", "png"], key="upload_image")
            
            if st.button("Add to Database", key="add_btn"):
                if name and apartment and entry_time and exit_time and uploaded_file is not None:
                    # Save the image file in the known_images folder with filename as unique_id.jpg
                    save_path = os.path.join("known_images", f"{auto_unique_id}.jpg")
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Insert the new user record into the database
                    conn = sqlite3.connect("smart_entry.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO domestic_help (unique_id, name, apartment_number, owner_name, role, entry_time, exit_time) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                        (auto_unique_id, name, apartment, "", "Worker/Resident", entry_time, exit_time)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"{name} added successfully with ID: {auto_unique_id}!")
                else:
                    st.error("Please fill in all fields and upload an image.")

        elif action == "Delete Worker/Resident":
            st.subheader("Delete Worker/Resident")
            # Admin enters name and apartment number to identify a user for deletion.
            del_name = st.text_input("Enter Name of User to Delete", key="delete_name")
            del_apartment = st.text_input("Enter Apartment Number", key="delete_apartment")
            if st.button("Delete", key="delete_btn"):
                if del_name and del_apartment:
                    conn = sqlite3.connect("smart_entry.db")
                    cursor = conn.cursor()
                    # Query for matching user record
                    cursor.execute("SELECT unique_id FROM domestic_help WHERE name = ? AND apartment_number = ?", (del_name, del_apartment))
                    result = cursor.fetchone()
                    if result:
                        unique_id_to_delete = result[0]
                        # Delete the record from the database
                        cursor.execute("DELETE FROM domestic_help WHERE unique_id = ?", (unique_id_to_delete,))
                        conn.commit()
                        conn.close()
                        st.warning(f"User {del_name} from apartment {del_apartment} deleted!")
                        # Remove the associated image from known_images folder, if it exists.
                        image_path = os.path.join("known_images", f"{unique_id_to_delete}.jpg")
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            st.info("Associated image removed.")
                        else:
                            st.info("No image found for this user.")
                    else:
                        st.error("No matching user found.")
                        conn.close()
                else:
                    st.error("Please enter both Name and Apartment Number.")
        
        elif action == "Show Logs":
            st.subheader("Access Logs")
            conn = sqlite3.connect("smart_entry.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM access_logs")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                st.table(rows)
            else:
                st.info("No logs available.")
