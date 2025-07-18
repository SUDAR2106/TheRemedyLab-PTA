# pages/signup.py
import streamlit as st
import bcrypt
from datetime import datetime, date

from database.db_utils import DBManager
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from utils.layout import render_header, render_footer

def app(navigate_to):
    render_header()
    st.title("📝 Sign Up")
    st.markdown("Create your account to get started.")

    # Initialize error flags
    password_error = False
    email_error = False

    # Initialize error flags
    password_error = False
    email_error = False

    user_type = st.radio("I am a:", ("Patient", "Doctor"), key="signup_user_type")

    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", key="signup_first_name")
        with col2:
            last_name = st.text_input("Last Name", key="signup_last_name")

        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email (Optional)", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

        # Common optional fields
        dob = gender = contact = address = specialization = license_id = hospital = None

        if user_type == "Patient":
            st.subheader("Patient Details")
            dob = st.date_input("Date of Birth", value=date(2000, 1, 1),
                                min_value=date(1900, 1, 1),
                                max_value=datetime.now().date(),
                                key="signup_dob_patient")
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], key="signup_gender_patient")
            contact = st.text_input("Contact Number (Optional)", key="signup_contact_patient")
            address = st.text_area("Address (Optional)", key="signup_address_patient")

        elif user_type == "Doctor":
            st.subheader("Doctor Details")
            specialization_options = [
                "", # Keep the empty option for "Please select..."
                "Cardiologist",
                "Dermatologist",
                "Endocrinologist",
                "ENT Specialist",
                "General Physician",
                "Hepatologist",
                "Nephrologist",
                "Neurologist",
                "Ophthalmologist",
                "Pediatrician",
                "Radiologist",
                "Gastroenterologist"
            ] 
            specialization = st.selectbox("Specialization", options=specialization_options, key="signup_specialization")
            license_id = st.text_input("Medical License ID", key="signup_license_id")
            hospital = st.text_input("Hospital/Clinic (Optional)", key="signup_hospital")
            contact = st.text_input("Contact Number (Optional)", key="signup_contact_doctor")

        submitted = st.form_submit_button("Sign Up")

        if submitted:
            # --- Validation ---
            if not username or not password or not confirm_password or not first_name or not last_name:
                st.error("First Name, Last Name, Username, Password, and Confirm Password are required.")
                return

            if password != confirm_password:
                st.error("Passwords do not match.")
                return

            if user_type == "Doctor" and (not specialization or not license_id):
                st.error("For Doctors, Specialization and Medical License ID are required.")
                return

            # Check if user already exists
            if User.get_by_username(username):
                st.error("Username already taken. Please choose a different one.")
                return

            if email and User.get_by_email(email):
                st.error("Email already registered. Please use a different one or login.")
                return
            # --- Doctor-specific Validation ---
            if user_type == "Doctor":
                if not specialization or not license_id:
                    st.error("Doctor's specialization and license ID are required.")
                    return

                license_exists = DBManager.fetch_one("SELECT 1 FROM doctors WHERE medical_license_number = ?", (license_id,))
                if license_exists:
                    st.error("Medical License ID already exists. Please use a different one.")
                    return

            try:
                    # --- Secure password hashing ---
                    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                    # Create user
                    new_user = User.create(
                        username=username,
                        password=password, # plain text password only!
                        user_type=user_type.lower(),
                        first_name=first_name,
                        last_name=last_name,
                        email=email
                    )

                    if not new_user:
                        st.error("Registration failed. Please try again.")
                        return

                    # Create profile based on user type
                    if new_user.user_type == "patient":
                        patient = Patient.create(
                            user_id=new_user.user_id,
                            date_of_birth=dob.isoformat() if dob else None,
                            gender=gender or None,
                            contact_number=contact or None,
                            address=address or None
                        )
                        if patient:
                            st.success("Patient account created successfully! Please log in.")
                            navigate_to("login")
                            st.rerun()
                        else:
                             # Cleanup: delete user if patient creation fails
                            new_user.delete()
                            st.error("Patient profile creation failed. Please try again.")
                            return

                    elif new_user.user_type == "doctor":
                        # license_exists = DBManager.fetch_one("SELECT 1 FROM doctors WHERE medical_license_number = ?", (license_id,))
                        # if license_exists:
                        #     st.error("A doctor with this Medical License ID already exists. Please use a different one or log in.")
                        #     return
                        doctor = Doctor.create(
                            user_id=new_user.user_id,
                            specialization=specialization,
                            medical_license_number=license_id,
                            contact_number=contact or None,
                            hospital_affiliation=hospital or None
                        )
                        if doctor:
                            st.success("Doctor account created successfully! Please log in.")
                            navigate_to("login")
                            st.rerun()
                        # elif error == "duplicate_license":
                        #     st.error("A doctor with this Medical License ID already exists. Please use a different one or log in.")
                        #     return
                        else:
                            # Cleanup: delete user if doctor creation fails
                            new_user.delete()
                            st.error("Doctor profile creation failed. Please try again.")
                            return

            except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.exception(e)

    st.markdown("---")
    st.info("Already have an account?")
    if st.button("Go to Login", key="signup_go_to_login_btn"):
        navigate_to("login")
        st.rerun()
    render_footer()