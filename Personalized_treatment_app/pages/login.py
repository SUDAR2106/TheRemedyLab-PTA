# pages/login.py
import streamlit as st
import bcrypt
from database.db_utils import DBManager
from datetime import datetime
from models.user import User  
from utils.security import check_password
from utils.layout import render_header, render_footer

def show_page():
    render_header()
    st.title("Login to Your Account")

    # Use username for login as per the updated table schema
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", use_container_width=True, key="login_btn"):
        if not username or not password:
            st.error("Please enter both username and password.")
            return

        user = User.get_by_username(username)

        if user:
            st.write(f"User found: {user.username}")
            st.write(f"Entered password: {password}")
            st.write(f"Stored hash: {user.password_hash}")
            st.write("Password check result:", user.verify_password(password))

        # Verify password
        if user and user.verify_password(password):
            st.session_state.logged_in = True
            st.session_state.user_id = user.user_id
            st.session_state.user_type = user.user_type
            st.session_state.username = user.username # Store username
            st.session_state.first_name = user.first_name # Store first name
            st.session_state.last_name = user.last_name # Store last name
            st.session_state.email = user.email # Store email

            st.session_state.logged_in_user = user  # ✅ REQUIRED for patient_dashboard.py

            # Update last_login_at
            current_time = datetime.now().isoformat()
            DBManager.execute_query(
                "UPDATE users SET updated_at = ? WHERE user_id = ?",
                (current_time, user.user_id)
            )

            st.success(f"Welcome, {user.first_name} {user.last_name} ({user.user_type.capitalize()})!")

            # Auto-detect role and navigate
            if st.session_state.user_type == 'patient':
                st.session_state.page = "patient_dashboard"
            elif st.session_state.user_type == 'doctor':
                st.session_state.page = "doctor_dashboard"
            elif st.session_state.user_type == 'admin':
                # Future: Redirect to admin dashboard
                st.session_state.page = "admin_dashboard" # Placeholder
                st.warning("Admin dashboard not yet implemented.")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    

    if st.button("Back to Home", key="login_back_home_btn"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("Don't have an account? Sign Up", key="login_to_signup_btn"):
        st.session_state.page = "signup"
        st.rerun()
    render_footer()