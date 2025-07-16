# pages/view_uploaded_report.py
import streamlit as st
from models.health_report import HealthReport
from utils.helpers import format_date_for_display

def show_page():
    if 'view_report_id' not in st.session_state:
        st.error("No report selected.")
        if st.button("Back to My Reports"):
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return

    report_id = st.session_state.view_report_id
    report = HealthReport.find_by_id(report_id)

    if not report:
        st.error("Report not found.")
        return

    st.title("View Health Report")
    st.write(f"**Report ID:** `{report.report_id}`")
    st.write(f"**File Name:** {report.file_name}")
    st.write(f"**Upload Date:** {format_date_for_display(report.upload_date)}")
    st.write(f"**Report Type:** {report.report_type}")
    st.write(f"**Status:** {report.processing_status}")

    st.subheader("Extracted Data:")
    st.json(report.get_extracted_data())

    if st.button("Back to My Reports"):
        st.session_state.page = "patient_dashboard"
        st.rerun()
