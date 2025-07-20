# pages/home.py - Enhanced Version
import streamlit as st
from utils.layout import render_header, render_footer

def show_page():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    # Apply updated CSS
    st.markdown("""
    <style>
        html, body, .main-container {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow-x: hidden;
        }

        .hero-section {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 80px 20px;
            text-align: center;
            border-radius: 20px;
            margin: 40px auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 900px;
        }

        .hero-title {
            font-size: 3rem;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
        }

        .hero-subtitle {
            font-size: 1.3rem;
            color: rgba(255,255,255,0.9);
        }

        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.2rem !important;
            }
            .hero-subtitle {
                font-size: 1rem !important;
            }
        }

        .stButton button {
            border-radius: 30px;
            padding: 10px 20px;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    render_header()

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🏥 Personalized Treatment Plans</h1>
        <p class="hero-subtitle">Advanced AI-powered healthcare tailored to your needs</p>
    </div>
    """, unsafe_allow_html=True)

    # Login/Signup Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        with col_btn2:
            if st.button("✨ Sign Up", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    render_footer()