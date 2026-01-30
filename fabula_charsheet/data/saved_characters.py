import os
import pickle
import streamlit as st

DATA_FILE = "characters.pkl"

class SavedCharacters:
    def __init__(self):
        self.char_list = self.load_data()

    def load_data(self):
        """Loads the character list from disk."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading saved characters: {e}")
                return []
        return []

    def save_data(self):
        """Saves the current character list to disk."""
        try:
            with open(DATA_FILE, "wb") as f:
                pickle.dump(self.char_list, f)
        except Exception as e:
            print(f"Error saving characters: {e}")

    def add_character(self, character):
        self.char_list.append(character)
        self.save_data()

    def update_character(self, character):
        for i, c in enumerate(self.char_list):
            if c.id == character.id:
                self.char_list[i] = character
                break
        self.save_data()

    def delete_character(self, character_id):
        self.char_list = [c for c in self.char_list if c.id != character_id]
        self.save_data()

# Global singleton instance
SAVED_CHARS = SavedCharacters()
