from datetime import datetime, timedelta
from django.shortcuts import render
from scrapper.views import AC,STM

def get_daily_statistics():
    if STM.firstrun == 0:
        print("updating stocks")
        STM.update_stocks_list_for_today()
        STM.firstrun = 1
    if len(STM.available_stocks) > 0:
        stock = STM.available_stocks[0]
        data = STM.render_daily_data(stock,None,None)
        starttime = data['data']['time'][0]
        endtime = data['data']['time'][-1]
        starttime = starttime.split(' ')[0]
        endtime = endtime.split(' ')[0]
        return stock,starttime,endtime

def get_per_minute_statistics():
    if len(STM.available_stocks) > 0:
        stock = STM.available_stocks[0]
        endtime = datetime.combine(datetime.today(), datetime.min.time())
        starttime = endtime - timedelta(days=2)
        if starttime.weekday() == 5:  # Saturday
            starttime -= timedelta(days=1)
        elif starttime.weekday() == 6:  # Sunday
            starttime -= timedelta(days=2)
        
        # Format dates as 'Y-m-d H:M:S'
        starttime = starttime.strftime("%Y-%m-%d %H:%M:%S")
        endtime = endtime.strftime("%Y-%m-%d %H:%M:%S")
        
        return stock, starttime, endtime

def index(request):
    hostname = request.get_host()
    stock,starttime,endtime = get_daily_statistics()
    stock,startperminutetime , endperminutetime = get_per_minute_statistics()
    return render(request, 'index.html',{
        'stock':stock,
        'starttime':starttime,
        'endtime':endtime,
        'hostname':hostname,
        'startperminutetime':startperminutetime,
        'endperminutetime':endperminutetime
    })
