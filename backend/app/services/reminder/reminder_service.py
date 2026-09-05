
 
from datetime import datetime, timedelta


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

        l.append((target,user_id,bot_id,text))
    
    return l


