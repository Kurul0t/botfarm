
 
from datetime import datetime, timedelta
from core import app_state


{
  "version": 1,
  "duration_days": 5,
  "steps": [
    {
      "day": 0,
      "message": "Розпочато інкубацію. Встановіть початкові параметри.",
      "parameters": {
        "temperature": 37.8,
        "humidity": {
          "min": 55,
          "max": 65
        },
        "turning_interval": 4
      }
    },
    {
      "day": 1,
      "message": "Перевірте температуру та вологість.",
      "parameters": {}
    },
    {
      "day": 2,
      "message": "Змініть температуру інкубації.",
      "parameters": {
        "temperature": 37.6
      }
    },
    {
      "day": 3,
      "message": "Почніть провітрювання інкубатора.",
      "parameters": {
        "ventilation_count": 2,
        "ventilation_duration": 10
      }
    },
    {
      "day": 5,
      "message": "Тестову інкубацію завершено.",
      "parameters": {},
      "finish": True
    }
  ]
}



async def pererobka(instruction, user_id, bot_id, number):
    reminders = []

    for i, step in enumerate(instruction["steps"]):
        day = step["day"]
        message = step["message"]
        parameters = step.get("parameters", {})

        # Твоя поточна формула часу — без змін
        date = datetime.now() + timedelta(days=day)
        target = datetime.combine(
            date, datetime.min.time()
        ).replace(hour=6, minute=0)

        text = (
            f"Система нагадування\n"
            f"інкубатор №{number}\n\n"
            f"Сьогодні {day} день, {message}"
        )

        commands = []

        # 1. Команда оновлення параметрів
        if parameters:
            command_id = await app_state.command_service.create_command(
                function_name="app_state.incubator_service.update_parameters",
                arguments={
                    "bot_id": bot_id,
                    "number": number,
                    "parameters": parameters
                },
                counter=1
            )

            commands.append(command_id)

        # 2. Команда завершення інкубації
        if step.get("finish", False):
            command_id = await app_state.command_service.create_command(
                function_name="app_state.incubator_service.update_state",
                arguments={
                    "bot_id": bot_id,
                    "number": number,
                    "incubators_info":{
                                    "state": "incubating",
                                    "eggs_amount": int(0),
                                    "instruction_id": None,
                                    
                                },
                },
                counter=1
            )

            commands.append(command_id)

        command = "".join(
            f"[{command_id}]" for command_id in commands
        )

        reminders.append((
            target,
            user_id,
            bot_id,
            text,
            command
        ))

    return reminders


