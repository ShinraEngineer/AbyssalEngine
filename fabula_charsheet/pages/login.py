import streamlit as st
import os
from data.database import DB
from config import ASSETS_DIRECTORY

def login_page():
    # --- CUSTOM RED/DARK THEME CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0f172a; }
        
        /* Input Fields */
        div[data-baseweb="input"] > div {
            background-color: #1e293b; color: #e2e8f0; border-color: #334155;
        }
        
        /* Buttons */
        div[data-testid="stButton"] > button {
            background-color: #991b1b; color: white; border: none; width: 100%; font-weight: bold;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #7f1d1d; border-color: #ef4444;
        }
        
        h1, h2, h3 { color: #f87171; text-align: center; }
        
        /* Centering Class for Title */
        .title-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem;
        }
        .app-title {
            font-size: 2.5rem; font-weight: 800; color: #f87171; line-height: 1.2; text-align: center;
        }
        .app-subtitle {
            font-size: 1.2rem; font-weight: 400; color: #94a3b8; letter-spacing: 0.1em; text-align: center;
        }

        /* FORCE IMAGE CENTERING */
        div[data-testid="stImage"] {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        div[data-testid="stImage"] > img {
            max-width: 150px; /* Ensure size matches requirement */
        }
        </style>
    """, unsafe_allow_html=True)

    if 'auth_view' not in st.session_state:
        st.session_state.auth_view = 'login'

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        container = st.container()
        with container:
            # --- BRANDING HEADER ---
            logo_path = os.path.join(ASSETS_DIRECTORY, "logo.png")
            
            # Logo (Now centered by CSS)
            if os.path.exists(logo_path):
                st.image(logo_path, width=150)
            else:
                st.markdown("<div style='text-align:center; font-size:4rem;'>💎</div>", unsafe_allow_html=True)

            # Title
            st.markdown(
                """
                <div class="title-container">
                    <div class="app-title">ABYSSAL ENGINE</div>
                    <div class="app-subtitle">FABULA ULTIMA CHARACTERMANCER</div>
                </div>
                """, 
                unsafe_allow_html=True
            )

            # --- FORMS ---
            if st.session_state.auth_view == 'login':
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("LOGIN")
                    
                    if submitted:
                        uid, error = DB.login_user(username, password)
                        if uid:
                            st.session_state.user_id = uid
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error(error)
                
                if st.button("Create New Account", type="secondary"):
                    st.session_state.auth_view = 'register'
                    st.rerun()

            else:
                st.header("📝 JOIN THE SOCIETY")
                st.caption("Requirements: 8+ chars, Upper, Lower, Number, Symbol (@$!%*?&)")
                
                with st.form("register_form"):
                    new_user = st.text_input("Username")
                    new_pass = st.text_input("Password", type="password")
                    ver_pass = st.text_input("Verify Password", type="password")
                    submitted = st.form_submit_button("REGISTER AGENT")
                    
                    if submitted:
                        success, msg = DB.register_user(new_user, new_pass, ver_pass)
                        if success:
                            st.success(msg)
                            st.session_state.auth_view = 'login'
                        else:
                            st.error(msg)
                
                if st.button("Back to Login", type="secondary"):
                    st.session_state.auth_view = 'login'
                    st.rerun()
