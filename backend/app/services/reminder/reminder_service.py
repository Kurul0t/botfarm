
 
from datetime import datetime, timedelta
from core import app_state


{"moister":"температуру до","temp":"вологу","flip":"перевертання","vent":"провітрювання","minus":"зменшити","plus":"збільшити","on":"увімкнути","off":"вимкнути", "tomorrow":"Завтра потрібно буде:","today":"потрібно"}




async def pererobka(listt):
    print(len(listt))
    l=[]
    for i in range(len(listt)):
        day = listt[i][0]
        date = datetime.now()+ timedelta(days=day)
        target = datetime.combine(date, datetime.min.time()).replace(hour=6, minute=0)
        print(target)
        data=listt[i][3]
        number=listt[i][4]
        text = f"Система нагадування\nінкубатор №{number}\n\nСьогодні {day} день, {data}"
        print(text)
        user_id=listt[i][1]
        bot_id=listt[i][2]
        if i == len(listt)-1:
            id_ = await app_state.command_service.create_command(function_name = "app_state.incubator_service.update_state",arguments = {"bot_id":8252306876,"number":1,"val":"INCUBATING"},counter = 1)
            id_=f"[{id_}]"
            l.append((target,user_id,bot_id,text,id_))
        else:
            l.append((target,user_id,bot_id,text,""))
            print(l)
    
    return l


