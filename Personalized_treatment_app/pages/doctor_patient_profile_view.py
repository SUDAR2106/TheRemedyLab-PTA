# pages/doctor_patient_profile_view.py
import streamlit as st
from models.user import User
from models.patient import Patient
from utils.layout import render_header, render_footer

def show_page():
    render_header()

    if "user_id" not in st.session_state or st.session_state.user_type != "doctor":
        st.warning("Please log in as a doctor to access this page.")
        st.session_state.page = "login"
        st.stop()

    # Retrieve the patient_id from session state
    viewing_patient_id = st.session_state.get("viewing_patient_id")

    if not viewing_patient_id:
        st.error("No patient selected. Please go back to the dashboard and select a patient.")
        if st.button("Back to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        st.stop()

    patient = Patient.get_by_patient_id(viewing_patient_id)
    if not patient:
        st.error("Patient not found.")
        if st.button("Back to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        st.stop()

    patient_user = User.get_by_user_id(patient.user_id)
    if not patient_user:
        st.error("Patient user information not found.")
        if st.button("Back to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        st.stop()

    st.title(f"👤 Patient Profile: {patient_user.first_name} {patient_user.last_name}")
    st.markdown("---")

    st.subheader("Basic Information")
    st.write(f"**Username:** {patient_user.username}")
    st.write(f"**Email:** {patient_user.email if patient_user.email else 'N/A'}")
    st.write(f"**Date of Birth:** {patient.date_of_birth if patient.date_of_birth else 'N/A'}")
    st.write(f"**Gender:** {patient.gender if patient.gender else 'N/A'}")
    st.write(f"**Contact Number:** {patient.contact_number if patient.contact_number else 'N/A'}")
    st.write(f"**Address:** {patient.address if patient.address else 'N/A'}")

    st.markdown("---")

    if st.button("Back to Doctor Dashboard", key="back_to_doctor_dashboard_profile"):
        del st.session_state.viewing_patient_id # Clean up session state
        st.session_state.page = "doctor_dashboard"
        st.rerun()

    render_footer()