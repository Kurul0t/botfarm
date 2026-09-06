



from database.session import SessionLocal
from repositories.command_repository import CommandRepository


class CommandService:
    
    def __init__(self):
        self.command_repository = CommandRepository()
        
    async def read_command(
        self,
        command_id:int,
    ):
        async with SessionLocal() as session:
            row = await self.command_repository.read_command(session=session, command_id=command_id)
            
            if row is not None:
                path, arguments= row
                if arguments is None:
                    arguments = {}
                return path, arguments
            
            return None, {}