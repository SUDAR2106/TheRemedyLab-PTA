# pages/doctor_reviewed_recommendations_view.py

import streamlit as st
from models.recommendation import Recommendation
from models.health_report import HealthReport
from models.patient import Patient
from models.user import User # To get patient's user info
from models.doctor import Doctor # To get doctor's user info (for 'Reviewed By')
from utils.layout import render_header, render_footer
from utils.helpers import format_date_for_display # Assuming you have this helper

def show_page():
    render_header()

    # --- Authentication Check ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in or st.session_state.user_type != 'doctor':
        st.warning("Please log in as a doctor to access this page.")
        st.session_state.page = "login"
        st.rerun()
        return

    # --- Retrieve Recommendation ID from Session State ---
    if 'view_reviewed_recommendation_id' not in st.session_state or st.session_state.view_reviewed_recommendation_id is None:
        st.error("No reviewed recommendation selected. Please go back to your reviewed recommendations list.")
        if st.button("Back to Reviewed Recommendations"):
            st.session_state.page = "doctor_reviewed_recommendations_view"
            st.rerun()
        return

    rec_id = st.session_state.view_reviewed_recommendation_id

    # --- Fetch Recommendation and Related Data ---
    recommendation = Recommendation.get_by_recommendation_id(rec_id) # Using get_by_recommendation_id now
    if not recommendation:
        st.error("Reviewed recommendation not found.")
        if st.button("Back to Reviewed Recommendations"):
            st.session_state.page = "doctor_reviewed_recommendations_view"
            st.rerun()
        return

    report = HealthReport.get_by_report_id(recommendation.report_id) # Fetch by report_id
    patient = Patient.get_by_patient_id(recommendation.patient_id) # Fetch by patient_id
    
    patient_user = None
    if patient:
        patient_user = User.get_by_user_id(patient.user_id)

    reviewed_by_doctor_user = None
    if recommendation.doctor_id: # The doctor who reviewed this
        reviewed_by_doctor_profile = Doctor.get_by_doctor_id(recommendation.doctor_id)
        if reviewed_by_doctor_profile:
            reviewed_by_doctor_user = User.get_by_user_id(reviewed_by_doctor_profile.user_id)

    st.title("Reviewed Recommendation Details")
    st.markdown("---")

    # Header: "Reviewed Recommendation for [Patient Name] - [Report Name]"
    patient_name = f"{patient_user.first_name} {patient_user.last_name}" if patient_user else "N/A"
    report_name = report.file_name if report else "N/A"
    st.subheader(f"Reviewed Recommendation for {patient_name} - {report_name}")

    st.markdown("---")

    # Original AI-Generated Content
    st.markdown("#### Original AI-Generated Suggestions:")
    st.info(f"**Treatment Plan:** {recommendation.ai_generated_treatment or 'Not provided by AI'}")
    st.info(f"**Lifestyle Changes:** {recommendation.ai_generated_lifestyle or 'Not provided by AI'}")
    st.info(f"**AI Generated Priority:** {recommendation.ai_generated_priority or 'N/A'}")

    st.markdown("---")

    # Doctor's Finalized Content
    st.markdown("#### Doctor's Finalized Recommendation:")
    if recommendation.status in ['approved_by_doctor', 'modified_and_approved_by_doctor']:
        st.success(f"**Approved Treatment Plan:** {recommendation.approved_treatment or 'N/A'}")
        st.success(f"**Approved Lifestyle Changes:** {recommendation.approved_lifestyle or 'N/A'}")
    elif recommendation.status == 'rejected_by_doctor':
        st.warning("Recommendation was rejected by the doctor.")
    else:
        st.info("Status not finalized or unrecognized.")

    st.text_area("Doctor's Notes:", value=recommendation.doctor_notes or "No notes.", height=100, disabled=True)

    st.markdown("---")

    # Review Metadata
    st.markdown("#### Review Metadata:")
    st.write(f"**Review Status:** `{recommendation.status.replace('_', ' ').title()}`")
    reviewed_by_name = f"{reviewed_by_doctor_user.first_name} {reviewed_by_doctor_user.last_name}" if reviewed_by_doctor_user else "N/A"
    st.write(f"**Reviewed By:** {reviewed_by_name}")
    st.write(f"**Review Date:** {format_date_for_display(recommendation.reviewed_date)}")

    # Reason for Rejection (if applicable)
    if recommendation.status == 'rejected_by_doctor' and recommendation.doctor_notes:
        st.error(f"**Reason for Rejection (from Doctor's Notes):** {recommendation.doctor_notes}")

    st.markdown("---")

    # No editing options
    st.info("This is a read-only view of a finalized recommendation.")

    if st.button("Back to Doctor Dashboard", key="back_from_details_button"):
        if 'view_reviewed_recommendation_id' in st.session_state:
            del st.session_state.view_reviewed_recommendation_id # Clean up session state
        st.session_state.page = "doctor_dashboard"
        st.rerun()

    render_footer()