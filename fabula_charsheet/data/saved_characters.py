# fabula_charsheet/data/saved_characters.py
import logging
import streamlit as st
from data.models import Character
from data.database import DB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SavedCharactersRegistry:
    def __init__(self):
        self.char_list = []

    def init(self, storage_dir: str):
        # We no longer need file paths, but we keep the method signature 
        # to avoid breaking main.py calls.
        self.load_from_disk()

    def load_from_disk(self):
        """
        Load characters for the CURRENTLY LOGGED IN user.
        """
        # Safety check: Is a user logged in?
        if "user_id" not in st.session_state or not st.session_state.user_id:
            self.char_list = []
            return

        try:
            raw_data = DB.get_user_characters(st.session_state.user_id)
            self.char_list = []
            for char_data in raw_data:
                try:
                    # Re-hydrate the dictionary into a Character object
                    if isinstance(char_data, dict):
                        self.char_list.append(Character(**char_data))
                except Exception as e:
                    logger.error(f"Failed to rehydrate character: {e}")
        except Exception as e:
            logger.error(f"Failed to load characters from DB: {e}")
            self.char_list = []

    def save_to_disk(self):
        """
        Saves ALL characters in the current list to the database.
        """
        if "user_id" not in st.session_state or not st.session_state.user_id:
            logger.error("Cannot save: No user logged in.")
            return

        for char in self.char_list:
            self.update_character(char)

    def update_character(self, character):
        """
        Update a single character in the DB.
        """
        if "user_id" not in st.session_state or not st.session_state.user_id:
            return

        # Prepare data
        if hasattr(character, "model_dump"):
            data = character.model_dump(mode='json')
        elif hasattr(character, "to_dict"):
            data = character.to_dict()
        else:
            data = character.__dict__

        char_id = str(getattr(character, 'id'))
        char_name = getattr(character, 'name', 'Unnamed')

        # Save to DB
        DB.save_character(st.session_state.user_id, char_id, char_name, data)

        # Update in-memory list
        self._update_list_in_memory(character)

    def _update_list_in_memory(self, character):
        char_id = getattr(character, 'id', None)
        found = False
        for i, c in enumerate(self.char_list):
            if getattr(c, 'id', None) == char_id:
                self.char_list[i] = character
                found = True
                break
        if not found:
            self.char_list.append(character)

# Global Singleton
SAVED_CHARS = SavedCharactersRegistry()

def init(storage_dir):
    SAVED_CHARS.init(storage_dir)
