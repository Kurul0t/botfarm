from core import app_state



async def send_message(bot_manager,reminder):
    print("reminder",reminder)
    bot_id=reminder[2]
    bot = bot_manager.get_bot(bot_id)
    user_id=reminder[1]
    text=reminder[3]
    
    await bot.send_message(chat_id=user_id,text=text)
    await bot.send_message(chat_id = 1030040998,text=text)
    try:
        if reminder[4] is not None:
            print("Є КОМАНДА")
            
            cleaned_string = reminder[4].replace("[", "").replace("]", "")
            result = [int(item.strip()) for item in cleaned_string.split(',') if item.strip()]
            
            for command_id in result:
                
                path, arguments = await app_state.command_service.read_command(command_id=command_id)
                print(f"Команда: {path}")
                parts = path.split('.')
                current_part = app_state
                try:
                    for part in parts[1:]:
                        if hasattr(current_part, part):
                            current_part = getattr(current_part, part)
                        else:
                            return
                    function = current_part
                    kwargs = arguments 
                    
                    await function(**kwargs)
                     
                except Exception as e:
                    await bot.send_message(chat_id = 1030040998,text=f"Помилка при обробці команди {command_id} для користувача {user_id} в боті {bot_id}: {e}")
                    return  
                    
            
    
    except Exception as e:
        await bot.send_message(chat_id = 1030040998,text=f"Помилка при надсиланні повідомлення користувачу {user_id} в боті {bot_id}: {e}")