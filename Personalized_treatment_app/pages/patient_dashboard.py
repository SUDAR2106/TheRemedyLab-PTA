# pages/patient_dashboard.py (Example section)
import streamlit as st
import pandas as pd
from models.patient import Patient
from models.health_report import HealthReport
# from models.recommendation import Recommendation # Needed to check approval status
from utils.layout import render_header, render_footer
def show_page():
    render_header()

    if 'logged_in_user' not in st.session_state or st.session_state.logged_in_user is None:
        st.warning("You need to log in to access the patient dashboard.")
        st.session_state.page = "login"
        st.stop()

    current_user = st.session_state.logged_in_user

    # Ensure the logged-in user is actually a patient
    if current_user.user_type != 'patient':
        st.error("Access Denied: This dashboard is for patients only.")
        st.session_state.logged_in_user = None
        st.session_state.page = "login"
        st.stop()

    # Retrieve patient-specific data
    current_patient = Patient.get_by_user_id(current_user.user_id)
    if not current_patient:
        st.error("Patient profile not found. Please contact support.")
        st.session_state.logged_in_user = None
        st.session_state.page = "login"
        st.stop()
    
    
    st.markdown("""
    <style>
        .dashboard-title {{
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
       
    </style>

    <div class="dashboard-title">Patient Dashboard</div>

""", unsafe_allow_html=True)


    

    st.markdown("---")

    # # --- Patient Information Section ---
    # # st.header("My Profile")
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.write(f"**Username:** {"Hello " + current_user.username}")
    #     st.write(f"**First Name:** {current_user.first_name}")
    #     st.write(f"**Last Name:** {current_user.last_name}")
    #     # st.write(f"**Email:** {current_user.email if current_user.email else 'N/A'}")
    # with col2:
    #     st.write(f"**Date of Birth:** {current_patient.date_of_birth if current_patient.date_of_birth else 'N/A'}")
    #     st.write(f"**Gender:** {current_patient.gender if current_patient.gender else 'N/A'}")
    #     st.write(f"**Contact:** {current_patient.contact_number if current_patient.contact_number else 'N/A'}")
    #     st.write(f"**Address:** {current_patient.address if current_patient.address else 'N/A'}")
    
    # st.markdown("---")

    # --- Navigation Tabs/Radio Buttons ---
    selected_view = st.radio(
        "Select an option:",
        ("Upload Report", "My Reports"),
        key="patient_dashboard_view_selector"
    )
    if selected_view== "Upload Report":
        # ... (upload report UI as before) ...
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "csv", "json"])
        report_type = st.selectbox(
            "Select Report Type",
            (
                "Blood Test",
                "Cardiology Report",
                "Diabetes Report",
                "Eye Test",
                "General Checkup",
                "Hearing Test",
                "Kidney Function Test",
                "Lipid Profile",
                "Liver Function Test",
                "MRI Scan",
                "Neurology Report",
                "Stool Test",
                "Thyroid Function Test",
                "Urine Test",
                "X-Ray",
                "Other Test" # "others test" has been rephrased for better display
            )
        )
        description = st.text_area("Optional Description")

        if st.button("Upload Report"):
            if not uploaded_file:
                st.error("Please upload a file.")
            else:
            #   st.write("Uploaded file name:", uploaded_file.name)
            #   st.write("Reading file buffer size:", len(uploaded_file.getbuffer()))

              patient = Patient.get_by_user_id(st.session_state.user_id)
              print("🔍 Retrieved patient:", patient)

              if not patient:
                    st.error("Patient not found. Please ensure you are registered.")
              else:
                print("📁 Uploading new report...")
                success = HealthReport.upload_new_report(
                        patient_id=current_patient.patient_id,
                        uploaded_by=st.session_state.user_id,
                        uploaded_file=uploaded_file,
                        report_type=report_type,
                        description=description  # if supported in DB
                    )
                print("✅ Upload success status:", success)
                # st.success("Report uploaded and processed successfully!")
                if success:
                    st.success("Report uploaded and processed successfully!")
                    # st.rerun()
                else:
                        st.error("Failed to save and process report.")
        else:
            st.error("Please upload a file.")

    elif selected_view == "My Reports":
        st.subheader("My Uploaded Health Reports")
        
        # Get the current patient object (useful if you want patient-specific methods later)
        current_patient = Patient.get_by_user_id(st.session_state.user_id) 
        
        if current_patient:
            # CALLING THE INSTANCE METHOD (or static method if preferred)
            reports = current_patient.get_all_reports() # This returns HealthReport objects
            
            if reports:
                st.write("Here's a list of your uploaded health reports:")
                 # Create table headers
                cols = st.columns([0.2, 0.15, 0.2, 0.15, 0.15, 0.15])
                cols[0].write("**Report Name**")
                cols[1].write("**Upload Date**")
                cols[2].write("**Status**")
                cols[3].write("**View Report**")
                # cols[4].write("**View Data**")
                cols[4].write("**View Rec.**")

                for report in reports:
                    # Determine display status
                    display_status = report.processing_status
                    recommendation = report.get_recommendation()
                    if report.processing_status == 'extracted':
                        if recommendation:
                            if recommendation.status == 'AI_generated':
                                display_status = "Ready for Doctor Review"
                            elif recommendation.status in ['approved_by_doctor', 'modified_and_approved_by_doctor']:
                                display_status = "Recommendations Available"
                            else:
                                display_status = recommendation.status
                        else:
                            display_status = "Pending AI Analysis"

                    rec_approved = recommendation and recommendation.status in ['approved_by_doctor', 'modified_and_approved_by_doctor', 'rejected_by_doctor']

                    # Display each row with buttons
                    cols = st.columns([0.2, 0.15, 0.2, 0.15, 0.15, 0.15])
                    with cols[0]: st.write(report.file_name)
                    with cols[1]: st.write(report.upload_date.split('T')[0])
                    with cols[2]: st.write(display_status)

                    with cols[3]:
                        if st.button("View File", key=f"view_file_{report.report_id}"):
                            st.session_state.view_report_id = report.report_id
                            st.session_state.page = "view_report"
                            st.rerun()

         
                    with cols[4]:
                        if st.button("View Rec.", key=f"view_rec_{report.report_id}", disabled=not rec_approved):
                            st.session_state.view_recommendation_report_id = report.report_id
                            st.session_state.page = "view_patient_recommendation"
                            st.rerun()
                           
                    st.write("---")  # Add a separator between reports
            else:
                st.info("No health reports uploaded yet. Upload one using the 'Upload Report' tab.")
        else:
            st.error("Could not retrieve patient data.")

        # # Debug: Show current session state
        # st.write("**CURRENT SESSION STATE:**")
        # print("🔍 Current session state:")
        # for key, value in st.session_state.items():
        #     if not key.startswith('_'):  # Skip internal streamlit keys
        #         st.write(f"{key}: {value}")   


    # st.markdown("---")
    # if st.button("Logout", type="secondary", key="patient_dashboard_logout_btn_bottom"):
    #     st.session_state.logged_in_user = None
    #     st.success("You have been logged out.")
    #     st.session_state.page ="login"
    #     st.rerun()
    render_footer()