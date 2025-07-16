# pages/view_patient_recommendation.py

import streamlit as st
from models.recommendation import Recommendation
from models.health_report import HealthReport
from models.doctor import Doctor
from utils.helpers import format_date_for_display

def show_page():
    """
    Displays a patient's approved/modified recommendation details.
    """
    # --- Authentication Check (Patient Role) ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in or st.session_state.user_type != 'patient':
        st.warning("Please log in as a patient to access this page.")
        st.session_state.page = "login"
        st.rerun()
        return

    # --- Retrieve Report ID from Session State ---
    if 'view_recommendation_report_id' not in st.session_state:
        st.error("No recommendation report selected. Please go back to My Reports.")
        if st.button("Back to My Reports"):
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return
    with st.spinner("Loading recommendation details..."):
        report_id = st.session_state.view_recommendation_report_id

    # --- Fetch Recommendation and Related Data ---
    
    recommendation = Recommendation.find_by_report_id(report_id)
    
    if not recommendation:
        st.info("No recommendation found for this report yet, or it has not been approved by a doctor.")
        if st.button("Back to My Reports"):
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return

    # Ensure the recommendation is actually approved/modified and belongs to the current patient
    if recommendation.patient_id != st.session_state.user_id or \
       recommendation.status not in ['approved_by_doctor', 'modified_by_doctor']:
        st.error("Access denied or recommendation not yet approved.")
        if st.button("Back to My Reports"):
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return

    report = HealthReport.find_by_id(recommendation.report_id)
    doctor = Doctor.find_by_id(recommendation.doctor_id) if recommendation.doctor_id else None # Doctor might be NULL if rejected or not assigned

    st.title("Your Personalized Recommendation")
    st.markdown("---")

    # --- Display Basic Info ---
    st.subheader(f"Recommendation for Report: {report.file_name if report else 'N/A'}")
    st.write(f"**Recommendation ID:** `{recommendation.recommendation_id}`")
    st.write(f"**Reviewed by Doctor:** {f'Dr. {doctor.first_name} {doctor.last_name}' if doctor else 'N/A'}")
    st.write(f"**Reviewed Date:** {format_date_for_display(recommendation.reviewed_date) if recommendation.reviewed_date else 'N/A'}")
    st.write(f"**Status:** {recommendation.status.replace('_', ' ').title()}")

    st.markdown("---")

    # --- Display Approved Content ---
    st.subheader("Approved Treatment Plan:")
    st.success(recommendation.approved_treatment or "No specific treatment plan provided.")

    st.subheader("Approved Lifestyle Changes:")
    st.success(recommendation.approved_lifestyle or "No specific lifestyle changes provided.")

    if recommendation.doctor_notes:
        st.subheader("Doctor's Notes:")
        st.info(recommendation.doctor_notes)

    st.markdown("---")
    if st.button("Back to My Reports", key="back_to_reports_btn"):
        st.session_state.page = "patient_dashboard"
        st.rerun()