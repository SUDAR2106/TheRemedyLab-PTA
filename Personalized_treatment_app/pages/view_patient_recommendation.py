# pages/view_patient_recommendation.py

import streamlit as st
from models.recommendation import Recommendation
from models.health_report import HealthReport
from models.doctor import Doctor
from utils.helpers import format_date_for_display
from models.user import User
from utils.layout import render_header, render_footer

def show_page():
    render_header()
        
    """
    Displays a patient's approved/modified recommendation details.
    """
    # --- Authentication Check (Patient Role) ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in_user or st.session_state.user_type != 'patient':
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
    
    # Fetch the report ID from session state
    report_id = st.session_state.view_recommendation_report_id
    with st.spinner("Loading recommendation details..."):
       report_id = st.session_state.view_recommendation_report_id
    
    # Fetch the recommendation linked to this report
    recommendation = Recommendation.find_by_report_id(report_id)

    if not recommendation:
        st.info("No recommendation available for this report yet.")
        if st.button("Back to Dashboard"):
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return

    report = HealthReport.get_by_report_id(report_id)
    
    # Fetch doctor's name who reviewed it
    doctor_user = None
    if recommendation.doctor_id:
        doctor_profile = Doctor.get_by_doctor_id(recommendation.doctor_id)
        if doctor_profile:
            doctor_user = User.get_by_user_id(doctor_profile.user_id)

    st.title("Your Personalized Recommendation")
    st.markdown("---")

    # --- Display Basic Info ---
    st.subheader(f"Recommendation for Report: {report.file_name if report else 'N/A'}")
    st.write(f"**Recommendation ID:** `{recommendation.recommendation_id}`")
    
    reviewed_by_doctor_name = f"Dr. {doctor_user.first_name} {doctor_user.last_name}" if doctor_user else "N/A"
    st.write(f"**Reviewed by Doctor:** {reviewed_by_doctor_name}")
    st.write(f"**Reviewed Date:** {format_date_for_display(recommendation.reviewed_date) if recommendation.reviewed_date else 'N/A'}")
    
    # Display status clearly for the patient
    display_status = recommendation.status.replace('_', ' ').title()
    if recommendation.status == 'rejected_by_doctor':
        st.error(f"**Status:** {display_status} (Please consult your doctor for more details)")
    elif recommendation.status in ['approved_by_doctor', 'modified_and_approved_by_doctor']:
         st.success(f"**Status:** {display_status}")
    else:
        st.info(f"**Status:** {display_status}") # For 'AI_generated' or other pending states

    st.markdown("---")

    # --- Display Approved Content ---
    st.subheader("Approved Treatment Plan:")
    if recommendation.approved_treatment:
        st.success(recommendation.approved_treatment)
    else:
        st.info("No specific treatment plan provided by your doctor yet, or the recommendation was rejected.")

    st.subheader("Approved Lifestyle Changes:")
    if recommendation.approved_lifestyle:
        st.success(recommendation.approved_lifestyle)
    else:
        st.info("No specific lifestyle changes provided by your doctor yet, or the recommendation was rejected.")

    if recommendation.doctor_notes:
        st.subheader("Doctor's Notes:")
        st.info(recommendation.doctor_notes)
    
    # Note: AI-generated original content is NOT shown to the patient, only the approved version.
    # If recommendation was rejected, only the status and notes (if any) are shown.

    st.markdown("---")

    if st.button("Back to Dashboard", key="back_to_patient_dashboard_from_rec"):
        if 'view_recommendation_report_id' in st.session_state:
            del st.session_state.view_recommendation_report_id
        st.session_state.page = "patient_dashboard"
        st.rerun()

    render_footer()