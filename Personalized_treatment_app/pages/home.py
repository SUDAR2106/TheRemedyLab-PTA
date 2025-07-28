# pages/home.py - Updated Version with Layout Fixes
import streamlit as st
from utils.layout import render_header, render_footer

def show_page():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    # Apply Updated CSS
    st.markdown("""
<style>
    .stApp {
            background-color: #E0BBE4; /* Light purple */
        }
    html, body, .main-container {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        background-color: var(--background-color);
        overflow-x: hidden;
    }

    .main-container {
        max-width: 100%;
        padding: 0 10px;
    }

    .hero-section {
        background-color: var(--secondary-background-color);
        border: 1px solid #ddd;
        padding: 40px 20px;
        text-align: center;
        border-radius: 20px;
        margin: 30px auto;
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        max-width: 900px;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--text-color);
        margin-bottom: 15px;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-color);
        opacity: 0.8;
    }

    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem !important;
        }
        .hero-subtitle {
            font-size: 0.95rem !important;
        }
    }

    .stButton button {
        border-radius: 30px;
        padding: 10px 20px;
        font-size: 1rem;
        background-color: var(--primary-color);
        color: Black;
    }

    .stButton button:hover {
        filter: brightness(0.9);
    }
</style>
""", unsafe_allow_html=True)


   
    # Hero Section
    # st.markdown("""
    # <div class="hero-section">
    #     <h1 class="hero-title">🏥 Personalized Treatment Plans</h1>
    #     <p class="hero-subtitle">Advanced AI-powered healthcare tailored to your unique needs</p>
    # </div>
    # """, unsafe_allow_html=True)
    st.image("Screenshot 2025-07-28 142606.png", use_container_width=True)
    # Simplified Button Layout
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
