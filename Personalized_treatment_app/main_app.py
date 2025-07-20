# main_app.py
import streamlit as st
from database.db import init_db
from pages import home, signup, login, patient_dashboard, doctor_dashboard, view_report, view_patient_recommendation, doctor_patient_profile_view, view_patient_reports_for_doctor,doctor_review_interface, doctor_reviewed_recommendations_view
from services.db_initializer import initialize_app  
from config import logger


# --- Global App Setup ---
st.set_page_config(page_title="Personalized Treatment Plans", layout="centered", initial_sidebar_state="collapsed")

# --- Initialize the database and setup ---
logger.info("Starting app: initializing database and application...")

init_db()
initialize_app()

logger.info("Database initialized and app setup complete.")

# --- Session State Management for Navigation and Authentication ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
    logger.debug("Session initialized: page='home'")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    logger.debug("Session initialized: logged_in=False")

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    logger.debug("Session initialized: user_id=None")

if 'user_type' not in st.session_state:
    st.session_state.user_type = None
    logger.debug("Session initialized: user_type=None")

# --- Page Routing Logic ---
if st.session_state.logged_in:
    logger.info(f"User logged in as {st.session_state.user_type}, routing to page: {st.session_state.page}")

    if st.session_state.user_type == 'patient':
       if st.session_state.page == "view_report":
            logger.debug("Routing patient to view_report")
            view_report.show_page()
       elif st.session_state.page == "view_patient_recommendation":
            logger.debug("Routing patient to view_patient_recommendation")
            view_patient_recommendation.show_page()
       else:
            logger.debug("Routing patient to default dashboard")
            patient_dashboard.show_page()

    elif st.session_state.user_type == 'doctor':
        logger.debug("Doctor access routing...")

        if st.session_state.page == "doctor_dashboard":
            logger.debug("Routing doctor to doctor_dashboard")
            doctor_dashboard.show_page()
        elif st.session_state.page == "doctor_patient_profile_view":
            logger.debug("Routing doctor to doctor_patient_profile_view")
            doctor_patient_profile_view.show_page()
        elif st.session_state.page == "view_patient_reports_for_doctor":
            logger.debug("Routing doctor to view_patient_reports_for_doctor")
            view_patient_reports_for_doctor.show_page()
        elif st.session_state.page == "doctor_review_interface":
            logger.debug("Routing doctor to doctor_review_interface")
            doctor_review_interface.show_page()
        elif st.session_state.page == "doctor_reviewed_recommendations_view":
            logger.debug("Routing doctor to doctor_reviewed_recommendations_view")
            doctor_reviewed_recommendations_view.show_page()
        elif st.session_state.page == "view":
            # This page might be reused by doctors to view final recommendations
            logger.debug("Routing doctor to view_patient_recommendation")
            view_patient_recommendation.show_page()
        else: # Default for doctor if an unexpected page state occurs
            logger.warning("Unknown doctor page requested, defaulting to doctor_dashboard")
            doctor_dashboard.show_page()
else:
    logger.info(f"User not logged in. Routing to public page: {st.session_state.page}")
    if st.session_state.page == "home":
        home.show_page()
    elif st.session_state.page == "signup":
        logger.debug("Routing to signup page")
        signup.app(navigate_to=lambda page: st.session_state.update(page=page))
    elif st.session_state.page == "login":
        logger.debug("Routing to login page")
        login.show_page()
    # Default to home if somehow an invalid page state
    else:
        logger.warning(f"Invalid page '{st.session_state.page}' for unauthenticated user, defaulting to home")
        home.show_page()