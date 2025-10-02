import aiosqlite
from typing import Any

from ..config import data_path
from utils.text.processing import validate_bus_number, validate_stop_name


class BusStopsManager:
    _instance: "BusStopsManager" = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def __init__(self):
        if not self._initialized:
            await self.create_table()
            self._initialized = True

    async def create_table(self):
        async with aiosqlite.connect(data_path) as connect:
            await connect.execute("PRAGMA foreign_keys = ON;")

            await connect.execute("""
                CREATE TABLE IF NOT EXISTS buses (
                    bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bus_number VARCHAR(30) NOT NULL UNIQUE
            );""")

            await connect.execute("""
                CREATE TABLE IF NOT EXISTS stops (
                    stop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bus_id INTEGER NOT NULL,
                    stop_name TEXT NOT NULL,
                    stop_order INTEGER NOT NULL,
                    FOREIGN KEY (bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE ON UPDATE CASCADE
            );""")

            await connect.commit()

    async def create_bus(self, bus_number: str):
        self.check_parameters(bus_number=bus_number)
        async with aiosqlite.connect(data_path) as connect:
            await connect.execute("PRAGMA foreign_keys = ON;")
            await connect.execute("INSERT INTO buses (bus_number) VALUES (?)", (bus_number,))
            await connect.commit()

    async def delete_bus(self, bus_number: str | None = None, bus_id: int | None = None):
        search_key = self._get_search_key(bus_number, bus_id)
        search_field = "bus_number" if bus_number else "bus_id"

        async with aiosqlite.connect(data_path) as connect:
            await connect.execute(f"DELETE FROM buses WHERE {search_field} = ?", (search_key,))
            await connect.commit()

    async def bus_exists(self, bus_number: str | None = None, bus_id: int | None = None) -> bool:
        search_key = self._get_search_key(bus_number, bus_id)
        search_field = "bus_number" if bus_number else "bus_id"
            
        async with aiosqlite.connect(data_path) as connect:
            async with connect.execute(f"SELECT 1 FROM buses WHERE {search_field} = ?", (search_key,)) as cursor:
                return await cursor.fetchone() is not None

    async def get_bus_id(self, bus_number: str) -> int:
        self.check_parameters(bus_number=bus_number)
        return await self._get_bus_field("bus_id", "bus_number", bus_number)

    async def get_bus_number(self, bus_id: int) -> str:
        self.check_parameters(bus_id=bus_id)
        return await self._get_bus_field("bus_number", "bus_id", bus_id)

    async def create_stop(
        self,
        bus_number: str | None = None,
        bus_id: int | None = None,
        stop_name: str | None = None,
        stop_order: int | None = None
    ):
        self.check_parameters(bus_number=bus_number, bus_id=bus_id, stop_name=stop_name, stop_order=stop_order)

        if not stop_name:
            raise ValueError("Stop name must be provided.")

        if bus_id is None:
            bus_id = await self.get_bus_id(bus_number)

        async with aiosqlite.connect(data_path) as connect:
            async with connect.execute("SELECT COUNT(*) FROM stops WHERE bus_id = ?", (bus_id,)) as cursor:
                total_stops = (await cursor.fetchone())[0]

            if stop_order is None or stop_order > total_stops:
                stop_order = total_stops + 1

            await connect.execute("""
                UPDATE stops SET stop_order = stop_order + 1
                WHERE bus_id = ? AND stop_order >= ?
            """, (bus_id, stop_order))

            await connect.execute("""
                INSERT INTO stops (bus_id, stop_name, stop_order)
                VALUES (?, ?, ?)
            """, (bus_id, stop_name, stop_order))

            await connect.commit()

    async def delete_stop(
        self,
        stop_id: int | None = None,
        bus_number: str | None = None,
        bus_id: int | None = None,
        stop_order: int | None = None
    ):
        self.check_parameters(bus_number=bus_number, bus_id=bus_id, stop_id=stop_id, stop_order=stop_order)

        if not stop_id and not stop_order:
            raise ValueError("Either stop_id or stop_order must be provided.")

        if bus_id is None:
            bus_id = await self.get_bus_id(bus_number)

        async with aiosqlite.connect(data_path) as connect:
            if stop_id:
                async with connect.execute("SELECT stop_order FROM stops WHERE stop_id = ?", (stop_id,)) as cursor:
                    row = await cursor.fetchone()
            else:
                async with connect.execute("SELECT stop_order FROM stops WHERE bus_id = ? AND stop_order = ?", (bus_id, stop_order)) as cursor:
                    row = await cursor.fetchone()

            if not row:
                raise ValueError("Stop not found.")

            stop_order = row[0]

            if stop_id:
                await connect.execute("DELETE FROM stops WHERE stop_id = ?", (stop_id,))
            else:
                await connect.execute("DELETE FROM stops WHERE bus_id = ? AND stop_order = ?", (bus_id, stop_order))

            await connect.execute("""
                UPDATE stops SET stop_order = stop_order - 1
                WHERE bus_id = ? AND stop_order > ?
            """, (bus_id, stop_order))

            await connect.commit()

    async def delete_all_stops(self, bus_number: str | None = None, bus_id: int | None = None):
        self.check_parameters(bus_number, bus_id)

        if bus_id is None:
            bus_id = await self.get_bus_id(bus_number)

        async with aiosqlite.connect(data_path) as connect:
            await connect.execute("DELETE FROM stops WHERE bus_id = ?", (bus_id,))
            await connect.commit()

    async def get_stop(
        self,
        stop_id: int,
        get_stop_id: bool = False,
        get_bus_id: bool = False,
        get_stop_name: bool = False,
        get_stop_order: bool = False
    ) -> list[Any] | Any:
        self.check_parameters(stop_id=stop_id)

        fields = [field for field, include in {
            "stop_id": get_stop_id,
            "bus_id": get_bus_id,
            "stop_name": get_stop_name,
            "stop_order": get_stop_order
        }.items() if include]

        if not fields:
            raise ValueError("At least one field must be requested to retrieve stop parameters.")

        async with aiosqlite.connect(data_path) as connect:
            async with connect.execute(f"SELECT {', '.join(fields)} FROM stops WHERE stop_id = ?", (stop_id,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            raise ValueError(f"Stop {stop_id} not found.")

        if len(row) > 1:
            return list(row)
        return row[0]

    async def get_stops(
        self,
        bus_number: str | None = None,
        bus_id: int | None = None,
        get_stop_id: bool = False,
        get_bus_id: bool = False,
        get_stop_name: bool = False,
        get_stop_order: bool = False
    ) -> list[tuple[Any]] | list[Any]:
        self.check_parameters(bus_number, bus_id)
        
        if bus_id is None:
            bus_id = await self.get_bus_id(bus_number)

        fields = [field for field, include in {
            "stop_id": get_stop_id,
            "bus_id": get_bus_id,
            "stop_name": get_stop_name,
            "stop_order": get_stop_order
        }.items() if include]

        if not fields:
            raise ValueError("At least one field must be requested to retrieve stop parameters.")

        async with aiosqlite.connect(data_path) as connect:
            async with connect.execute(f"SELECT {', '.join(fields)} FROM stops WHERE bus_id = ? ORDER BY stop_order", (bus_id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return []

        if len(fields) > 1:
            return rows
        return [row[0] for row in rows]

    async def _get_bus_field(self, return_field: str, search_field: str, search_value: Any) -> Any:
        async with aiosqlite.connect(data_path) as connect:
            async with connect.execute(f"SELECT {return_field} FROM buses WHERE {search_field} = ?", (search_value,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            raise ValueError(f"Bus with {search_field}={search_value} not found.")
        return row[0]

    def _get_search_key(self, bus_number: str | None = None, bus_id: int | None = None) -> str | int:
        self.check_parameters(bus_number, bus_id)

        if bus_number:
            return bus_number
        if bus_id:
            return bus_id
        raise ValueError("Neither bus_number nor bus_id was passed for search.")

    def check_parameters(
        self,
        bus_number: str | None = None,
        bus_id: int | None = None,
        stop_id: int | None = None,
        stop_name: str | None = None,
        stop_order: int | None = None
    ):
        if bus_number is not None and not validate_bus_number(bus_number):
            raise ValueError("Invalid bus number.")
        elif bus_id is not None and (not isinstance(bus_id, int) or bus_id <= 0):
            raise ValueError("Invalid bus id.")
        elif stop_id is not None and (not isinstance(stop_id, int) or stop_id <= 0):
            raise ValueError("Invalid stop id.")
        elif stop_name is not None and not validate_stop_name(stop_name):
            raise ValueError("Invalid stop name.")
        elif stop_order is not None and (not isinstance(stop_order, int) or stop_order <= 0):
            raise ValueError("Invalid stop order.")
