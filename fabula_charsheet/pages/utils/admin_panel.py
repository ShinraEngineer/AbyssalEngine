import streamlit as st
import os
import tarfile
import shutil
import time
from io import BytesIO
from datetime import datetime

# Define what folders/files to backup
BACKUP_SOURCES = [
    "fabula_charsheet/data",
    "fabula_charsheet/assets",
    "fabula_charsheet/pages",
    "config.py"
]

def render_admin_panel():
    """Renders the Admin Portal sidebar widget."""
    # Strict Access Control
    if st.session_state.get("username") != "ShinraEngineer":
        return

    with st.expander("🔐 Admin Portal", expanded=False):
        st.caption("System Management")

        # --- BACKUP ---
        st.subheader("Backup")
        if st.button("📦 Create System Snapshot", width="stretch"):
            buffer = BytesIO()
            # New Naming Scheme: abyssalEngine_FileSysDB_Backup_VYYYYMMDD_HHMM.tgz
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"abyssalEngine_FileSysDB_Backup_V{timestamp}.tgz"
            
            try:
                with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
                    for source in BACKUP_SOURCES:
                        if os.path.exists(source):
                            tar.add(source)
                
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Download Snapshot",
                    data=buffer,
                    file_name=filename,
                    mime="application/gzip",
                    width="stretch"
                )
                st.success(f"Snapshot created: {filename}")
            except Exception as e:
                st.error(f"Backup failed: {e}")

        st.divider()

        # --- RESTORE ---
        st.subheader("Restore")
        uploaded_file = st.file_uploader("Upload Snapshot (.tgz)", type=["tgz", "tar.gz"])
        
        if uploaded_file:
            st.warning("⚠️ This will overwrite all data!")
            if st.button("🚨 EXECUTE RESTORE", type="primary", width="stretch"):
                try:
                    with open("restore_temp.tgz", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    with tarfile.open("restore_temp.tgz", "r:gz") as tar:
                        tar.extractall(path=".")
                    
                    os.remove("restore_temp.tgz")
                    st.success("Restored. Rebooting...")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Restore failed: {e}")

