# utils/layout.py
import streamlit as st

import streamlit as st

def render_header():
    user_type = st.session_state.get("user_type", "")
    user_type = user_type.capitalize() if user_type else ""

    first_name = st.session_state.get("first_name", "")
    username = st.session_state.get("username", "")

    # Compose user label
    if first_name:
        user_display = f"{user_type} {first_name}"
    elif username:
        user_display = username
    else:
        user_display = ""

    # Layout: Left (user), Center (title), Right (logout)
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.session_state.get("logged_in"):
            st.caption(user_display)

    with col2:
        st.markdown(
            "### 🩺 THE REMEDY LAB",
            unsafe_allow_html=False
        )

    with col3:
        if st.session_state.get("logged_in"):
            if st.button("Logout", key="logout_btn"):
                logout_user()

    st.markdown("---")

def logout_user():
    st.session_state.clear()
    st.session_state.page = "login"
    st.rerun()

def render_footer():
    st.markdown(
        """
        <hr>
        <div style='text-align: center; font-size: 13px; color: #999; padding-top: 10px;'>
            &copy; 2025 The Remedy Lab | Personalized Treatment Plans
        </div>
        """,
        unsafe_allow_html=True
    )
