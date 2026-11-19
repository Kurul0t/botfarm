import asyncio
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram.manager.bot_manager import BotManager
from telegram.manager.reminder_manager import ReminderManager
from telegram.manager.bot_loader import BotLoader
import core.app_state as app_state


from api.v1.api import api_router

load_dotenv()

app = FastAPI(title="Botfarm API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://farmmanager-frontend.onrender.com",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "Botfarm backend is running"}


async def run_fastapi():
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    
    
    
    
    app_state.bot_manager = BotManager()
    app_state.reminder_manager = ReminderManager(
        bot_manager=app_state.bot_manager
    )

    bot_loader = BotLoader(app_state.bot_manager)

    await app_state.bot_manager.start()
    await bot_loader.load_saved_bots()
    await asyncio.gather(
        app_state.reminder_manager.start(),
        run_fastapi()
    )


if __name__ == "__main__":
    asyncio.run(main())