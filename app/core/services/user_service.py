from aiogram import Bot


class UserService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_full_name(self, user_id):
        user = await self.bot.get_chat(user_id)
        full_name = user.full_name
        return full_name