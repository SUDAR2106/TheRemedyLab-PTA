# utils/layout.py
import streamlit as st

import streamlit as st

# def render_header():
#     user_type = st.session_state.get("user_type", "")
#     user_type = user_type.capitalize() if user_type else ""

#     first_name = st.session_state.get("first_name", "")
#     username = st.session_state.get("username", "")

#     # Compose user label
#     if first_name:
#         user_display = f"{user_type} {first_name}"
#     elif username:
#         user_display = username
#     else:
#         user_display = ""

#     # Layout: Left (user), Center (title), Right (logout)
#     col1, col2, col3 = st.columns([1, 3, 1])

#     # with col1:
#     #       st.markdown(
            
#     #         unsafe_allow_html=False
#     #     )
       
#     with col2:
#         st.markdown(
#             "### 🩺 THE RemedyLab - Personalized Treatment Plans",
#             unsafe_allow_html=False
#         )

#     with col3:
#          if st.session_state.get("logged_in"):
#             st.caption(user_display)
#             if st.button("Logout", key="logout_btn"):
       
#                 logout_user()

#     st.markdown("---")
# def render_header():
#     # You can set a minimal background color if you want the very edges of the app to match,
#     # but the image itself will cover most of the header area.
#     st.markdown(
#         """
#         <style>
#         .stApp {
#             background-color: #E0BBE4; /* Light purple from the image */
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

#     # Use st.image to display the uploaded screenshot directly.
#     # You'll need to make sure the image file 'Screenshot 2025-07-28 142606.png'
#     # is accessible by your Streamlit application (e.g., in the same directory).
#     st.image("Screenshot 2025-07-28 142606.png", use_container_width=True)
def render_header():
    # Set the background color to a light purple
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #E0BBE4; /* Light purple */
        }
        /* Make logo image slightly smaller if needed for alignment in columns */
        .stImage > img {
            max-height: 80px; /* Adjust as needed to fit the header row */
            object-fit: contain; /* Ensures the image scales down without cropping */
        }
        /* Style for the logout button */
        .stButton button {
            background-color: #A9A9A9; /* Grey background for logout button */
            color: white; /* White text for better contrast on grey */
            border-radius: 5px;
            padding: 5px 15px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: background-color 0.2s ease; /* Smooth transition for hover */
        }
        .stButton button:hover {
            background-color: #888888; /* Slightly darker grey on hover */
            color: white;
        }
        /* Style for the centered text in col2 */
        .center-text {
            text-align: center;
            line-height: 1.2; /* Adjust line height for better spacing */
        }
        .personalized-text {
            color: white; /* White color for 'Personalized' */
            font-size: 2.5em; /* Large font size */
            font-weight: bold;
        }
        .treatment-plans-text {
            color: white; /* White color for 'Treatment Plans' */
            font-size: 2.5em; /* Large font size */
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create three columns for the layout: Logo (left), Title (center), Logout (right)
    col1, col2, col3 = st.columns([1, 2, 1]) # Adjust ratios as needed

    with col1:
        # The RemedyLab image as logo
        # Ensure 'Screenshot 2025-07-28 145637.png' is in an accessible path
        st.image("Screenshot 2025-07-28 145637.png")

    with col2:
        # Personalized Treatment Plans text
        st.markdown(
            """
            <div class="center-text">
                <span class="personalized-text">Personalized</span><br>
                <span class="treatment-plans-text">Treatment Plans</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        # User display and Logout button (right-aligned visually)
        st.markdown("<div style='display: flex; flex-direction: column; justify-content: center; height: 100%; align-items: flex-end;'>", unsafe_allow_html=True)
        user_type = st.session_state.get("user_type", "")
        user_type = user_type.capitalize() if user_type else ""

        first_name = st.session_state.get("first_name", "")
        username = st.session_state.get("username", "")

        if first_name:
            user_display = f"{user_type} {first_name}"
        elif username:
            user_display = username
        else:
            user_display = ""

        if st.session_state.get("logged_in"):
             # Add the welcome message here
            st.markdown(f"<div class='welcome-message' style='color: black; font-weight: bold; margin-bottom: 5px;'>Welcome, {user_display}! 👋</div>", unsafe_allow_html=True)

            # st.caption(user_display) # Keep user display
            if st.button("Logout", key="logout_btn"):
                # Assuming logout_user() is defined elsewhere
                logout_user()
                st.rerun() # or appropriate logout action
        st.markdown("</div>", unsafe_allow_html=True) # Close the div

    # Add a separator line below the header
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
