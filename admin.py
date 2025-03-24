import streamlit as st
import sqlite3

# Hardcoded admin credentials (can be moved to a secure database later)
ADMIN_CREDENTIALS = {"admin": "password123"}

def authenticate(username, password):
    return ADMIN_CREDENTIALS.get(username) == password

def admin_page():
    st.title("Admin Dashboard")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid credentials!")

    else:
        st.success("Logged in as Admin")
        st.subheader("Admin Controls")

        action = st.radio("Select an action", ["Add Worker/Resident", "Delete Worker/Resident", "Show Logs"])

        if action == "Add Worker/Resident":
            unique_id = st.text_input("Unique ID")
            name = st.text_input("Name")
            apartment = st.text_input("Apartment Number")
            entry_time = st.text_input("Allowed Entry Time")
            exit_time = st.text_input("Allowed Exit Time")

            if st.button("Add to Database"):
                conn = sqlite3.connect("smart_entry.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO domestic_help (unique_id, name, apartment_number, entry_time, exit_time) VALUES (?, ?, ?, ?, ?)", 
                               (unique_id, name, apartment, entry_time, exit_time))
                conn.commit()
                conn.close()
                st.success(f"{name} added successfully!")

        elif action == "Delete Worker/Resident":
            unique_id = st.text_input("Enter Unique ID to Delete")
            if st.button("Delete"):
                conn = sqlite3.connect("smart_entry.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM domestic_help WHERE unique_id = ?", (unique_id,))
                conn.commit()
                conn.close()
                st.warning("User Deleted!")

        elif action == "Show Logs":
            conn = sqlite3.connect("smart_entry.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM domestic_help")
            rows = cursor.fetchall()
            conn.close()
            st.table(rows)
