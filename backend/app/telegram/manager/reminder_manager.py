
import asyncio
import heapq
from datetime import datetime
from database.session import SessionLocal
from database.models.reminder import Reminder

from services.sender import remind_send
from repositories.reminder_repository import ReminderRepository




        
class ReminderManager:
    def __init__(self, bot_manager):
        self.bot_manager = bot_manager
        self.task=None
        self.heap=[]
        self.reminder_repository = ReminderRepository()
        
    async def start(self):
        
        await self.get_all_reminders()
        self.task = asyncio.create_task(self.reminder_loop())
        
    async def restart(self):
        if self.task is not None:
            self.task.cancel()

            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("Перезагрузка нагадувальника")
        self.task = asyncio.create_task(self.reminder_loop())
        
    async def reminder_loop(self):
        print("Запуск нагадувальника")
        heap=self.heap
        try:
            while heap:
                    target=heap[0][0]
                    now = datetime.now(target.tzinfo)
                    sleep_time = max(0, (target - now).total_seconds())
                    await asyncio.sleep(sleep_time)
                    while heap and heap[0][0] <= datetime.now():
                        reminder = heapq.heappop(heap)
                        print(f"Нагадування: {reminder[3]} (ID: {reminder[1]}, BOT_ID: {reminder[2]})")
                        print(heap)
                        
                        await remind_send.send_message(self.bot_manager,reminder)
            
        except asyncio.CancelledError:
            print("Зупинка нагадувальника")
            raise
    async def add_reminder(
        self,
        reminder:tuple,
    ):
        print(reminder)
        reminder = Reminder(
            datetime=reminder[0],
            user_id=reminder[1],
            bot_id=reminder[2],
            text=reminder[3],
        )

        async with SessionLocal() as session:
            await self.reminder_repository.create(
                session=session,
                reminder=reminder,
            )
            await session.commit()

        heapq.heappush(
            self.heap,
            (
                reminder.datetime,
                reminder.user_id,
                reminder.bot_id,
                reminder.text,
            ),
        )
    async def get_all_reminders(self):
        async with SessionLocal() as session:
            reminders = await self.reminder_repository.get_all(session=session)
            print("REMINDERS FROM DB:", reminders)
            print("COUNT:", len(reminders))
            missed_rem=[]
            for reminder in reminders:
                if reminder.datetime >= datetime.now():
                    print(reminder)
                    heapq.heappush(
                        self.heap,
                        (
                            reminder.datetime,
                            reminder.user_id,
                            reminder.bot_id,
                            reminder.text,
                        )
                    )
                else:
                    missed_rem.append(reminder.id)
                    
            await self.reminder_repository.delete_(session = session, list_ = missed_rem)
    
    
                
        