import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread

from .config_manager import ConfigManager 
from ..config import google_key_path


class GoogleSheetsManager:
    _instance: "GoogleSheetsManager" = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        if not google_key_path.exists():
            raise FileNotFoundError(f"The file google_sheets_key.json was not found at path {google_key_path}. This file is required to connect to the Google Sheet.")

        sheet_id = ConfigManager.env["GOOGLE_SHEET_ID"]
        sheet_name = ConfigManager.env["GOOGLE_SHEET_NAME"]
        
        gc = gspread.service_account(filename=google_key_path)
        self.sheet = gc.open_by_key(sheet_id).worksheet(sheet_name)
        
        all_data = self.sheet.get_all_values() 
        header = [
            "ID водителя",
            "Дата",
            "Время",
            "Имя",
            "Номер автобуса",
            "Остановка",
            "Кол-во пассажиров"
        ]
        
        # ебашу заголовок
        if not all_data or len(all_data) <= 1 and all(not cell for cell in all_data[0]):
            self.sheet.update([header])
        
        self._initialized = True

    async def add_row(self, driver_id: int, driver_name: str, bus_number: str, stop_name: str, passenger_count: int):
        tz = ZoneInfo(ConfigManager.app["time_zone"])
        now = datetime.now(tz)
        row_data = [
            driver_id,
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M"),
            driver_name,
            bus_number,
            stop_name,
            passenger_count
        ]
        await asyncio.to_thread(
            self.sheet.append_row,
            row_data,
            value_input_option="USER_ENTERED"
        )

    async def delete_nth_last_driver_entry(self, driver_id: int, occurrence_from_end: int = 1):
        all_data = await asyncio.to_thread(self.sheet.get_all_values)
        found_count = 0
        row_to_delete_index = -1

        for i in range(len(all_data) - 1, 0, -1):
            if all_data[i] and all_data[i][0] == str(driver_id):
                found_count += 1
                if found_count == occurrence_from_end:
                    row_to_delete_index = i + 1
                    break

        if row_to_delete_index != -1:
            await asyncio.to_thread(self.sheet.delete_rows, row_to_delete_index)

    async def clear_first_n_days(self, n_days: int):
        if n_days <= 0:
            return

        all_data = await asyncio.to_thread(self.sheet.get_all_values)
        if len(all_data) <= 1:
            return

        header = all_data[0]
        records = all_data[1:]

        unique_dates = sorted(list(set(row[1] for row in records if len(row) > 1)))

        if not unique_dates:
            return

        if n_days >= len(unique_dates):
            await asyncio.to_thread(self.sheet.clear)
            await asyncio.to_thread(self.sheet.update, [header])
            return

        dates_to_delete = unique_dates[:n_days]
        data_to_keep = [row for row in records if len(row) <= 1 or row[1] not in dates_to_delete]

        await asyncio.to_thread(self.sheet.clear)
        await asyncio.to_thread(self.sheet.update, [header] + data_to_keep)

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread

from .config_manager import ConfigManager 
from ..config import google_key_path


class GoogleSheetsManager:
    _instance: "GoogleSheetsManager" = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        if not google_key_path.exists():
            raise FileNotFoundError(f"The file google_sheets_key.json was not found at path {google_key_path}. This file is required to connect to the Google Sheet.")

        sheet_id = ConfigManager.env["GOOGLE_SHEET_ID"]
        sheet_name = ConfigManager.env["GOOGLE_SHEET_NAME"]
        
        gc = gspread.service_account(filename=google_key_path)
        self.sheet = gc.open_by_key(sheet_id).worksheet(sheet_name)
        
        all_data = self.sheet.get_all_values() 
        header = [
            "ID водителя",
            "Дата",
            "Время",
            "Имя",
            "Номер автобуса",
            "Остановка",
            "Кол-во пассажиров"
        ]
        
        # ебашу заголовок
        if not all_data or len(all_data) <= 1 and all(not cell for cell in all_data[0]):
            self.sheet.update([header])
        
        self._initialized = True

    async def add_row(self, driver_id: int, driver_name: str, bus_number: str, stop_name: str, passenger_count: int):
        tz = ZoneInfo(ConfigManager.app["time_zone"])
        now = datetime.now(tz)
        row_data = [
            driver_id,
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M"),
            driver_name,
            bus_number,
            stop_name,
            passenger_count
        ]
        await asyncio.to_thread(
            self.sheet.append_row,
            row_data,
            value_input_option="USER_ENTERED"
        )

    async def delete_nth_last_driver_entry(self, driver_id: int, occurrence_from_end: int = 1):
        all_data = await asyncio.to_thread(self.sheet.get_all_values)
        found_count = 0
        row_to_delete_index = -1

        for i in range(len(all_data) - 1, 0, -1):
            if all_data[i] and all_data[i][0] == str(driver_id):
                found_count += 1
                if found_count == occurrence_from_end:
                    row_to_delete_index = i + 1
                    break

        if row_to_delete_index != -1:
            await asyncio.to_thread(self.sheet.delete_rows, row_to_delete_index)

    async def clear_first_n_days(self, n_days: int):
        if n_days <= 0:
            return

        all_data = await asyncio.to_thread(self.sheet.get_all_values)
        if len(all_data) <= 1:
            return

        header = all_data[0]
        records = all_data[1:]

        unique_dates = sorted(list(set(row[1] for row in records if len(row) > 1)))

        if not unique_dates:
            return

        if n_days >= len(unique_dates):
            await asyncio.to_thread(self.sheet.clear)
            await asyncio.to_thread(self.sheet.update, [header])
            return

        dates_to_delete = unique_dates[:n_days]
        data_to_keep = [row for row in records if len(row) <= 1 or row[1] not in dates_to_delete]

        await asyncio.to_thread(self.sheet.clear)
        await asyncio.to_thread(self.sheet.update, [header] + data_to_keep)

    async def was_last_registration_today(self, driver_id: int | None = None) -> bool:
        """
        Проверяет, была ли последняя регистрация остановки сегодня.
        Если driver_id указан — проверяет только этого водителя.
        Если None — проверяет для всех (если хоть один водитель сегодня регистрировался).
        """
        tz = ZoneInfo(ConfigManager.app["time_zone"])
        today = datetime.now(tz).strftime("%Y-%m-%d")

        all_data = await asyncio.to_thread(self.sheet.get_all_values)
        if len(all_data) <= 1:
            return False

        records = all_data[1:]

        if driver_id is not None:
            for row in reversed(records):
                if row and row[0] == str(driver_id):
                    return len(row) > 1 and row[1] == today
            return False
        else:
            for row in reversed(records):
                if len(row) > 1 and row[1] == today:
                    return True
            return False