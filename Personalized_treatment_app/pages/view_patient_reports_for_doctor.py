# pages/view_patient_reports_for_doctor.py
import streamlit as st
from models.user import User # Assuming User model might be needed for user context later
from models.patient import Patient
from models.health_report import HealthReport

def app():
    st.title("👨‍⚕️ View Patient Reports for Doctor")
    st.write("This page will allow doctors to view all reports for their assigned patients.")
    st.info("Content for this page is coming soon!")

    # Placeholder for future implementation
    if 'current_patient_to_view_id' not in st.session_state:
        st.session_state.current_patient_to_view_id = None
    if st.session_state.current_patient_to_view_id:
        patient = Patient.get_by_patient_id(st.session_state.current_patient_to_view_id)
        if patient:
            st.subheader(f"Reports for {patient.first_name} {patient.last_name}")
            reports = HealthReport.get_reports_by_patient_id(patient.patient_id)
            if reports:
                for report in reports:
                    st.write(f"**Report ID:** {report.report_id}")
                    st.write(f"**Date:** {report.date}")
                    st.write(f"**Details:** {report.details}")
                    st.markdown("---")
            else:
                st.warning("No reports found for this patient.")
        else:
            st.error("Patient not found.")