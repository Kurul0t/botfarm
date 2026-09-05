from .bot_manager import BotManager

from database.session import SessionLocal
from repositories.telegram_bot_repository import TelegramBotRepository


class BotLoader:
    def __init__(self, bot_manager:BotManager):
        self.bot_manager = bot_manager
        self.telegram_bot_repository = TelegramBotRepository()
    
    async def load_saved_bots(self):
        async with SessionLocal( )as session:
            bots = await self.telegram_bot_repository.get_all_active(session)
            
            for bot in bots:
                await self.bot_manager.create_bot(bot.token)
        