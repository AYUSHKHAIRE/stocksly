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

def get_per_minnute_statistics():
    if len(STM.available_stocks) > 0:
        stock = STM.available_stocks[0]
        data = STM.render_per_minute_data(stock)
        starttime = data['data']['time'][0]
        endtime = data['data']['time'][-1]
        return stock,starttime,endtime

def index(request):
    hostname = request.get_host()
    stock,starttime,endtime = get_daily_statistics()
    return render(request, 'index.html',{
        'stock':stock,
        'starttime':starttime,
        'endtime':endtime,
        'hostname':hostname
    })
