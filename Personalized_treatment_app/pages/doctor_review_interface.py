# pages/doctor_review_interface.py

import streamlit as st
from models.recommendation import Recommendation


from models.user import User
from models.doctor import Doctor
from utils.layout import render_header, render_footer
from models.doctor import Doctor # Although current_doctor is from session, useful for type hints/future use
import json # For parsing extracted_data_json
from utils.helpers import format_date_for_display
import pandas as pd
import altair as alt
import json

def show_page():
    from models.health_report import HealthReport
    from models.patient import Patient
    render_header()

    
    """
    Displays an interface for doctors to review, approve, modify, or reject AI-generated recommendations.
    """
    # --- Authentication Check ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in or st.session_state.user_type != 'doctor':
        st.warning("Please log in as a doctor to access this page.")
        st.session_state.page = "login"
        st.rerun()
        return
    # --- Check if doctor_id is in session state ---
    current_user = st.session_state.logged_in_user
    current_doctor = Doctor.get_by_user_id(current_user.user_id)

    if not current_doctor:
        st.error("Doctor profile not found. Please contact support.")
        st.session_state.logged_in_user = None
        st.session_state.page = "login"
        st.stop()

    # --- Retrieve Recommendation ID from Session State ---
    # Ensure a recommendation ID is passed from the dashboard
    if 'review_recommendation_id' not in st.session_state:
        st.error("No recommendation selected for review. Please go back to your dashboard.")
        if st.button("Go to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        return

    rec_id = st.session_state.review_recommendation_id
    # report_id = st.session_state.review_report_id # Assuming report_id is also passed for context

    # --- Fetch Recommendation and Related Data ---
    recommendation = Recommendation.get_by_recommendation_id(rec_id) # Assuming get_by_id is implemented or use get_by_report_id if that's how you link
    
    if not recommendation:
        st.error("Recommendation not found.")
        if st.button("Go to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        return

    report = HealthReport.find_by_id(recommendation.report_id)

    patient = Patient.get_by_patient_id(recommendation.patient_id)
    # Ensure report and patient data is available
    if not report or not patient:
        st.error("Related report or patient data not found.")
        if st.button("Go to Doctor Dashboard"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
        return
    # Ensure patient user info is available
    patient_user = User.get_by_user_id(patient.user_id)
    if not patient_user:
        st.error("Patient user info not found.")
        return

    st.subheader("Review AI-Generated Recommendation")
    st.markdown("---")
    # --- Display Basic Info ---
    st.subheader(f"Patient: {patient_user.first_name} {patient_user.last_name}")
    st.write(f"**Report:** {report.file_name} (Uploaded: {format_date_for_display(report.upload_date)})")
    # st.write(f"**Recommendation ID:** `{recommendation.recommendation_id}`")
    st.write(f"**AI Generated Priority:** {recommendation.ai_generated_priority}")

    st.markdown("---")

    #  # Display Extracted Data as a Bar Chart
    # st.subheader("Extracted Health Metrics")

    # # Assuming health_report.extracted_data_json is already loaded as a dict
    # # If it's still a string, uncomment the line below to parse it:
    # # extracted_data = json.loads(health_report.extracted_data_json) if health_report.extracted_data_json else {}

    # # Directly use the get_extracted_data method from HealthReport model
    # # which already handles JSON parsing.
    
    # extracted_data = HealthReport.get_extracted_data()

    # if 'metrics' in extracted_data and extracted_data['metrics']:
    #     chart_data = []
    #     for metric, values in extracted_data['metrics'].items():
    #         if isinstance(values, list) and len(values) >= 2:
    #             raw_value = str(values[0]).strip()
    #             color_status = str(values[1]).strip().lower() # 'green', 'orange', 'red' etc.

    #             # Clean the raw_value to extract only the numeric part
    #             # Remove symbols like '⚠️', '❌', and anything after a space if it's not a number
    #             numeric_str = ''.join(filter(lambda x: x.isdigit() or x == '.', raw_value))

    #             try:
    #                 numeric_value = float(numeric_str)
    #                 chart_data.append({
    #                     "Metric": metric,
    #                     "Value": numeric_value,
    #                     "Color": color_status
    #                 })
    #             except ValueError:
    #                 # Skip values that cannot be converted to numbers for the chart
    #                 continue
        
    #     if chart_data:
    #         df_metrics = pd.DataFrame(chart_data)

    #         # Define a color scale mapping status to actual colors
    #         color_scale = alt.Scale(domain=['green', 'orange', 'red', 'unknown'],
    #                                 range=['green', 'orange', 'red', 'gray']) # 'unknown' for anything else

    #         chart = alt.Chart(df_metrics).mark_bar().encode(
    #             x=alt.X('Metric:N', axis=alt.Axis(title='Metric')),
    #             y=alt.Y('Value:Q', axis=alt.Axis(title='Value')),
    #             color=alt.Color('Color:N', scale=color_scale, legend=None), # Use the 'Color' column directly
    #             tooltip=['Metric', 'Value', 'Color']
    #         ).properties(
    #             title="Extracted Health Metrics and Status"
    #         ).interactive()

    #         st.altair_chart(chart, use_container_width=True)
    #     else:
    #         st.info("No numeric health metrics found in 'metrics' section to display in chart.")
    # else:
    #     st.info("No 'metrics' data available in the extracted report.")

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
                if not current_doctor:
                    st.error("Doctor record not found for this user.")
                    return
                # Call the approve method with modified content
                recommendation.approve(current_doctor.doctor_id, doctor_notes)
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
                    # Get doctor_id from logged-in user_id
                    doctor = Doctor.get_by_user_id(st.session_state.user_id)
                    if not doctor:
                        st.error("Doctor record not found for this user.")
                        return
                    # Call the modify_and_approve method with modified content
                    recommendation.modify_and_approve(doctor.doctor_id, modified_treatment, modified_lifestyle, doctor_notes)
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
                if not current_doctor:
                    st.error("Doctor record not found for this user.")
                    return
                # Call the reject method
                recommendation.reject(current_doctor.doctor_id, doctor_notes)
                st.warning("In-person consultation required for accurate assessment.")
                st.session_state.page = "doctor_dashboard"
                st.rerun()
            except Exception as e:
                st.error(f"Error rejecting recommendation: {e}")

    st.markdown("---")
    if st.button("Back to Doctor Dashboard", key="back_to_dashboard_btn"):
        del st.session_state.review_recommendation_id
        if "review_report_id" in st.session_state:
            del st.session_state.review_report_id
        st.session_state.page = "doctor_dashboard"
        st.rerun()
    render_footer()