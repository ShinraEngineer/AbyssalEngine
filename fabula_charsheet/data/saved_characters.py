import os
import json
import logging
from typing import List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SavedCharactersRegistry:
    def __init__(self):
        self.storage_file = None
        self.char_list = []

    def init(self, storage_dir: str):
        """
        Initialize the registry with a storage directory.
        """
        # Ensure directory exists
        if not os.path.exists(storage_dir):
            try:
                os.makedirs(storage_dir, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create storage directory {storage_dir}: {e}")
                return

        self.storage_file = os.path.join(storage_dir, "characters.json")
        self.load_from_disk()

    def load_from_disk(self):
        """
        Load characters from the JSON file into memory.
        """
        if not self.storage_file or not os.path.exists(self.storage_file):
            self.char_list = []
            return

        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                # We assume the file contains a list of character dicts
                data = json.load(f)
                if isinstance(data, list):
                    # In a real app, you might want to re-hydrate these into Character objects here
                    # For now, we load them as they are (likely dicts or Pydantic models when in memory)
                    self.char_list = data
                else:
                    self.char_list = []
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load characters: {e}")
            self.char_list = []

    def save_to_disk(self):
        """
        Serialize the current char_list to JSON and save to disk.
        """
        if not self.storage_file:
            logger.error("Attempted to save without initialization.")
            return

        data_to_save = []
        for char in self.char_list:
            # Handle Pydantic models, objects with to_dict, or plain dicts
            if hasattr(char, "model_dump"):
                data_to_save.append(char.model_dump())
            elif hasattr(char, "to_dict"):
                data_to_save.append(char.to_dict())
            elif isinstance(char, dict):
                data_to_save.append(char)
            else:
                data_to_save.append(char.__dict__)

        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4)
            logger.info(f"Saved {len(data_to_save)} characters to {self.storage_file}")
        except Exception as e:
            logger.error(f"Failed to save characters to disk: {e}")

    def update_character(self, character):
        """
        Update a character in the list if it exists (by ID/Name), or append it.
        Then triggers a save to disk.
        """
        # Determine unique identifier (prefer 'id', fallback to 'name')
        char_id = getattr(character, 'id', None)
        char_name = getattr(character, 'name', None)

        found_index = -1
        
        for i, c in enumerate(self.char_list):
            c_id = c.get('id') if isinstance(c, dict) else getattr(c, 'id', None)
            c_name = c.get('name') if isinstance(c, dict) else getattr(c, 'name', None)

            # Match by ID if available, otherwise Name
            if char_id is not None and c_id == char_id:
                found_index = i
                break
            elif char_id is None and char_name is not None and c_name == char_name:
                found_index = i
                break

        if found_index >= 0:
            self.char_list[found_index] = character
        else:
            self.char_list.append(character)

        self.save_to_disk()

# Global Singleton
SAVED_CHARS = SavedCharactersRegistry()

# Main entry point for initialization
def init(storage_dir):
    SAVED_CHARS.init(storage_dir)
