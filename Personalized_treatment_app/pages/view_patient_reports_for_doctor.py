# pages/view_patient_reports_for_doctor.py

import streamlit as st
import pandas as pd
from models.user import User
from models.patient import Patient
from models.health_report import HealthReport
from models.recommendation import Recommendation # Assuming you have a get_by_report_id method
from utils.layout import render_header, render_footer
import os # For file viewing if applicable
from config import UPLOAD_DIR # For file paths
import json
import base64
from docx import Document
from io import BytesIO
from PIL import Image

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

    st.subheader(f"📋 Reports for {patient_user.first_name} {patient_user.last_name}")
    st.markdown("---")

    reports = HealthReport.find_by_patient_id(viewing_patient_id)

    if not reports:
        st.info(f"No reports found for {patient_user.first_name} {patient_user.last_name}.")
    else:
        st.write("Here are the reports for this patient:")
        
        # Define columns for the custom table layout
        # Report Name, Type, Upload Date, Processing Status, Doctor Review Status, View Report
        col_names = st.columns([4, 2, 2, 2, 8, 3, 3]) # Adjust widths as needed
        with col_names[0]: st.markdown("**Report Name**")
        with col_names[1]: st.markdown("**Type**")
        with col_names[2]: st.markdown("**Upload Date**")
        with col_names[3]: st.markdown("**Processing Status**")
        with col_names[4]: st.markdown("**Doctor Review Status**")
        with col_names[5]: st.markdown("**View Report**")
        with col_names[6]: st.markdown("**AI Status / Retry**")
        st.markdown("---") # Separator below header

        for report in reports:
            recommendation = Recommendation.find_by_report_id(report.report_id)
            doctor_review_status = recommendation.status if recommendation else "N/A"

            cols = st.columns([2, 2, 2, 2, 2, 2,2]) # Match header widths
            with cols[0]: st.write(report.file_name)
            with cols[1]: st.write(report.report_type)
            with cols[2]: st.write(report.upload_date.split('T')[0] if report.upload_date else "N/A")
            with cols[3]: st.write(report.processing_status)
            with cols[4]: st.write(doctor_review_status)
            with cols[5]:
                if st.button("Open Report", key=f"open_report_{report.report_id}"):
                    st.session_state.report_to_display_content = report.report_id
                    st.rerun() # Rerun to display content in the section below
            with cols[6]:
                if report.processing_status in ["pending_ai_analysis", "extracted"] and doctor_review_status != "pending_doctor_review":
                    if st.button("Retry AI", key=f"retry_ai_{report.report_id}"):
                        from services.document_parser import DocumentParser#Lazy import
                        success = DocumentParser.process_report_pipeline(report.report_id)
                        if success:
                            st.success("✅ AI recommendation successfully regenerated.")
                            st.rerun()
                        else:
                            st.error("❌ AI generation failed.")
                elif report.processing_status == "pending_doctor_review":
                    st.write("✅ Ready")
                elif report.processing_status == "doctor_assigned":
                    st.write("⏳ Waiting for AI")
                else:
                    st.write("—")      
        
        st.markdown("---") # Separator below table

        # Section to display the selected report's content
        if "report_to_display_content" in st.session_state and st.session_state.report_to_display_content:
            selected_report_id_to_display = st.session_state.report_to_display_content
            report_to_display = HealthReport.get_by_report_id(selected_report_id_to_display)

            if report_to_display:
                st.subheader(f"Content of: {report_to_display.file_name}")
                file_path_full = os.path.join(UPLOAD_DIR, report_to_display.file_path.split(os.sep)[-1])

                if os.path.exists(file_path_full):
                    file_extension = report_to_display.file_type.lower()

                    if file_extension == 'json':
                        try:
                            with open(file_path_full, 'r', encoding='utf-8') as f:
                                content = json.load(f)
                            st.json(content)
                        except Exception as e:
                            st.error(f"Error loading JSON file: {e}")
                            # Provide download as fallback
                            with open(file_path_full, "rb") as file:
                                st.download_button(
                                    label=f"Download {report_to_display.file_name} (Error during display)",
                                    data=file,
                                    file_name=report_to_display.file_name,
                                    mime="application/json",
                                    key=f"download_json_error_{report_to_display.report_id}"
                                )
                    elif file_extension == 'csv':
                        try:
                            df = pd.read_csv(file_path_full)
                            st.dataframe(df, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading CSV file: {e}")
                            # Provide download as fallback
                            with open(file_path_full, "rb") as file:
                                st.download_button(
                                    label=f"Download {report_to_display.file_name} (Error during display)",
                                    data=file,
                                    file_name=report_to_display.file_name,
                                    mime="text/csv",
                                    key=f"download_csv_error_{report_to_display.report_id}"
                                )
                    elif file_extension in ['txt', 'log']: # Simple text files
                        try:
                            with open(file_path_full, 'r', encoding='utf-8') as f:
                                content = f.read()
                            st.text_area("File Content", content, height=300)
                        except Exception as e:
                            st.error(f"Error loading text file: {e}")
                            # Provide download as fallback
                            with open(file_path_full, "rb") as file:
                                st.download_button(
                                    label=f"Download {report_to_display.file_name} (Error during display)",
                                    data=file,
                                    file_name=report_to_display.file_name,
                                    mime="text/plain",
                                    key=f"download_txt_error_{report_to_display.report_id}"
                                )
                    elif file_extension == 'pdf':
                        try:
                            with open(file_path_full, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                            st.markdown(pdf_display, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error displaying PDF file: {e}")

                    elif file_extension == 'docx':
                        try:
                            doc = Document(file_path_full)
                            text = "\n".join([para.text for para in doc.paragraphs])
                            st.text_area("DOCX Content", text, height=400)
                        except Exception as e:
                            st.error(f"Error displaying DOCX file: {e}")

                    elif file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                        st.warning(f"Direct in-app viewing for '{file_extension.upper()}' files is not natively supported by Streamlit without specialized components or external libraries. A download option is provided so your system can open it with the appropriate viewer.")
                        with open(file_path_full, "rb") as file:
                            st.download_button(
                                label=f"Download {report_to_display.file_name}",
                                data=file,
                                file_name=report_to_display.file_name,
                                mime=f"application/{file_extension}", # Use specific mime type if known
                                key=f"download_file_{report_to_display.report_id}"
                            )
                    else:
                        st.info(f"File type '{file_extension}' not recognized for in-app display. Offering as download.")
                        with open(file_path_full, "rb") as file:
                            st.download_button(
                                label=f"Download {report_to_display.file_name}",
                                data=file,
                                file_name=report_to_display.file_name,
                                mime="application/octet-stream", # Generic binary
                                key=f"download_unknown_file_{report_to_display.report_id}"
                            )
                else:
                    st.error("Report file not found on server.")
            else:
                st.error("Selected report not found.")
            
            # Button to clear the displayed content
            if st.button("Hide Report Content", key="hide_report_content"):
                st.session_state.report_to_display_content = None
                st.rerun()

    st.markdown("---")

    if st.button("Back to Doctor Dashboard", key="back_to_doctor_dashboard_reports"):
        if "report_to_display_content" in st.session_state:
            del st.session_state.report_to_display_content # Clean up session state
        del st.session_state.viewing_patient_id # Clean up session state
        st.session_state.page = "doctor_dashboard"
        st.rerun()

    render_footer()
   