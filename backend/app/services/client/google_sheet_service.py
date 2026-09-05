from repositories.telegram_bot_repository import TelegramBotRepository
from repositories.company_repository import GoogleSheetRepository
from database.session import SessionLocal

from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import gspread
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

creds_path = os.environ.get(
    "CREDS_PATH",
    str(BASE_DIR / "credentials.json")
)
SCOPE = ["https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"]

class GoogleSheetService:
    def __init__(self):
        self.bot_repository = TelegramBotRepository()
        self.googl_sheet_repository = GoogleSheetRepository()
     
            
    async def get_key(
        self,
        bot_id:int,
        
    ):
        async with SessionLocal() as session:
            company_id = await self.bot_repository.get_company_by_bot(session = session, tg_bot_id=bot_id)
            return await self.googl_sheet_repository.get_key(session=session,company_id=company_id)
    async def write(
        self,
        bot_id:int,
        
    ):
        key = await self.get_key(bot_id)
         
        sheet =  await asyncio.to_thread(self.open_sheet,key)
        return sheet 
    def open_sheet(
        self,
        key:str,
    ):
        try:
            with open(creds_path, "r") as f:
                creds_dict = json.load(f)
    
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict, SCOPE)
            
        except Exception as e:
                    raise
        client = gspread.authorize(creds)  
        return client.open_by_key(key)         
