import streamlit as st

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Fabula Ultima", 
    page_icon=":material/person_play:",
    layout="wide"
)

from data.localizator import init_localizator, select_local
from data.compendium import init as init_compendium
from data.saved_characters import init as init_saved_characters
from config import ASSETS_DIRECTORY, SAVED_CHARS_DIRECTORY, LOCALS_DIRECTORY
from pages import build_pages
from pages.login import login_page

# --- IMPORT NEW UTILS ---
from pages.utils.admin_panel import render_admin_panel
from pages.utils.dice_roller import render_dice_roller

def main():
    # --- AUTHENTICATION GATE ---
    if 'user_id' not in st.session_state:
        login_page()
        return

    # --- MAIN APP START ---
    init_compendium(ASSETS_DIRECTORY)
    init_saved_characters(SAVED_CHARS_DIRECTORY)
    init_localizator(LOCALS_DIRECTORY)

    # --- SIDEBAR ---
    with st.sidebar:
        # User Info
        st.write(f"Logged in as: **{st.session_state.get('username', 'Agent')}**")
        
        # Logout Button
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        
        # 1. Dice Roller (Visible to all users)
        # Pass the controller if it exists so we can grab attributes
        controller = st.session_state.get("char_controller", None)
        render_dice_roller(controller)
        
        st.divider()

        # 2. Admin Portal (Restricted to ShinraEngineer)
        render_admin_panel()

    select_local()

    pages = build_pages()
    pg = st.navigation([st.Page(**p) for p in pages], position="top")
    pg.run()

if __name__ == "__main__":
    main()
