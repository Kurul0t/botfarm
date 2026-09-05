from telegram.manager.reminder_manager import ReminderManager
from  services.client.company_service import CompanyService
from services.client.google_sheet_service import GoogleSheetService
from services.incubator.incubator_service import IncubatorService
from services.incubator.incubation_instruction_service import InstructionService

company_service = CompanyService()
reminder_manager = None
incubator_service = IncubatorService()
instruction_service = InstructionService()
google_sheet_service = GoogleSheetService()




bot_manager = None
