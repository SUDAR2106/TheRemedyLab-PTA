# pages/doctor_dashboard.py
import streamlit as st
from models.health_report import HealthReport # For linking reports to recommendations
from models.doctor import Doctor
from models.recommendation import Recommendation
from models.patient import Patient  # For getting patient details
from models.user import User
from models.patient_doctor_mapping import PatientDoctorMapping  # For patient-doctor mapping
import json
import pandas as pd
from utils.layout import render_header, render_footer
def show_page():
    render_header()
    # Ensure user is logged in
    if 'logged_in_user' not in st.session_state or st.session_state.logged_in_user is None:
        st.warning("You need to log in to access the doctor dashboard.")
        st.session_state.page="login"
        st.stop()

    current_user = st.session_state.logged_in_user

    # Ensure the logged-in user is actually a doctor
    if current_user.user_type != 'doctor':
        st.error("Access Denied: This dashboard is for doctors only.")
        st.session_state.logged_in_user = None
        st.session_state.page="login"
        st.stop()

    # Retrieve doctor-specific data
    current_doctor = Doctor.get_by_user_id(current_user.user_id)
    if not current_doctor:
        st.error("Doctor profile not found. Please contact support.")
        st.session_state.logged_in_user = None
        st.session_state.page="login"
        st.stop()

    # st.title(f"👨‍⚕️ Hi, Dr. {current_user.first_name} {current_user.last_name}!")
    # st.subheader("Doctor Dashboard")
    st.markdown("""
    <style>
        .dashboard-title {{
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
       
    </style>

    <div class="dashboard-title">Doctor Dashboard</div>

""", unsafe_allow_html=True)


    st.markdown("---")

    # # --- Doctor Information Section ---
    # st.header("My Profile")
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.write(f"**Username:** {current_user.username}")
    #     st.write(f"**First Name:** {current_user.first_name}")
    #     st.write(f"**Last Name:** {current_user.last_name}")
    #     st.write(f"**Email:** {current_user.email if current_user.email else 'N/A'}")
    # with col2:
    #     st.write(f"**Specialization:** {current_doctor.specialization if current_doctor.specialization else 'N/A'}")
    #     st.write(f"**License ID:** {current_doctor.medical_license_number if current_doctor.medical_license_number else 'N/A'}")
    #     st.write(f"**Hospital:** {current_doctor.hospital_affiliation if current_doctor.hospital_affiliation else 'N/A'}")
    #     st.write(f"**Contact:** {current_doctor.contact_number if current_doctor.contact_number else 'N/A'}")
    
    # Placeholder for 'Edit Profile' button if needed later
    # if st.button("Edit Profile"):
    #     navigate_to("edit_doctor_profile") # You'd create this page

    st.markdown("---")

    # --- Navigation Tabs/Radio Buttons ---
    selected_view = st.radio(
        "Select an option:",
        ("Assigned Patients", "Pending Reviews", "Reviewed Recommendations"),
        key="doctor_dashboard_view_selector"
    )




    if selected_view == "Assigned Patients":
        st.header("My Assigned Patients")
        # Fetch patients assigned to this doctor
        patient_mappings = PatientDoctorMapping.find_patients_for_doctor(current_doctor.doctor_id) 
        
        if patient_mappings:
            st.write("Here are the patients assigned to you:")
            # You'd iterate through mappings, fetch patient details, and display
            patient_data = []
            for mapping in patient_mappings:
                patient = Patient.get_by_patient_id(mapping.patient_id)
                
                # Fetch user details for the patient
                if patient:
                    patient_user = User.get_by_user_id(patient.user_id)

                    if patient_user:
                        health_reports = HealthReport.get_reports_by_patient(patient.patient_id)
                        report_name = health_reports[0].file_name if health_reports else "No reports yet"
                        patient_data.append({
                            "patient_id": patient.patient_id,
                            "patient_name": f"{patient_user.first_name} {patient_user.last_name}",
                            "username": patient_user.username,
                            "assigned_date": mapping.assigned_date.split('T')[0]
                        })
            if patient_data:
                # Custom table header
                col_name, col_username, col_assigned_date, col_profile_btn, col_reports_btn = st.columns([2, 1.5, 1.5, 1.5, 1.5])
                with col_name: st.markdown("**Patient Name**")
                with col_username: st.markdown("**Username**")
                with col_assigned_date: st.markdown("**Assigned Date**")
                with col_profile_btn: st.markdown("**Patient Profile**")
                with col_reports_btn: st.markdown("**Patient Reports**")
                
                st.markdown("---") # Separator below header

                # Display patient data with buttons
                for patient_info in patient_data:
                    col_name, col_username, col_assigned_date, col_profile_btn, col_reports_btn = st.columns([2, 1.5, 1.5, 1.5, 1.5])
                    
                    with col_name:
                        st.write(patient_info["patient_name"])
                    with col_username:
                        st.write(patient_info["username"])
                    with col_assigned_date:
                        st.write(patient_info["assigned_date"])
                    with col_profile_btn:
                        # Ensure unique keys for buttons
                        if st.button("View Profile", key=f"view_profile_{patient_info['patient_id']}"):
                            st.session_state.viewing_patient_id = patient_info["patient_id"]
                            st.session_state.page = "doctor_patient_profile_view"
                            st.rerun()
                    with col_reports_btn:
                        if st.button("View Reports", key=f"view_reports_{patient_info['patient_id']}"):
                            st.session_state.viewing_patient_id = patient_info["patient_id"]
                            st.session_state.page = "view_patient_reports_for_doctor"
                            st.rerun()
                st.markdown("---") # Separator below table

            else:
                st.info("No patients found in your assignments.")
        else:
            st.info("No patients are currently assigned to you.")
        # else:
        #     st.info("No patients are currently assigned to you. (Placeholder: PatientDoctorMapping needs implementation)")
        #     st.write("Placeholder: Your assigned patients will appear here. You can then navigate to view their reports.")
        #     # Example of how to navigate to view a patient's reports
        #     if st.button("View Patient X's Reports"):
        #         st.session_state.current_patient_to_view_id = 'patient_x_id'
        #         st.session_state.page = "view_patient_reports_for_doctor"
        #         st.rerun()

    elif selected_view == "Pending Reviews":
        st.header("AI-Generated Recommendations Pending Your Review")
        
        # Fetch recommendations with 'AI_generated' status that are not yet reviewed by this doctor (if doctor_id can be null or different)
        # For simplicity, let's assume get_pending_for_doctor is a method that gets all pending for *any* doctor
        # and we can filter here, or we extend it to filter by doctor if patient_doctor_mapping is in place.
        pending_recommendations = Recommendation.get_pending_for_doctor(current_doctor.doctor_id) # This method needs to be implemented/refined in Recommendation model

        if pending_recommendations:
            st.write("Here are recommendations requiring your attention:")
            cols = st.columns([0.2, 0.2, 0.2, 0.2, 0.2]) # Adjust column widths as needed
            cols[0].write("**Patient Name**")
            cols[1].write("**Report Name**")
            cols[2].write("**AI Recommendation Date**")
            cols[3].write("**AI Priority**")
            cols[4].write("**Action**")

            for rec in pending_recommendations:
                patient_name = "N/A"
                report_name = "N/A"
                
                # Fetch patient and report details for display
                patient = Patient.get_by_patient_id(rec.patient_id)
                if patient:
                    patient_user = User.get_by_user_id(patient.user_id)
                    if patient_user:
                        patient_name = f"{patient_user.first_name} {patient_user.last_name}"
                
                report = HealthReport.get_by_report_id(rec.report_id)
                if report:
                    report_name = report.file_name

                cols = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
                with cols[0]: st.write(patient_name)
                with cols[1]: st.write(report_name)
                with cols[2]: st.write(rec.created_at.split('T')[0])
                with cols[3]: st.write(rec.ai_generated_priority if rec.ai_generated_priority else "N/A")
                with cols[4]:
                    if st.button("Review", key=f"review_rec_{rec.recommendation_id}"):
                        st.session_state.review_recommendation_id = rec.recommendation_id
                        st.session_state.review_report_id = rec.report_id 
                        st.session_state.page="doctor_review_interface"
                        st.rerun()
        else:
            st.info("No AI-generated recommendations are currently pending your review.")

    elif selected_view == "Reviewed Recommendations":
        st.header("My Reviewed Recommendations")
        
        # Fetch recommendations reviewed by this doctor (approved_by_doctor or modified_by_doctor)
        reviewed_recommendations = Recommendation.get_reviewed_by_doctor(current_doctor.doctor_id) # This method needs to be implemented in Recommendation model

        if reviewed_recommendations:
            st.write("Here's a list of recommendations you have reviewed:")
            cols = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
            cols[0].write("**Patient Name**")
            cols[1].write("**Report Name**")
            cols[2].write("**Review Date**")
            cols[3].write("**Status**")
            cols[4].write("**Action**")

            for rec in reviewed_recommendations:
                patient_name = "N/A"
                report_name = "N/A"
                
                # Fetch patient and report details for display
                patient = Patient.get_by_patient_id(rec.patient_id)
                if patient:
                    patient_user = User.get_by_user_id(patient.user_id)
                    if patient_user:
                        patient_name = f"{patient_user.first_name} {patient_user.last_name}"
                
                report = HealthReport.get_by_report_id(rec.report_id)
                if report:
                    report_name = report.file_name

                cols = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
                with cols[0]: st.write(patient_name)
                with cols[1]: st.write(report_name)
                with cols[2]: st.write(rec.reviewed_date.split('T')[0] if rec.reviewed_date else "N/A")
                with cols[3]: st.write(rec.status)
                with cols[4]:
                    if st.button("View Your Recommedations", key=f"view_reviewed_rec_{rec.recommendation_id}"):
                        st.session_state.view_reviewed_recommendation_id = rec.recommendation_id 
                        st.session_state.page="doctor_reviewed_recommendations_view" # Can reuse this page
                        st.rerun()
        else:
            st.info("You have not reviewed any recommendations yet.")

    # st.markdown("---")
    # if st.button("Logout", type="secondary", key="doctor_dashboard_logout_btn_bottom"):
    #     st.session_state.logged_in_user = None
    #     st.success("You have been logged out.")
    #     st.session_state.page ="login"
    #     st.rerun()
    render_footer()