import streamlit as st
import os
from data.database import DB
from config import ASSETS_DIRECTORY

def login_page():
    # --- CUSTOM CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0f172a; }
        
        div[data-baseweb="input"] > div {
            background-color: #1e293b; color: #e2e8f0; border-color: #334155;
        }
        div[data-testid="stButton"] > button {
            background-color: #991b1b; color: white; border: none; width: 100%; font-weight: bold;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #7f1d1d; border-color: #ef4444;
        }
        
        h1, h2, h3 { color: #f87171; text-align: center; }
        
        .title-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem; margin-top: 1rem;
        }
        .app-title {
            font-size: 2.5rem; font-weight: 800; color: #f87171; line-height: 1.2; text-align: center;
        }
        .app-subtitle {
            font-size: 1.2rem; font-weight: 400; color: #94a3b8; letter-spacing: 0.1em; text-align: center;
        }

        /* FORCE IMAGE CENTERING */
        /* This targets the img tag directly to force block centering */
        div[data-testid="stImage"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        /* Ensure the container is full width to allow auto margins to work */
        div[data-testid="stImage"] {
            width: 100%;
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
            
            if os.path.exists(logo_path):
                # We do NOT use columns here, letting the CSS 'margin: auto' handle the centering
                st.image(logo_path, width=150)
            else:
                st.markdown("<div style='text-align:center; font-size:4rem;'>💎</div>", unsafe_allow_html=True)

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
                    
                    # Login Button
                    if st.form_submit_button("LOGIN", width="stretch"):
                        uid, error = DB.login_user(username, password)
                        if uid:
                            st.session_state.user_id = uid
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error(error)
                
                if st.button("Create New Account", type="secondary", width="stretch"):
                    st.session_state.auth_view = 'register'
                    st.rerun()

            else:
                st.header("📝 FUEL THE ENGINE")
                st.caption("Requirements: 8+ chars, Upper, Lower, Number, Symbol (@$!%*?&)")
                
                with st.form("register_form"):
                    new_user = st.text_input("Username")
                    new_pass = st.text_input("Password", type="password")
                    ver_pass = st.text_input("Verify Password", type="password")
                    
                    if st.form_submit_button("REGISTER AGENT", width="stretch"):
                        success, msg = DB.register_user(new_user, new_pass, ver_pass)
                        if success:
                            st.success(msg)
                            st.session_state.auth_view = 'login'
                        else:
                            st.error(msg)
                
                if st.button("Back to Login", type="secondary", width="stretch"):
                    st.session_state.auth_view = 'login'
                    st.rerun()

