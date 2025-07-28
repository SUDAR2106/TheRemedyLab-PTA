# pages/login.py - Enhanced Version
import streamlit as st
import bcrypt
from database.db_utils import DBManager
from datetime import datetime
from models.user import User  
from utils.security import check_password
from utils.layout import render_header, render_footer

def show_page():
    # Custom CSS for modern login form
    st.markdown("""
    <style>
        /* Login container styling */
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin: 20px auto;
            max-width: 500px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .login-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .login-subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        
        /* Form styling */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            padding: 12px 16px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 0;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6);
        }
        
        /* Secondary button styling */
        .secondary-btn button {
            background: white !important;
            color: #667eea !important;
            border: 2px solid #667eea !important;
        }
        
        .secondary-btn button:hover {
            background: #667eea !important;
            color: white !important;
        }
        
        /* Features list */
        .feature-list {
            background: #f8fafc;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .feature-icon {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 14px;
        }
        
        .feature-text {
            color: #555;
        }
        
        /* Security notice */
        .security-notice {
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #4facfe;
            margin: 20px 0;
        }
        
        /* Divider styling */
        .divider {
            text-align: center;
            margin: 30px 0;
            position: relative;
        }
        
        .divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #e2e8f0;
        }
        
        .divider span {
            background: white;
            padding: 0 20px;
            color: #666;
            font-weight: 500;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .login-container {
                padding: 30px 20px;
                margin: 10px;
            }
            
            .login-title {
                font-size: 2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    render_header()
    
    # Main layout
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
              
        # Login form
        with st.container():
            st.markdown("##### 👤 Account Credentials")
            
            # Username input with icon
            username = st.text_input(
                "Username", 
                key="login_username",
                placeholder="Enter your username"
            )
            
            # Password input with icon
            password = st.text_input(
                "Password", 
                type="password", 
                key="login_password",
                placeholder="Enter your password"
            )
            
            # # Remember me and forgot password
            # col_remember, col_forgot = st.columns([1, 1])
            # with col_remember:
            #     remember_me = st.checkbox("Remember me")
            # with col_forgot:
            #     if st.button("Forgot Password?", key="forgot_password"):
            #         st.info("🔐 Password reset functionality will be implemented soon. Please contact support for now.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Login button
            if st.button("🚀 Sign In", use_container_width=True, key="login_btn"):
                if not username or not password:
                    st.error("⚠️ Please enter both username and password.")
                    return

                with st.spinner("🔍 Authenticating..."):
                    user = User.get_by_username(username)

                    # # Debug information (remove in production)
                    # if user:
                    #     st.write(f"User found: {user.username}")
                    #     st.write(f"Entered password: {password}")
                    #     st.write(f"Stored hash: {user.password_hash}")
                    #     st.write("Password check result:", user.verify_password(password))

                    # Verify password
                    if user and user.verify_password(password):
                        # Set session state
                        st.session_state.logged_in = True
                        st.session_state.user_id = user.user_id
                        st.session_state.user_type = user.user_type
                        st.session_state.username = user.username
                        st.session_state.first_name = user.first_name
                        st.session_state.last_name = user.last_name
                        st.session_state.email = user.email
                        st.session_state.logged_in_user = user

                        # Update last_login_at
                        current_time = datetime.now().isoformat()
                        DBManager.execute_query(
                            "UPDATE users SET updated_at = ? WHERE user_id = ?",
                            (current_time, user.user_id)
                        )

                        st.success(f"✅ Welcome back, {user.first_name} {user.last_name}!")
                        st.balloons()

                        # Auto-detect role and navigate
                        if st.session_state.user_type == 'patient':
                            st.session_state.page = "patient_dashboard"
                        elif st.session_state.user_type == 'doctor':
                            st.session_state.page = "doctor_dashboard"
                        elif st.session_state.user_type == 'admin':
                            st.session_state.page = "admin_dashboard"
                            st.warning("🚧 Admin dashboard not yet implemented.")
                        
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")
            
            # Divider
            st.markdown('<div class="divider"><span>or</span></div>', unsafe_allow_html=True)
            
            # Secondary actions
            col_home, col_signup = st.columns(2)
            
            with col_home:
                if st.button("🏠 Back to Home", use_container_width=True, key="login_back_home_btn", help="Return to homepage"):
                    st.session_state.page = "home"
                    st.rerun()
            
            with col_signup:
                if st.button("✨ Create Account", use_container_width=True, key="login_to_signup_btn", help="Don't have an account? Sign up now"):
                    st.session_state.page = "signup"
                    st.rerun()
    
    render_footer()