# fabula_charsheet/data/database.py
import sqlite3
import os
import json
import hashlib
import re
from typing import Optional, Dict, List, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "society.db")

class DatabaseManager:
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the SQLite database with users and characters tables."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Characters Table (Linked to Users)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT,
                data JSON NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()

    # --- AUTHENTICATION ---

    def register_user(self, username, password, verify_password) -> tuple[bool, str]:
        """
        Returns (Success, Message).
        Enforces: 8+ chars, Upper, Lower, Number, Symbol.
        """
        if password != verify_password:
            return False, "Passwords do not match."

        # Regex from your PHP reference
        # 8+ chars, 1 Upper, 1 Lower, 1 Num, 1 Symbol (@$!%*?&)
        pass_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        
        if not re.match(pass_regex, password):
            return False, "Password must be 8+ chars, include Upper, Lower, Number, and Symbol (@$!%*?&)."

        # Hash password (PBKDF2 is standard in Python lib)
        salt = os.urandom(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        storage_string = salt.hex() + ":" + pwd_hash.hex()

        try:
            conn = self._get_conn()
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, storage_string))
            conn.commit()
            conn.close()
            return True, "Account created successfully. Please login."
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        except Exception as e:
            return False, f"Database Error: {e}"

    def login_user(self, username, password) -> tuple[Optional[int], str]:
        """
        Returns (User_ID, Error_Message). If User_ID is present, login succeeded.
        """
        conn = self._get_conn()
        user = conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if not user:
            return None, "Invalid credentials."

        try:
            stored_salt_hex, stored_hash_hex = user['password_hash'].split(':')
            salt = bytes.fromhex(stored_salt_hex)
            input_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

            if input_hash == stored_hash_hex:
                return user['id'], ""
            else:
                return None, "Invalid credentials."
        except ValueError:
            return None, "Legacy or Corrupt Password Format."

    # --- CHARACTER DATA ---

    def save_character(self, user_id: int, char_id: str, char_name: str, char_data: dict):
        """Saves or updates a character for a specific user."""
        conn = self._get_conn()
        json_str = json.dumps(char_data)
        
        # Check if exists to determine Insert or Update (Upsert support varies in SQLite versions)
        exists = conn.execute("SELECT 1 FROM characters WHERE id = ? AND user_id = ?", (char_id, user_id)).fetchone()
        
        if exists:
            conn.execute("UPDATE characters SET name = ?, data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                         (char_name, json_str, char_id))
        else:
            conn.execute("INSERT INTO characters (id, user_id, name, data) VALUES (?, ?, ?, ?)", 
                         (char_id, user_id, char_name, json_str))
        
        conn.commit()
        conn.close()

    def get_user_characters(self, user_id: int) -> List[dict]:
        """Returns a list of character dictionaries for the specific user."""
        conn = self._get_conn()
        rows = conn.execute("SELECT data FROM characters WHERE user_id = ?", (user_id,)).fetchall()
        conn.close()
        
        results = []
        for row in rows:
            try:
                results.append(json.loads(row['data']))
            except json.JSONDecodeError:
                continue
        return results

    def delete_character(self, user_id: int, char_id: str):
        conn = self._get_conn()
        conn.execute("DELETE FROM characters WHERE id = ? AND user_id = ?", (char_id, user_id))
        conn.commit()
        conn.close()

# Singleton
DB = DatabaseManager()
