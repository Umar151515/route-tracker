import aiosqlite
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
    
    @classmethod
    async def create(cls):
        if not cls._initialized:
            cls._instance = cls()
            await cls._instance.create_table()
            cls._initialized = True
        
        return cls._instance

    async def create_table(self):
        async with aiosqlite.connect(data_path) as connect:
            await connect.execute("PRAGMA foreign_keys = ON;")

            await connect.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    phone_number TEXT NOT NULL UNIQUE,
                    user_id INTEGER UNIQUE,
                    role TEXT NOT NULL,
                    name VARCHAR(123) NOT NULL,
                    bus_number VARCHAR(30)
            );""")

            await connect.commit()

    async def get_parameters(
        self,
        phone_number: str | None = None,
        user_id: int | None = None,

        get_user_id: bool = False,
        get_phone_number: bool = False,
        get_role: bool = False,
        get_name: bool = False,
        get_bus_number: bool = False
    ) -> list[Any] | Any:
        self.check_parameters(phone_number, user_id)
        
        fields = [field for field, include in {
            "phone_number": get_phone_number,
            "user_id": get_user_id,
            "role": get_role,
            "name": get_name,
            "bus_number": get_bus_number
        }.items() if include]

        if not fields:
            raise ValueError("At least one field must be requested to retrieve user parameters.")
        
        async with aiosqlite.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"

            async with connect.execute(f"SELECT {', '.join(fields)} FROM users WHERE {search_field} = ?", (search_key,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            return None

        if len(row) > 1:
            return list(row)
        return row[0]
    
    async def get_users(
        self,
        roles: list[str] | None = None,
        bus_numbers: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Получает список пользователей с возможностью фильтрации по ролям и номерам автобусов.
        
        Args:
            roles: Список ролей для фильтрации
            bus_numbers: Список номеров автобусов для фильтрации
            limit: Ограничение количества записей
            offset: Смещение для пагинации
        
        Returns:
            Список словарей с данными пользователей
        """
        # Валидация параметров фильтрации (оставляем, тут все четко)
        if roles:
            for role in roles:
                if not validate_role(role):
                    raise ValueError(f"Invalid role: {role}")
        
        if bus_numbers:
            for bus_number in bus_numbers:
                if not validate_bus_number(bus_number):
                    raise ValueError(f"Invalid bus number: {bus_number}")
        
        if limit is not None and (not isinstance(limit, int) or limit < 0):
            raise ValueError("Limit must be non-negative integer")
        
        if offset is not None and (not isinstance(offset, int) or offset < 0):
            raise ValueError("Offset must be non-negative integer")

        # Построение запроса с параметризацией
        query_parts = ["SELECT phone_number, user_id, role, name, bus_number FROM users"]
        params = []
        
        where_conditions = []
        if roles:
            # placeholders: ', '.join(["?"] * len(roles))
            where_conditions.append(f"role IN ({', '.join(['?'] * len(roles))})")
            params.extend(roles)
        
        if bus_numbers:
            # placeholders: ', '.join(["?"] * len(bus_numbers))
            where_conditions.append(f"bus_number IN ({', '.join(['?'] * len(bus_numbers))})")
            params.extend(bus_numbers)
        
        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))
        
        # Добавление пагинации
        if limit is not None:
            query_parts.append("LIMIT ?")
            params.append(limit)
            
            if offset is not None:
                query_parts.append("OFFSET ?")
                params.append(offset)

        # --- СУТЬ ИЗМЕНЕНИЙ ЗДЕСЬ ---
        # 1. Используем row_factory
        # 2. Убираем ручное создание словарей
        async with aiosqlite.connect(data_path) as connect:
            # Магия, которая заставляет aiosqlite возвращать результаты как объекты-словари
            connect.row_factory = aiosqlite.Row 
            
            full_query = " ".join(query_parts)
            cursor = await connect.execute(full_query, params)
            
            # fetchall() теперь возвращает список aiosqlite.Row объектов
            rows = await cursor.fetchall()
            
            # Преобразуем aiosqlite.Row в чистые Python-словари
            return [dict(row) for row in rows] 
        
    async def get_users_stats(self) -> dict[str, Any]:
        """
        Получает статистику по пользователям.
        
        Returns:
            Словарь со статистикой
        """
        async with aiosqlite.connect(data_path) as connect:
            async with connect.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]

            role_stats = {}
            async with connect.execute("SELECT role, COUNT(*) FROM users GROUP BY role") as cursor:
                for role, count in await cursor.fetchall():
                    role_stats[role] = count

            return {
                "total_users": total_users,
                "roles": role_stats
            }

    async def create_user(
        self, 
        phone_number: str,
        role: str,
        name: str,
        bus_number: str = None,
        user_id: int | None = None
    ):
        self.check_parameters(phone_number, user_id, role, name)
        if role == "driver":
            self.check_parameters(bus_number=bus_number)

        fields_to_update = {
            "phone_number": phone_number,
            "role": role,
            "name": name,
            "bus_number": bus_number
        }
        fields = {key: value for key, value in fields_to_update.items() if value is not None}
        if not fields:
            raise ValueError("At least one field must be provided to create the user.")

        async with aiosqlite.connect(data_path) as connect:
            await connect.execute("PRAGMA foreign_keys = ON;")
            
            if not await self.user_exists(phone_number):
                fields_to_insert = fields.copy()
                if user_id:
                    fields_to_insert['user_id'] = user_id
                    
                columns = ', '.join(fields_to_insert.keys())
                placeholders = ', '.join(['?'] * len(fields_to_insert))
                
                await connect.execute(
                    f"INSERT INTO users ({columns}) VALUES ({placeholders})",
                    tuple(fields_to_insert.values())
                )
                await connect.commit()

    async def set_user(
        self, 
        phone_number: str | None = None,
        user_id: int | None = None,

        new_phone_number: str | None = None,
        new_user_id: int | None = None,
        new_role: str | None = None,
        new_name: str | None = None,
        new_bus_number: str | None = None
    ):
        self.check_parameters(phone_number, user_id, new_role, new_name, new_bus_number)
        self.check_parameters(new_phone_number, new_user_id)

        if new_phone_number:
            new_user_id = None

        fields_to_update = {
            "phone_number": new_phone_number,
            "user_id": new_user_id,
            "role": new_role,
            "name": new_name,
            "bus_number": new_bus_number
        }
        fields = {key: value for key, value in fields_to_update.items() if value is not None}
        if not fields:
            raise ValueError("At least one field must be provided to update the user.")

        async with aiosqlite.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"

            await connect.execute("PRAGMA foreign_keys = ON;")
            await connect.execute(
                f"UPDATE users SET {', '.join(f'{key} = ?' for key in fields.keys())} WHERE {search_field} = ?",
                (*fields.values(), search_key)
            )
            await connect.commit()

    async def delete_user(self, phone_number: str | None = None, user_id: int | None = None):
        self.check_parameters(phone_number, user_id)

        async with aiosqlite.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"

            await connect.execute("PRAGMA foreign_keys = ON;")
            await connect.execute(f"DELETE FROM users WHERE {search_field} = ?", (search_key,))
            await connect.commit()

    async def user_exists(self, phone_number: str | None = None, user_id: int | None = None) -> bool:
        self.check_parameters(phone_number, user_id)

        async with aiosqlite.connect(data_path) as connect:
            search_key = self._get_search_key(phone_number, user_id)
            search_field = "phone_number" if phone_number else "user_id"
            
            async with connect.execute(f"SELECT 1 FROM users WHERE {search_field} = ?", (search_key,)) as cursor:
                return await cursor.fetchone() is not None
    
    def check_parameters(
        self, 
        phone_number: str | None = None,
        user_id: int | None = None,
        role: str | None = None,
        name: str | None = None,
        bus_number: str | None = None
    ):
        if phone_number is not None and not validate_phone(phone_number):
            raise ValueError("Invalid phone number.")
        elif user_id is not None and (not isinstance(user_id, int) or user_id <= 0):
            raise ValueError("Invalid user ID.")
        elif role is not None and not validate_role(role):
            raise ValueError(f"Invalid role, it should be {ALLOWED_ROLES}.")
        elif name is not None and not validate_name(name):
            raise ValueError("Invalid name.")
        elif bus_number is not None and not validate_bus_number(bus_number):
            raise ValueError("Invalid bus number.")
        
    def _get_search_key(self, phone_number: str | None = None, user_id: int | None = None) -> str | int:
        search_key = phone_number
        if not phone_number:
            if not user_id:
                raise ValueError("Neither phone_number nor user_id was passed for search.")
            search_key = user_id
        return search_key

