# pages/view_report.py
import streamlit as st
from models.health_report import HealthReport
import os
import json
import base64
from docx import Document
import pandas as pd

def show_page():
    st.title("Detailed Report View")
    report_id = st.session_state.get("view_report_id", None)
    st.write(f"Viewing Report ID: `{report_id}`")

    if not report_id:
        st.error("No report selected to view.")
        if st.button("Back to Patient Dashboard"):
            st.session_state.view_report_id = None
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return

    report = HealthReport.get_by_report_id(report_id)

    if not report:
        st.error("Report not found.")
        if st.button("Back to Patient Dashboard"):
            st.session_state.view_report_id = None
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return
        

    st.subheader(f"{report.file_name}")
    file_path_full = report.file_path

    if not os.path.exists(file_path_full):
        st.error("Report file not found on server.")
        if st.button("Back to Patient Dashboard"):
            st.session_state.view_report_id = None
            st.session_state.page = "patient_dashboard"
            st.rerun()
        return

    file_extension = report.file_type.lower()

    # View Logic Based on File Type
    if file_extension == "json":
        try:
            with open(file_path_full, "r", encoding="utf-8") as f:
                content = json.load(f)
            st.json(content)
        except Exception as e:
            st.error(f"Error loading JSON: {e}")

    elif file_extension == "csv":
        try:
            df = pd.read_csv(file_path_full)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading CSV: {e}")

    elif file_extension == "pdf":
        try:
            with open(file_path_full, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying PDF: {e}")

    elif file_extension == "docx":
        try:
            doc = Document(file_path_full)
            text = "\n".join([para.text for para in doc.paragraphs])
            st.text_area("DOCX Content", text, height=400)
        except Exception as e:
            st.error(f"Error displaying DOCX: {e}")

    else:
        st.warning(f"Cannot preview this file type ({file_extension}).")
        with open(file_path_full, "rb") as file:
            st.download_button(
                label="Download Original File",
                data=file,
                file_name=report.file_name,
                mime="application/octet-stream"
            )


    st.markdown("---")
    if st.button("Back to My Reports"):
        st.session_state.view_report_id = None # Clear the ID
        st.session_state.page = "patient_dashboard" # Go back to dashboard
        st.rerun()