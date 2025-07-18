# main_app.py
import streamlit as st
from database.db import init_db
from pages import home, signup, login, patient_dashboard, doctor_dashboard, view_report, view_patient_recommendation, doctor_patient_profile_view, view_patient_reports_for_doctor,doctor_review_interface
from services.db_initializer import initialize_app  
# --- Global App Setup ---
st.set_page_config(page_title="Personalized Treatment Plans", layout="centered", initial_sidebar_state="collapsed")

# Initialize the database connection and create tables once at the very start of the app
# This will also create the 'data' directory and 'healthcare_app.db' if they don't exist.
init_db()
initialize_app()
# --- Session State Management for Navigation and Authentication ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# --- Page Routing Logic ---
if st.session_state.logged_in:
    if st.session_state.user_type == 'patient':
       if st.session_state.page == "view_report":
            view_report.show_page()
       else:
            patient_dashboard.show_page()

    elif st.session_state.user_type == 'doctor':
        if st.session_state.page == "doctor_dashboard":
            doctor_dashboard.show_page()
        elif st.session_state.page == "doctor_patient_profile_view":
            doctor_patient_profile_view.show_page()
        elif st.session_state.page == "view_patient_reports_for_doctor":
            view_patient_reports_for_doctor.show_page()
        elif st.session_state.page == "doctor_review_interface":
            doctor_review_interface.show_page()
        elif st.session_state.page == "view_patient_recommendation":
            # This page might be reused by doctors to view final recommendations
            view_patient_recommendation.show_page()
        else: # Default for doctor if an unexpected page state occurs
            doctor_dashboard.show_page()
else:
    if st.session_state.page == "home":
        home.show_page()
    elif st.session_state.page == "signup":
        signup.app(navigate_to=lambda page: st.session_state.update(page=page))
    elif st.session_state.page == "login":
        login.show_page()
    # Default to home if somehow an invalid page state
    else:
        home.show_page()