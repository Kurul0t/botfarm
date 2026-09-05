import asyncio
from dotenv import load_dotenv

from telegram.manager.bot_manager import BotManager
from telegram.manager.reminder_manager import ReminderManager
from telegram.manager.bot_loader import BotLoader
import core.app_state as app_state




load_dotenv()



async def main():
    
    
    
    
    app_state.bot_manager = BotManager()
    app_state.reminder_manager = ReminderManager(
        bot_manager=app_state.bot_manager
    )

    bot_loader = BotLoader(app_state.bot_manager)

    await app_state.bot_manager.start()
    await bot_loader.load_saved_bots()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())