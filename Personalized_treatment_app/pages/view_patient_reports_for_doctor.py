# pages/view_patient_reports_for_doctor.py
# pages/doctor_patient_reports_view.py
import streamlit as st
import pandas as pd
from models.user import User
from models.patient import Patient
from models.health_report import HealthReport
from models.recommendation import Recommendation # Assuming you have a get_by_report_id method
from utils.layout import render_header, render_footer
import os # For file viewing if applicable
from config import UPLOAD_DIR # For file paths

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

    st.title(f"📋 Reports for {patient_user.first_name} {patient_user.last_name}")
    st.markdown("---")

    reports = HealthReport.find_by_patient_id(viewing_patient_id)

    if not reports:
        st.info(f"No reports found for {patient_user.first_name} {patient_user.last_name}.")
    else:
        reports_data = []
        for report in reports:
            recommendation = Recommendation.find_by_report_id(report.report_id) # Fetch associated recommendation

            reports_data.append({
                "Report_ID": report.report_id, # Hidden ID for actions
                "Report Name": report.file_name,
                "Type": report.report_type,
                "Upload Date": report.upload_date.split('T')[0] if report.upload_date else "N/A",
                "Processing Status": report.processing_status,
                "AI Analysis Status": "Available" if recommendation and recommendation.ai_generated_treatment else "N/A", # Assuming AI analysis fills this
                "Doctor Review Status": recommendation.status if recommendation else "N/A" # Status from recommendation
            })

        df_reports = pd.DataFrame(reports_data)
        
        # Display the table of reports
        st.dataframe(
            df_reports.drop(columns=["Report_ID"]),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Actions for Reports")
        
        # Allow selecting a report for actions
        selected_report_id = st.selectbox(
            "Select a report:",
            options=[r["Report_ID"] for r in reports_data],
            format_func=lambda x: next(r['Report Name'] for r in reports_data if r['Report_ID'] == x),
            key="select_report_action"
        )
        
        # Fetch the selected report object
        selected_report = HealthReport.get_by_report_id(selected_report_id)
        selected_recommendation = Recommendation.find_by_report_id(selected_report_id)

        col_view_report, col_view_ai, col_review_edit = st.columns(3)

        with col_view_report:
            if st.button("View Report", key="btn_view_report_doc"):
                if selected_report:
                    # Implement logic to view the actual file (e.g., open PDF in new tab, or display image/text)
                    # For a full viewer, you might need a dedicated component or a simple download link
                    file_path_full = os.path.join(UPLOAD_DIR, selected_report.file_path.split(os.sep)[-1]) # Adjust path based on how it's stored
                    if os.path.exists(file_path_full):
                        st.download_button(
                            label=f"Download {selected_report.file_name}",
                            data=open(file_path_full, "rb"),
                            file_name=selected_report.file_name,
                            mime=f"application/{selected_report.file_type}",
                            key=f"download_report_{selected_report.report_id}"
                        )
                        st.info("File download initiated. Please check your downloads.")
                    else:
                        st.error("Report file not found on server.")
                else:
                    st.warning("Please select a report to view.")

        with col_view_ai:
            if st.button("View AI Analysis", key="btn_view_ai_analysis_doc"):
                if selected_recommendation and selected_recommendation.ai_generated_treatment:
                    st.session_state.viewing_recommendation_id = selected_recommendation.recommendation_id
                    st.session_state.viewing_report_id = selected_report.report_id
                    # This could navigate to a read-only part of the doctor_review_interface
                    # or a dedicated AI analysis view
                    st.info("Navigating to AI Analysis View (part of Review Interface).")
                    st.session_state.page = "doctor_review_interface"
                    st.rerun()
                else:
                    st.info("No AI analysis available for this report yet.")

        with col_review_edit:
            if st.button("Review/Edit Recommendation", key="btn_review_edit_rec_doc"):
                if selected_report:
                    st.session_state.viewing_report_id = selected_report.report_id
                    # If a recommendation already exists, load it. Otherwise, the interface can create one.
                    if selected_recommendation:
                        st.session_state.viewing_recommendation_id = selected_recommendation.recommendation_id
                    else:
                        # Clear existing recommendation ID if none exists for this report
                        if "viewing_recommendation_id" in st.session_state:
                            del st.session_state.viewing_recommendation_id

                    st.session_state.page = "doctor_review_interface" # This page will handle creating/editing
                    st.rerun()
                else:
                    st.warning("Please select a report to review.")


    st.markdown("---")

    if st.button("Back to Doctor Dashboard", key="back_to_doctor_dashboard_reports"):
        del st.session_state.viewing_patient_id # Clean up session state
        st.session_state.page = "doctor_dashboard"
        st.rerun()

    render_footer()
   