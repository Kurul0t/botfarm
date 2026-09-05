
async def send_message(bot_manager,reminder):
    print("reminder",reminder)
    bot_id=reminder[2]
    bot = bot_manager.get_bot(bot_id)
    user_id=reminder[1]
    text=reminder[3]
    
    await bot.send_message(chat_id=user_id,text=text)
    #await bot.send_message(chat_id = 1030040998,text=text)