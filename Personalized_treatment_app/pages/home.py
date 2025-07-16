# pages/home.py
import streamlit as st
from utils.layout import render_header, render_footer

def show_page():
    render_header()
    st.title("Welcome to Personalized Treatment Plans")
    st.write("Your health, tailored.")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun() # Use st.rerun() for immediate page state changes
    with col2:
        if st.button("Sign Up", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
    render_footer()