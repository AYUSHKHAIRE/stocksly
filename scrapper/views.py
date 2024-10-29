from django.shortcuts import render,redirect
from django.http import JsonResponse , HttpResponse
from .collector import stocksManager
from .models import setup_stocks_model
from datetime import datetime,timedelta
from scrapper.logger_config import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .mongodb_manager import AtlasClient

STM = stocksManager()
AC = AtlasClient(
    atlas_uri="mongodb+srv://ayushkhaire:ayushkhaire@ayushkhaire.fznbh.mongodb.net/?retryWrites=true&w=majority&appName=ayushkhaire",
    dbname = "stocks"
)

def home_redirect(request):
    return redirect('get_available_stocks/')


'''
input : nothing

algorithm :
this funcion runs a setup update for a time .
it takes stock symbols for today and set up their models .
it ensures the process of setup should held only once a day .

output : nothing
'''
def update_data_for_today():
    AC.ping()
    logger.info("starting update for today ___________________________________-")
    symbols = STM.collect_stock_symbols()
    stocks_list_for_setup = []
    new_list = symbols['names']
    catagories = []
    for st in new_list:
        for key,value in st.items():
            for v in value:
                stocks_list_for_setup.append(
                    [key,v]
                )
            if key not in catagories:
                catagories.append(key)
    setup_stocks_model(stocks_list_for_setup)
    
    stocks_list_for_setup = stocks_list_for_setup[:100]
    STM.update_prices_for_daily(stocks_list_for_setup)
    STM.update_prices_for_per_minute(stocks_list_for_setup)

    logger.info("finishing update for today ___________________________________-")

'''
input : request

algorithm:
it get the available stocks data and render it .
it checks stock availablbity . if it is not updated , it updates it . 

output:
a json response containing stock data .
'''
def get_available_stocks(request):
    available_stocks= STM.check_stock_availability()
    if STM.firstrun == 0:
        update_data_for_today()
        STM.firstrun = 1
    return JsonResponse(
        available_stocks,
        safe=False
    )

'''
input:
request : fired by user 
stocksymbol : symbol for the stock .

algorithm:
it takes startdate , enddate and srock symbol
collect data and render its json .
'''
def get_stocks_daily_data(
        request, 
        stocksymbol
    ):
    if stocksymbol is None:
        return JsonResponse(
        "please provide stock symbol",
        safe=False
    )
    else:
        if STM.check_if_stock_is_available(stocksymbol) == True:
            startdate = request.GET.get('start', None)  
            enddate = request.GET.get('end', None)  
            data = STM.render_daily_data(
                stocksymbol, 
                startdate, 
                enddate
            )
            return JsonResponse(
                data, 
                safe=False
            )   
        else:
            return JsonResponse(
                f"{stocksymbol} is not available . ", 
                safe=False
            )

'''
if we does not get stock name 
'''
def not_get_stockname(request):
    return JsonResponse('please provide stock symbol' , safe= False)

'''
function for rendering per minute stock data .
input: 
a request
and a stocksymbol .
algorithm:
calls an internal function 
takes data and render it . 
output:
a JSON response containing stocks data .
'''
def get_stocks_per_minute_data(
    request, 
    stocksymbol   ,
):
    if stocksymbol is None :
        return JsonResponse(
        "please provide stock symbol ",
        safe=False
    )
    else:
        if STM.check_if_stock_is_available(stocksymbol) == True:
            starttime = request.GET.get('start', None)  
            endtime = request.GET.get('end', None) 
            if starttime is None or endtime is None:
                return JsonResponse(
                    'please provide starttime and endtime .'
                    ,safe=False
                )
            starttime = starttime.replace('%',' ')
            endtime = endtime.replace('%',' ')
            data = STM.render_per_minute_data(
                stocksymbol, 
                starttime, 
                endtime
            )
            return JsonResponse(
                data, 
                safe=False
            )
        else:
            return JsonResponse(
                f"{stocksymbol} is not available . ", 
                safe=False
            )

'''
function for rendering stock data chart .
input:
a request and a symbol 
algorithm:
it checks if first stpck is available or not .
if it is available , then make a chart and render it .
output:
rendering html containing stock data.
'''
def get_stocks_daily_data_chart(
    request, 
    stocksymbol
):
    if stocksymbol is None:
        return HttpResponse("Please provide a stock symbol", status=400)

    if STM.check_if_stock_is_available(stocksymbol):
        startdate = request.GET.get('start', None)
        enddate = request.GET.get('end', None)

        data = STM.render_daily_data(stocksymbol, startdate, enddate)
        data = data['data']
        
        time = data['time']
        close = data['close']
        open_ = data['open']
        low = data['low']
        high = data['high']
        volume = data['volume']
        
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            row_heights=[0.7, 0.3], 
            vertical_spacing=0.03
        )

        fig.add_trace(
            go.Candlestick(
                x=time,
                open=open_,
                high=high,
                low=low,
                close=close,
                name="Price"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=time, 
                y=volume, 
                name="Volume",
                marker_color='blue',
                opacity=0.6
            ),
            row=2, col=1
        )

        fig.update_layout(
            template='plotly_dark',
            title=f"Daily Stock Data for {stocksymbol}",
            xaxis_title="Date",
            yaxis_title="Price",
            yaxis2_title="Volume",
            showlegend=False,
            xaxis_rangeslider_visible=False  
        )

        chart_data = fig.to_json()
        return render(
            request, 
            'chart.html', {
            'stocksymbol': stocksymbol,
            'chart_data': chart_data
            }
        )
    
    else:
        return HttpResponse(f"{stocksymbol} is not available.", status=404)


def get_stocks_per_minute_data_chart(
    request, 
    stocksymbol
    ):
    if stocksymbol is None:
        return HttpResponse("Please provide a stock symbol", status=400)

    if STM.check_if_stock_is_available(stocksymbol):
        starttime = request.GET.get('start', None)
        endtime = request.GET.get('end', None)

        data = STM.render_per_minute_data(
            stocksymbol, 
            starttime, 
            endtime
        )

        data = data['data'].get('data')

        close = data.get('close')
        open_ = data.get('open')
        low = data.get('low')
        high = data.get('high')
        time = data.get('time')
        volume = data.get('volume')
        
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            row_heights=[0.7, 0.3], 
            vertical_spacing=0.03
        )

        fig.add_trace(
            go.Candlestick(
                x=time,
                open=open_,
                high=high,
                low=low,
                close=close,
                name="Price"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=time, 
                y=volume, 
                name="Volume",
                marker_color='blue',
                opacity=0.6
            ),
            row=2, col=1
        )

        fig.update_layout(
            template='plotly_dark',
            title=f"Daily Stock Data for {stocksymbol}",
            xaxis_title="Date",
            yaxis_title="Price",
            yaxis2_title="Volume",
            showlegend=False,
            xaxis_rangeslider_visible=False  
        )

        chart_data = fig.to_json()
        return render(
            request, 
            'chart.html', {
            'stocksymbol': stocksymbol,
            'chart_data': chart_data
        })
    
    else:
        return HttpResponse(f"{stocksymbol} is not available.", status=404)
