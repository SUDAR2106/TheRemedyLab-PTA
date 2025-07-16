# pages/doctor_review_interface.py

import streamlit as st
from models.recommendation import Recommendation
from models.health_report import HealthReport
from models.patient import Patient
from models.doctor import Doctor # Although current_doctor is from session, useful for type hints/future use
import json # For parsing extracted_data_json
from utils.helpers import format_date_for_display

def show_page():
    """
    Displays an interface for doctors to review, approve, modify, or reject AI-generated recommendations.
    """
    # --- Authentication Check ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in or st.session_state.user_type != 'doctor':
        st.warning("Please log in as a doctor to access this page.")
        st.session_state.page = "login"
        st.rerun()
        return

    # --- Retrieve Recommendation ID from Session State ---
    # Ensure a recommendation ID is passed from the dashboard
    if 'review_recommendation_id' not in st.session_state:
        st.error("No recommendation selected for review. Please go back to your dashboard.")
        if st.button("Go to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        return

    rec_id = st.session_state.review_recommendation_id
    report_id = st.session_state.review_report_id # Assuming report_id is also passed for context

    # --- Fetch Recommendation and Related Data ---
    recommendation = Recommendation.get_by_id(rec_id) # Assuming get_by_id is implemented or use get_by_report_id if that's how you link
    if not recommendation:
        st.error("Recommendation not found.")
        if st.button("Go to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        return

    report = HealthReport.get_by_id(recommendation.report_id)
    patient = Patient.get_by_id(recommendation.patient_id)
    
    if not report or not patient:
        st.error("Related report or patient data not found.")
        if st.button("Go to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        return

    st.title("Review AI-Generated Recommendation")
    st.markdown("---")

    # --- Display Basic Info ---
    st.subheader(f"Patient: {patient.first_name} {patient.last_name}")
    st.write(f"**Report:** {report.file_name} (Uploaded: {format_date_for_display(report.upload_date)})")
    st.write(f"**Recommendation ID:** `{recommendation.recommendation_id}`")
    st.write(f"**AI Generated Priority:** {recommendation.ai_generated_priority}")

    st.markdown("---")

    # --- Display AI-Generated Suggestions ---
    st.subheader("AI-Generated Suggestions:")
    st.info(f"**Treatment Plan:** {recommendation.ai_generated_treatment or 'N/A'}")
    st.info(f"**Lifestyle Changes:** {recommendation.ai_generated_lifestyle or 'N/A'}")

    st.markdown("---")

    # --- Doctor's Review Form ---
    st.subheader("Your Review and Action:")
    
    # Text areas for doctor to add notes or modify
    doctor_notes = st.text_area("Your Notes (Optional):", value=recommendation.doctor_notes or "", height=100, key="doctor_notes_input")
    
    st.markdown("#### Modify Approved Recommendations (Optional):")
    modified_treatment = st.text_area("Approved Treatment Plan (Modify if needed):", 
                                      value=recommendation.ai_generated_treatment or "", 
                                      height=150, key="modified_treatment_input")
    modified_lifestyle = st.text_area("Approved Lifestyle Changes (Modify if needed):", 
                                      value=recommendation.ai_generated_lifestyle or "", 
                                      height=150, key="modified_lifestyle_input")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Approve As Is", key="approve_button"):
            try:
                # Call the method on the recommendation object
                recommendation.approve(st.session_state.user_id, doctor_notes)
                st.success("Recommendation approved successfully!")
                st.session_state.page = "doctor_dashboard"
                st.rerun()
            except Exception as e:
                st.error(f"Error approving recommendation: {e}")

    with col2:
        # Check if modifications were actually made
        if modified_treatment != (recommendation.ai_generated_treatment or "") or \
           modified_lifestyle != (recommendation.ai_generated_lifestyle or ""):
            if st.button("Modify & Approve", key="modify_approve_button"):
                try:
                    # Call the method with modified content
                    recommendation.modify_and_approve(st.session_state.user_id, modified_treatment, modified_lifestyle, doctor_notes)
                    st.success("Recommendation modified and approved successfully!")
                    st.session_state.page = "doctor_dashboard"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error modifying and approving recommendation: {e}")
        else:
            st.button("Modify & Approve", disabled=True, help="Modify treatment/lifestyle above to enable.", key="modify_approve_disabled")


    with col3:
        if st.button("Reject", key="reject_button"):
            try:
                # Call the reject method
                recommendation.reject(st.session_state.user_id, doctor_notes)
                st.warning("Recommendation rejected.")
                st.session_state.page = "doctor_dashboard"
                st.rerun()
            except Exception as e:
                st.error(f"Error rejecting recommendation: {e}")

    st.markdown("---")
    if st.button("Back to Doctor Dashboard", key="back_to_dashboard_btn"):
        st.session_state.page = "doctor_dashboard"
        st.rerun()