# pages/view_report.py
import streamlit as st
from models.health_report import HealthReport
import json
import os

def show_page():
    st.title("Detailed Report View")
    report_id = st.session_state.get("view_report_id", None)
    st.write(f"Viewing Report ID: `{report_id}`")

    report = HealthReport.get_by_report_id(report_id)

    if report:
        st.subheader(f"Report Details: {report.file_name}")
        st.write(f"**Patient ID:** `{report.patient_id}`")
        st.write(f"**Uploaded By User ID:** `{report.uploaded_by}`")
        st.write(f"**Report Type:** {report.report_type}")
        st.write(f"**Upload Date:** {report.upload_date.split('T')[0]}")
        st.write(f"**Processing Status:** {report.processing_status}")
        st.write(f"**Stored File Path:** `{report.file_path}`")

        st.markdown("---")
        st.subheader("Extracted Data (JSON)")
        if report.extracted_data_json:
            try:
                extracted_data = json.loads(report.extracted_data_json)
                st.json(extracted_data)
            except json.JSONDecodeError:
                st.warning("Extracted data is not valid JSON. Displaying raw text.")
                st.text(report.extracted_data_json)
        else:
            st.info("No extracted data available for this report yet.")

        st.markdown("---")
        st.subheader("Original Report File")
        # Provide a download link for the original file if it exists and is accessible
        if os.path.exists(report.file_path):
            with open(report.file_path, "rb") as file:
                btn = st.download_button(
                    label="Download Original File",
                    data=file,
                    file_name=report.file_name,
                    mime="application/octet-stream" # Generic mime type for download
                )
        else:
            st.warning("Original file not found at the recorded path.")

    else:
        st.error(f"Report with ID `{report_id}` not found.")

    st.markdown("---")
    if st.button("Back to My Reports"):
        st.session_state.view_report_id = None # Clear the ID
        st.session_state.page = "patient_dashboard" # Go back to dashboard
        st.rerun()