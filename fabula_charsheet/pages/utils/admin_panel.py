import streamlit as st
import os
import tarfile
import shutil
import time
from io import BytesIO
from datetime import datetime

# Define what to backup
BACKUP_TARGETS = [
    "fabula_charsheet/data",  # Database and saves
    "fabula_charsheet/assets", # Custom content
    "fabula_charsheet/pages",  # Code pages
    "config.py"
]

def render_admin_panel():
    """Renders the Admin Panel in the sidebar if the user is authorized."""
    # Strict Access Control
    if st.session_state.get("username") != "ShinraEngineer":
        return

    with st.expander("🔐 Admin Portal", expanded=False):
        st.caption("System Management")
        
        # --- BACKUP SECTION ---
        st.subheader("Backup")
        if st.button("📦 Create System Snapshot", use_container_width=True):
            # Create in-memory buffer
            buffer = BytesIO()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"society_backup_{timestamp}.tgz"
            
            try:
                with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
                    for target in BACKUP_TARGETS:
                        if os.path.exists(target):
                            tar.add(target)
                
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Download Snapshot",
                    data=buffer,
                    file_name=filename,
                    mime="application/gzip",
                    use_container_width=True
                )
                st.success("Snapshot created!")
            except Exception as e:
                st.error(f"Backup failed: {e}")

        st.divider()

        # --- RESTORE SECTION ---
        st.subheader("Restore")
        uploaded_file = st.file_uploader("Upload Snapshot (.tgz)", type=["tgz", "tar.gz"])
        
        if uploaded_file is not None:
            st.warning("⚠️ This will overwrite current data/database!")
            if st.button("🚨 EXECUTE RESTORE", type="primary", use_container_width=True):
                try:
                    # Save upload to temp
                    with open("temp_restore.tgz", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Extract
                    with tarfile.open("temp_restore.tgz", "r:gz") as tar:
                        tar.extractall(path=".")
                    
                    os.remove("temp_restore.tgz")
                    st.success("System Restored. Rebooting...")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Restore failed: {e}")
