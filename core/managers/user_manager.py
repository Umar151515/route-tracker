import sqlite3
from typing import Any

from ..config import data_path
from utils.text.processing import validate_name, validate_phone, validate_role, validate_bus_number, ALLOWED_ROLES


class UserManager:
    _instance: "UserManager" = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.create_table()
            self._initialized = True

    def create_table(self):
        with sqlite3.connect(data_path) as connect:
            cursor = connect.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    phone_number TEXT NOT NULL UNIQUE,
                    user_id INTEGER DEFAULT -1,
                    role TEXT NOT NULL,
                    name VARCHAR(123) NOT NULL,
                    bus_number VARCHAR(30) NOT NULL
            );""")

    def get_parameters(
        self,
        phone_number: str | None = None,
        user_id: int | None = None,

        get_user_id: bool = False,
        get_phone_number: bool = False,
        role: bool = False,
        name: bool = False,
        bus_number: bool = False
    ) -> dict[str, Any] | Any:
        self.check_parameters(phone_number, user_id)
        
        fields = [field for field, include in {
            "phone_number": get_phone_number,
            "user_id": get_user_id,
            "role": role,
            "name": name,
            "bus_number": bus_number
        }.items() if include]

        if not fields:
            raise ValueError("At least one field must be requested to retrieve user parameters.")
        
        with sqlite3.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"

            cursor = connect.cursor()
            cursor.execute(f"SELECT {', '.join(fields)} FROM users WHERE {search_field} = ?", (search_key,))
            row = cursor.fetchone()

        if not row:
            raise ValueError(f"User {phone_number} not found.")

        if len(row) > 1:
            return dict(zip(fields, row))
        return row[0]

    def create_user(
        self, 
        phone_number: str,
        role: str,
        name: str,
        bus_number: str,
        user_id: int | None = None
    ):
        self.check_parameters(phone_number, user_id, role, name, bus_number)

        fields_to_update = {
            "phone_number": phone_number,
            "role": role,
            "name": name,
            "bus_number": bus_number
        }
        fields = {key: value for key, value in fields_to_update.items() if value is not None}
        if not fields:
            raise ValueError("At least one field must be provided to create the user.")

        with sqlite3.connect(data_path) as connect:
            cursor = connect.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            if not self.user_exists(phone_number):
                fields_to_insert = fields.copy()
                if user_id:
                    fields_to_insert['user_id'] = user_id
                    
                columns = ', '.join(fields_to_insert.keys())
                placeholders = ', '.join(['?'] * len(fields_to_insert))
                
                cursor.execute(
                    f"INSERT INTO users ({columns}) VALUES ({placeholders})",
                    tuple(fields_to_insert.values())
                )
                connect.commit()

    def set_user(
        self, 
        phone_number: str | None = None,
        user_id: int | None = None,

        new_phone_number: str | None = None,
        new_user_id: int | None = None,
        role: str | None = None,
        name: str | None = None,
        bus_number: str | None = None
    ):
        self.check_parameters(phone_number, user_id, role, name, bus_number)
        self.check_parameters(new_phone_number, new_user_id)

        if new_phone_number:
            new_user_id = -1

        fields_to_update = {
            "phone_number": new_phone_number,
            "user_id": new_user_id,
            "role": role,
            "name": name,
            "bus_number": bus_number
        }
        fields = {key: value for key, value in fields_to_update.items() if value is not None}
        if not fields:
            raise ValueError("At least one field must be provided to update the user.")

        with sqlite3.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"

            cursor = connect.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(f"UPDATE users SET {', '.join(f'{key} = ?' for key in fields.keys())} WHERE {search_field} = ?",
                           (*fields.values(), search_key))
            connect.commit()

    def delete_user(self, phone_number: str | None = None, user_id: int | None = None):
        self.check_parameters(phone_number, user_id)

        with sqlite3.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"

            cursor = connect.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(f"DELETE FROM users WHERE {search_field} = ?", (search_key,))
            connect.commit()

    def user_exists(self, phone_number: str | None = None, user_id: int | None = None) -> bool:
        self.check_parameters(phone_number, user_id)

        with sqlite3.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"
            
            cursor = connect.cursor()
            cursor.execute(f"SELECT 1 FROM users WHERE {search_field} = ?", (search_key,))
            return cursor.fetchone() is not None
    
    def check_parameters(
        self, 
        phone_number: str | None = None,
        user_id: int | None = None,
        role: str | None = None,
        name: str | None = None,
        bus_number: str | None = None
    ):
        if not phone_number is None and not validate_phone(phone_number):
            raise ValueError("Invalid phone number.")
        elif not user_id is None and (not isinstance(user_id, int) or user_id <= 0):
            raise ValueError("Invalid user ID.")
        elif not role is None and not validate_role(role):
            raise ValueError(f"Invalid role, it should be {ALLOWED_ROLES}.")
        elif not name is None and not validate_name(name):
            raise ValueError(f"Invalid name.")
        elif not bus_number is None and not validate_bus_number(bus_number):
            raise ValueError("Invalid bus number.")
        
    def _get_search_key(self, phone_number: str | None = None, user_id: int | None = None) -> str | int:
        search_key = phone_number
        if not phone_number:
            if not user_id:
                raise ValueError("Neither phone_number nor user_id was passed for search.")
            search_key = user_id
        return search_key