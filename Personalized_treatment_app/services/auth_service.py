# utils/auth.py
import streamlit as st

def set_session_state_defaults():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_first_name' not in st.session_state:
        st.session_state.user_first_name = None
    if 'user_last_name' not in st.session_state:
        st.session_state.user_last_name = None
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    # Add any other session states you might need, e.g., for specific data views
    if 'view_report_id' not in st.session_state:
        st.session_state.view_report_id = None
    if 'view_recommendation_report_id' not in st.session_state:
        st.session_state.view_recommendation_report_id = None
    if 'review_report_id' not in st.session_state:
        st.session_state.review_report_id = None
    if 'current_patient_id' not in st.session_state:
        st.session_state.current_patient_id = None