import requests as rq
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from stocksly.settings import BASE_DIR
import time 
from tqdm import tqdm
import os
from datetime import datetime,timedelta
from scrapper.logger_config import logger
from scrapper.models import StockInformation , StocksCategory ,PerMinuteTrade,DayTrade
'''
A class handles all stocks related operations .
'''

class stocksManager:
    '''
    input:
    holds values for 
    stocks : all stocks data to render fast .
    headers : to bypass request check .
    todays_update_flag : if it was updated today or not .
    
    algorithm:none
    
    output:none
    '''
    def __init__(self) -> None:
        self.available_stocks = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.headers = headers
        self.firstrun = 0
        
    '''
    input : none
    
    algorithm:
    collects all stocks that are in models .
    renders the json response .
    
    output:
    a json response of stocks data .
    '''
    def check_stock_availability(self):
        stocks = StockInformation.objects.all()
        stockslist = []
        for st in stocks:
            stockslist.append(st.symbol)
        return {'stocks':stockslist}
    
    def check_if_stock_is_available(self,stocksymbol):
        stocks = StockInformation.objects.all()
        stockslist = []
        for st in stocks:
            stockslist.append(st.symbol)
        if stocksymbol in stockslist:
            return True
        else:
            return False
    
    '''
    input : none
    
    algorithm:
    it have basically three targets on yahoo finance website . 
    ie most active , gainers and loosers .
    it detects the pages to hit , max hits , and prepare urls
    to hit in order to getting symbols .
    
    output : data collected - stocknames .
    '''
    def collect_stock_symbols(self):
        targets = [
            'most-active',
            'gainers',
            'losers',
        ]   
    
        limitlist = []

        for page in tqdm(targets):
            url = f'https://finance.yahoo.com/{page}/?offset=0&count=100'
            try:
                r = rq.get(url,headers = self.headers)
            except Exception as e:
                logger.warning("cannot hit url : ",url ,e,r.status_code)
            soup = BeautifulSoup(r.text,'html.parser')
            limits = soup.find(
                'div',{'class':'total yf-1tdhqb1'}
            ).text
            limits = limits.split(' ')[2]
            limitlist.append(limits)

        max_hits = []
        for limit in limitlist:
            max_hit = int(int(limit) / 100)
            max_hits.append(max_hit)

        findict = {
            'targets':targets,
            'max_hits':max_hits
        }
        
        urls_for_stocks = []

        i = 0
        for i in range(
            len(
                findict['targets']
                )
            ):
            target = findict['targets'][i]
            maxhit = findict['max_hits'][i]
            for m in range(maxhit+1):
                url = f'https://finance.yahoo.com/markets/stocks/{target}/?start={m*100}&count=100/'
                urls_for_stocks.append(url)

        data = []

        logger.info('collecting data for symbols _______________________________--')
        for u in urls_for_stocks:
            catg = u.split('/')[-3]
            symbol_list = []
            try:
                r = rq.get(u,headers = self.headers)
            except Exception as e:
                logger.warning("cannot hit url : ",u ,r.status_code)
            soup = BeautifulSoup(r.text,'html.parser')
            symbs= soup.find_all('span',{'class':'symbol'})
            for s in symbs:
                symbol_list.append(s.text)
            data.append(
                {catg:symbol_list}
            )
        logger.info("finished collecting data for symbols ______________________________-")
        data = {'names':data}
        return data

    """
    Convert a list or a single Unix timestamp to a human-readable timestamp.
    :param timestamps: list or string of Unix timestamp(s)
    :return: list of human-readable timestamps or single human-readable timestamp
    """
    def return_human_timestamp(self, timestamps):
            if isinstance(timestamps, list):
                new_dates = []
                for unix_time in timestamps:
                    try:
                        if isinstance(unix_time, str):
                            datetime.strptime(unix_time, '%Y-%m-%d %H:%M:%S') 
                            new_dates.append(unix_time)
                        else:
                            unix_time = float(unix_time)
                            date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
                            new_dates.append(date)
                    except (ValueError, TypeError):
                        new_dates.append(None)  
                return new_dates
            elif isinstance(timestamps, str):
                try:
                    unix_time = float(timestamps)
                    date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
                    return date
                except (ValueError, TypeError):
                    return None

    """
    Convert a list or a single human-readable timestamp to a Unix timestamp.
    :param date_strings: list or string of human-readable timestamp(s)
    :return: list of Unix timestamps or a single Unix timestamp
    """
    def return_unix_timestamps(self, date_strings):
        if isinstance(date_strings, list):
            unix_timestamps = []
            for date_str in date_strings:
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    unix_timestamp = int(dt.timestamp())  
                    unix_timestamps.append(unix_timestamp)
                except (ValueError, TypeError):
                    unix_timestamps.append(None)
            return unix_timestamps
        elif isinstance(date_strings, str):
            try:
                dt = datetime.strptime(date_strings, '%Y-%m-%d %H:%M:%S')
                unix_timestamp = int(dt.timestamp())  
                return unix_timestamp
            except (ValueError, TypeError):
                return None
            
    '''
    input : list of all symbols 
    
    algorithm:
    it hits all stocks urls and create jsons in 
    /scrapper/data/daily_update/[stocksymbol].json 
    it processes json , and convert unix timestamps to radable .
    
    output : nothing 
    '''
    def update_prices_for_daily(self, symbol_list):
        current_timestamp = int(time.time())
        current_time = datetime.fromtimestamp(current_timestamp)
        human_readable_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Start and end periods for data retrieval
        start_date_str = "2015-01-01"
        start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d")
        period1 = int(time.mktime(start_date_obj.timetuple()))
        period2 = current_timestamp
        
        logger.warning(f"Daily data for today's date {human_readable_time}")
        logger.info(f"Checking updates for period1={period1} & period2={period2} for stocks daily")

        # Define base path for daily updates
        files_path = f'{BASE_DIR}/scrapper/data/daily_update/'

        for stock in tqdm(symbol_list):
            stock_symbol = stock[1].replace(' ', '')
            json_path = f'{files_path}/{stock_symbol}.json'
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            url = (f'https://query1.finance.yahoo.com/v8/finance/chart/{stock_symbol}?events=capitalGain%7Cdiv%7Csplit'
                f'&formatted=true&includeAdjustedClose=true&interval=1d&period1={period1}&period2={period2}'
                f'&symbol={stock_symbol}&userYfid=true&lang=en-US&region=US')
            
            response = rq.get(url, headers=self.headers)
            
            if response.status_code == 200:
                with open(json_path, 'wb') as file:
                    file.write(response.content)
            else:
                logger.warning(f"Request failed: {url}, Status code: {response.status_code}")
                continue

        logger.info("Processing collected daily data")

        # Iterate through downloaded files to add human-readable timestamps
        for file_name in tqdm(os.listdir(files_path)):
            file_path = os.path.join(files_path, file_name)
            try:
                json_data = pd.read_json(file_path)
                timestamp = json_data['chart']['result'][0].get('timestamp')
                
                # Convert timestamps to human-readable format if present
                if timestamp:
                    new_timestamps = self.return_human_timestamp(timestamp)
                    json_data['chart']['result'][0]['timestamp'] = new_timestamps
                
                # Save the updated JSON data back to the file
                json_data.to_json(file_path, orient='records', indent=4)
            
            except ValueError as e:
                logger.warning(f"Cannot read JSON: {file_name}. Error: {e}")
                continue

        logger.info("Daily data update finished.")
  
    '''
    input:
    stocksymbol : string : stocks symbol 
    startdate : string : format : "%y-%m-%d" starting date for the user
    enddate : string : format : "%y-%m-%d" ending date for the user
    
    algorithm:
    it reads file in 
    /scrapper/data/daily_update/[stocksymbol].json
    it maintains amessage string .
    it handles cases :
    
    Testing:
    case 1
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=2100-01-01&end=2100-10-01 passed
    case 2
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/ passed
    case 3
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=2023-01-01&end=2100-10-01 passed
    case 4
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=2024-01-01 passed
    case 5
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=1900-01-01&end=2024-10-01 passed
    case 6
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?end=2024-10-01 passed
    case 7
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=2024-01-01&end=2023-10-01 passed
    case 8
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=2022-01-01&end=2024-10-01 passed
    case 9
    http://localhost:8000/stocks/get_stock_daily_data/NVDA/?start=1922-01-01&end=2224-10-01 passed
        
    output:
    a response {
                'response':final_message,
                'data':{
                    'dates':[],
                    'close':[],
                    'open':[],
                    'high':[],
                    'low':[],
                    'volume':[],
                        }
    }
     '''
    def render_daily_data(
        self, 
        stocksymbol, 
        startdate, 
        enddate
    ):
        global_start_timestamp = None
        global_end_timestamp = None
        if startdate is not None:
            unix_starttime = f'{startdate} 00:00:00'
            date_object = datetime.strptime(
                unix_starttime, '%Y-%m-%d %H:%M:%S'
            )
            global_start_timestamp = int(
                date_object.timestamp())

        if enddate is not None :
            unix_endtime = f'{enddate} 00:00:00'
            date_object = datetime.strptime(
                unix_endtime, '%Y-%m-%d %H:%M:%S')
            global_end_timestamp = int(
                date_object.timestamp())

        path = f'{BASE_DIR}/scrapper/data/daily_update/'
        data = pd.read_json(f'{path}/{stocksymbol}.json').to_dict()
        timestmp = data.get('chart')[0][0].get("timestamp")
        dates =   [ 
                   str(t.split(' ')[0]) for t in timestmp ]
        unix_dates = self.return_unix_timestamps(timestmp)
        new_data = data.get('chart')[0][0].get('indicators').get('quote')[0]

        now_timestamp = datetime.now().timestamp()
        global_startindex = None
        global_endindex = None
        final_message = ''

        def get_closer_index_if_date_is_missing(
            unix_date
        ):
            if unix_date in unix_dates:
                return unix_dates.index(unix_date), 'OK'

            for i in range(
                len(unix_dates) - 1):
                if unix_dates[i] <= unix_date <= unix_dates[i + 1]:
                    message = f"Allocated new date. New date is {timestmp[i+1]} from closer case .  ."
                    logger.warning(message)
                    return i + 1, message

        def data_render_on_hit(
            new_data,
            final_message,
            global_startindex,
            global_endindex
        ):
            final = {
                    'time': timestmp[global_startindex:global_endindex + 1],
                    'close': new_data['close'][global_startindex:global_endindex + 1],
                    'open': new_data['open'][global_startindex:global_endindex + 1],
                    'high': new_data['high'][global_startindex:global_endindex + 1],
                    'low': new_data['low'][global_startindex:global_endindex + 1],
                    'volume': new_data['volume'][global_startindex:global_endindex + 1],
                }
            response = {
                    'response': final_message,
                    'data':final
                }
            return response

        ''' Case 2: Start or end date is None '''
        if startdate is None and enddate is None:  
            thirty_days_ago = (
                datetime.now() - timedelta(days=30)
            ).timestamp()
            starttime = int(thirty_days_ago)
            endtime = unix_dates[-1]
            startindex_,message1 = get_closer_index_if_date_is_missing(starttime)
            endindex_,message2 = get_closer_index_if_date_is_missing(endtime)
            global_startindex = startindex_
            global_endindex = endindex_
            message = "Dates were not provided. Defaulting to last 30 days."
            final_message = message1 + message2 + message 
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
            )
            return response
            
        ''' Case 6: Start date is None but end time is OK '''
        if startdate is None and global_end_timestamp <= now_timestamp:
            startindex_ = 0
            endindex_, message1 = get_closer_index_if_date_is_missing(global_end_timestamp)
            global_startindex = startindex_
            global_endindex = endindex_
            message = f"Start date is None. Providing data from {dates[0]} to {enddate}."
            final_message += message + message1
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
            )
            return response
        
        ''' Case 4: Start time is OK but end date is none '''
        if global_start_timestamp < now_timestamp and enddate is None:
            startindex_, message1 = get_closer_index_if_date_is_missing(global_start_timestamp)
            endindex_ = len(timestmp) - 1
            global_startindex = startindex_
            global_endindex = endindex_
            message = "Start date is OK, but end date is None. Allocating the latest date."
            final_message += message1 + message
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
            )
            return response
        
        ''' Case 9: Both start and end times are out of range  '''
        if global_start_timestamp < unix_dates[0] and global_end_timestamp > unix_dates[-1]:
            startindex_, message1 = get_closer_index_if_date_is_missing(unix_dates[0])
            endindex_, message2 = get_closer_index_if_date_is_missing(unix_dates[-1])
            global_startindex = startindex_
            global_endindex = endindex_
            message = f' both {startdate} and {enddate} are out of available data range . providing data from {timestmp[0]} to {timestmp[-1]}'
            final_message += message + message1 + message2
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
            )
            return response
        
        ''' Case 1: Both dates are in the future '''
        if global_start_timestamp > now_timestamp and global_end_timestamp > now_timestamp:
            message = f'Give correct dates. {startdate} and {enddate} are in the future. Please request data between {dates[0]} and {dates[-1]}.'
            return {
                'message': message, 
                'data': None
            }
        
        ''' Case 3: Start time is OK but end time is in the future '''
        if global_start_timestamp < now_timestamp and now_timestamp < global_end_timestamp:
            startindex_, message1 = get_closer_index_if_date_is_missing(global_start_timestamp)
            endindex_ = len(timestmp) - 1
            global_startindex = startindex_
            global_endindex = endindex_
            message = f"Start date is OK. {enddate} is in the future. Allocating the latest date."
            final_message += message1 + message
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
            )
            return response
            
        ''' Case 5: Start date is earlier than available data but end time is OK '''
        if global_start_timestamp < unix_dates[0] and global_end_timestamp <= now_timestamp:
            startindex_ = 0
            endindex_, message1 = get_closer_index_if_date_is_missing(global_end_timestamp)
            message = f"Start date is earlier than available data. Providing data from {dates[0]} to {enddate}."
            global_startindex = startindex_
            global_endindex = endindex_
            final_message += message + message1
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
                )
            return response
        
        ''' Case 7: Start date is after end date '''
        if global_start_timestamp > global_end_timestamp:
            startindex_, message1 = get_closer_index_if_date_is_missing(global_start_timestamp)
            endindex_, message2 = get_closer_index_if_date_is_missing(global_end_timestamp)
            global_startindex = startindex_
            global_endindex = endindex_
            message = f"{startdate} is later than {enddate}. Did you mean to swap them? Allocating the corrected data."
            final_message += message + message1 + message2
            response = data_render_on_hit(
                new_data,
                final_message,
                global_endindex=global_startindex,
                global_startindex=global_endindex
            )
            return response
        
        ''' Case 8: Both start and end times are valid '''
        if global_start_timestamp >= unix_dates[0] and global_end_timestamp <= unix_dates[-1]:
            startindex_, message1 = get_closer_index_if_date_is_missing(global_start_timestamp)
            endindex_, message2 = get_closer_index_if_date_is_missing(global_end_timestamp)
            global_startindex = startindex_
            global_endindex = endindex_
            final_message += message1 + message2
            response = data_render_on_hit(
                new_data,
                final_message,
                global_startindex,
                global_endindex
            )
            return response
        
        else:
            message = f"Unknown issue with the dates {startdate} and {enddate}. Please raise an issue."
            pass
   
    '''
    input:
    symbols list : list of strings
    
    algorithm:
    read a file , fire the request .
    take the data in json . read and convert unix timestamps
    to human redable format
    save the json .
    
    output:
    None
    '''
    def update_prices_for_per_minute(self, symbol_list):
        os.makedirs(f'{BASE_DIR}/scrapper/data/per_minute', exist_ok=True)
        todays_date = datetime.now().strftime('%Y-%m-%d 00:00:00')
        today = datetime.now() 

        '''Check if it is Sunday (weekday=6) or first time run .'''
        logger.warning("Checking for Sunday updates.")
        if today.weekday() == 6 or self.firstrun == 0:   
            logger.warning("It is Sunday today.")
            logger.warning(f"Per minute data for today's date {todays_date}")
            
            # Calculate periods for data retrieval
            date_time_obj = datetime.strptime(todays_date, '%Y-%m-%d %H:%M:%S')
            period1 = int(date_time_obj.timestamp())
            seven_days_back = date_time_obj - timedelta(days=7)
            period2 = int(seven_days_back.timestamp())
            filespaths = f'{BASE_DIR}/scrapper/data/per_minute/'
            
            logger.info(f"Checking updates for period1={period1} & period2={period2} for stocks per minute.")
            
            for stock in tqdm(symbol_list):
                stock_symbol = stock[1].replace(' ', '')
                link = f'https://query2.finance.yahoo.com/v8/finance/chart/{stock_symbol}?period1={period2}&period2={period1}&interval=1m&includePrePost=true&events=div%7Csplit%7Cearn&&lang=en-US&region=US'
                response = rq.get(link, headers=self.headers)
                
                # Define file path and save response content if successful
                tmppath = f'{filespaths}/{stock_symbol}/_{period2}_{period1}.json'
                os.makedirs(os.path.dirname(tmppath), exist_ok=True)
                if response.status_code == 200:
                    with open(tmppath, 'wb') as jsn:
                        jsn.write(response.content)
                else:
                    logger.warning(f"Request failed: {link}, Status code: {response.status_code}")
                    continue
                
                # Read JSON file and save it in a more readable format
                try:
                    jsonfile = pd.read_json(tmppath)
                    timestamp = jsonfile['chart']['result'][0]['timestamp']
                    name = f'_{timestamp[0]}_{timestamp[-1]}.json'
                    jsonfile.to_json(f'{filespaths}/{stock_symbol}/{name}', orient='records', indent=4)
                    os.remove(tmppath)
                except Exception as e:
                    logger.warning(f"Failed to process JSON file: {path}. Error: {e}")
            
            # Process collected data files
            logger.info("Processing collected per minute data.")
            for folder in tqdm(os.listdir(filespaths)):
                folder_path = os.path.join(filespaths, folder)
                files = sorted(os.listdir(folder_path))
                if not files:
                    continue
                
                file_path = os.path.join(folder_path, files[-1])
                try:
                    jsonf = pd.read_json(file_path)
                    timestamp = jsonf['chart'][0][0]['timestamp']
                    new_ts = self.return_human_timestamp(timestamp)
                    jsonf['chart'][0][0]['timestamp'] = new_ts
                    
                    # Save the modified JSON data directly
                    jsonf.to_json(file_path, orient='records', indent=4)
                except Exception as e:
                    logger.warning(f"Cannot read JSON: {file_path}. Error: {e}")

        else:
            logger.warning("It is not Sunday today. Skipping the update step.")
        
        logger.info("Per minute update finished.")
    
    '''
    input:
    stocksymbol : symbol for the stock
    starttime : users requested starting time 
    endtine : user requested ending time
    algorithm:
    take inputs . check dates first at all .
    if dates gap is greater then 7 days , return a message .
    else , here are cases possible .
    if all okay , and data is inside a week , then filter and render .
    if end date is not valid but start valid , render upto available data .
    if start date is not valid , but end date valid , render data from available date to the end .
    if both out of range , then avoid rendering .
    search date in dates list of the file, and determine index .
    output:
    an error or a json with message .
    testing:
    case 0 : 
    http://localhost:8000/stocks/get_stock_per_minute_data/NVDA/?start=2024-09-14%2008:00:00&end=2024-10-18%2023:59:59 
    passed
    case 1 : 
    http://localhost:8000/stocks/get_stock_per_minute_data/NVDA/?start=2024-09-14%2008:00:00&end=2024-09-18%2023:59:59 
    passed
    case 2 : 
    http://localhost:8000/stocks/get_stock_per_minute_data/NVDA/?start=2025-09-14%2008:00:00&end=2025-09-18%2023:59:59 
    passed
    case 3 : 
    http://localhost:8000/stocks/get_stock_per_minute_data/NVDA/?start=2024-10-14%2008:00:00&end=2024-10-20%2023:59:59 
    passed
    case 4 : 
    http://localhost:8000/stocks/get_stock_per_minute_data/NVDA/?start=2024-10-10%2008:00:00&end=2024-10-16%2023:59:59 
    passed
    case 5 : 
    http://localhost:8000/stocks/get_stock_per_minute_data/NVDA/?start=2024-10-14%2008:00:00&end=2024-10-18%2023:59:59
    passed
    '''        
    def render_per_minute_data(
        self, 
        stocksymbol, 
        starttime, 
        endtime
    ):
        def is_within_7_days(
            timestamp1, 
            timestamp2
        ):
            dt1 = datetime.fromtimestamp(timestamp1)
            dt2 = datetime.fromtimestamp(timestamp2)
            difference = abs(dt1 - dt2)
            return difference < timedelta(days=7)
        
        def get_closer_index_if_stamp_is_missing(
            unix_time,unix_timestamp
        ):
            if unix_time in unix_timestamp:
                return unix_timestamp.index(unix_time), 'OK'
            else:
                for i in range(
                    len(unix_timestamp) - 1):
                    if unix_timestamp[i] <= unix_time <= unix_timestamp[i + 1]:
                        message = f"Allocated new date. New date is {unix_timestamp[i+1]} from closer case .  ."
                        logger.warning(message)
                        return i + 1, message

        def collect_and_render_data(
            jsons,
            stocksymbol,
            startunix,
            endunix
        ):
            global_startindex = None 
            global_endindex = None
            for j in range(
                len(jsons)):
                dt = jsons[j].split('.')[0]
                d1 = int(dt.split('_')[1])
                d2 = int(dt.split('_')[2])
                if len(jsons) > 1:
                    next_dt = jsons[j+1].split('.')[0]
                    next_d1 = int(next_dt.split('_')[0])
                    next_d2 = int(next_dt.split('_')[1])
                '''case 1 : if both start and end are in same file'''
                if d1 <= startunix <= d2 and d1 <= endunix <= d2:
                    new_data = pd.read_json(
                        f'{BASE_DIR}/scrapper/data/per_minute/{stocksymbol}/{jsons[j]}')
                    timestmp = new_data['chart'][0][0]['timestamp']
                    unix_timestamp = self.return_unix_timestamps(timestmp)
                    startindex,message1 = get_closer_index_if_stamp_is_missing(
                        startunix,
                        unix_timestamp
                    )
                    endindex,message2 = get_closer_index_if_stamp_is_missing(
                        endunix,
                        unix_timestamp
                    )
                    global_startindex = startindex
                    global_endindex = endindex
                    final_message = message1 + message2
                    logger.warning(f'{global_startindex},{global_endindex}')
                    new_data = new_data['chart'][0][0]['indicators']["quote"][0]
                    final = {
                        'time': timestmp[global_startindex:global_endindex + 1],
                        'close': new_data['close'][global_startindex:global_endindex + 1],
                        'open': new_data['open'][global_startindex:global_endindex + 1],
                        'high': new_data['high'][global_startindex:global_endindex + 1],
                        'low': new_data['low'][global_startindex:global_endindex + 1],
                        'volume': new_data['volume'][global_startindex:global_endindex + 1],
                    }
                    data = {
                    'response': final_message,
                    'data':final
                    }
                    return data
                    
                '''case 2 : if start and end in one after another file coz max gap 1 week . '''
                if d1 <= startunix <= next_d2 and d1 <= endunix <= next_d2 :
                    new_data1 = pd.read_json(
                        f'{BASE_DIR}/scrapper/data/per_minute/{stocksymbol}/{jsons[j]}')
                    new_data2 = pd.read_json(
                        f'{BASE_DIR}/scrapper/data/per_minute/{stocksymbol}/{jsons[j+1]}')
                    new_data = {}
                    for key in new_data1:
                        new_data[key] = new_data1[key] + new_data2[key]
                    timestmp = new_data.get('chart').get('result')[0].get('timestamp', [])
                    unix_timestamp = self.return_unix_timestamps(timestmp)
                    startindex,message1 = get_closer_index_if_stamp_is_missing(
                        startunix,
                        unix_timestamp
                    )
                    endindex,message2 = get_closer_index_if_stamp_is_missing(
                        startunix,
                        unix_timestamp
                    )
                    global_startindex = startindex
                    global_endindex = endindex
                    final_message = message1 + message2
                    final = {
                        'time': timestmp[global_startindex:global_endindex + 1],
                        'close': new_data['close'][global_startindex:global_endindex + 1],
                        'open': new_data['open'][global_startindex:global_endindex + 1],
                        'high': new_data['high'][global_startindex:global_endindex + 1],
                        'low': new_data['low'][global_startindex:global_endindex + 1],
                        'volume': new_data['volume'][global_startindex:global_endindex + 1],
                    }
                    return final  
                '''else return none'''
            else:
                return None 
        
        startunix = self.return_unix_timestamps(f'{starttime}')
        endunix = self.return_unix_timestamps(f'{endtime}')

        if not is_within_7_days(
            startunix,
            endunix
        ):
            message = """
                please provide start date and end date with only 7 days gaps . Due to latency issues we dont allow to render data larger then 7 days .you can obtain data one by one .for example ,instad of 2022-01-01 to 2022-01-14,fire two requests like2022-01-01 to 2022-01--07,2022-01-07 to 2022-01-14,
                """
            return {
                'message':message
            }
        
        path = f'{BASE_DIR}/scrapper/data/per_minute/{stocksymbol}/'
        jsons = os.listdir(path)

        start_available_date = int(jsons[0].split('.')[0].split('_')[1])
        last_available_date = int(jsons[-1].split('.')[0].split('_')[-1])
        human_start_available_date = self.return_human_timestamp(
            str(start_available_date)
        )
        human_last_available_date = self.return_human_timestamp(
            str(last_available_date)
        )
        logger.warning(f'human_start_available_date{human_start_available_date},human_last_available_date{human_last_available_date}')
        logger.warning(f'start_available_date{start_available_date} last_available_date{last_available_date}')
        logger.warning(f'starttime{starttime} endtime{endtime}')
        logger.warning(f'startunix{startunix} endunix{endunix}')

        try:
            '''case 5 : if start and end date is within range'''
            if start_available_date <= startunix and last_available_date >= endunix:
                logger.warning("hit case 5")
                data = collect_and_render_data(
                        jsons,
                        stocksymbol,
                        startunix,
                        endunix
                    )
                return {
                    'message': "OK " ,
                    'data':data
                } 
            '''case 1 : if user start date and end date is far behind then our available '''
            if startunix < start_available_date and endunix < start_available_date:
                logger.warning("hit case 1",startunix,start_available_date)
                return {
                    'message': f"""both {starttime} and {endtime} behind then recoreds available in our database . available data is between {human_start_available_date} and {human_last_available_date}for {stocksymbol} ."""   ,
                    'data':None
                }
            '''case 2 : if user start date end date is far ahead then our available '''
            if endunix > last_available_date and startunix > last_available_date :
                logger.warning("hit case 2")
                return {
                    'message': f"""both {starttime} and {endtime} are ahead then recoreds available in our database . . available data is between {human_start_available_date} and {human_last_available_date}for {stocksymbol} ."""   ,
                    'data':None
                }
            '''case 3 : if user start data available but not end date '''
            if start_available_date <= startunix <= last_available_date and endunix > last_available_date:
                logger.warning("hit case 3")
                return {
                    'message': f""" {starttime} available in our database but not {endtime} . providing you latest record upto {human_last_available_date}for {stocksymbol} ."""   ,
                    'data':collect_and_render_data(
                        jsons,
                        stocksymbol,
                        startunix,
                        last_available_date
                    )
                } 
            '''case 4 : if user end data available but not start data '''
            if start_available_date <= endunix <= last_available_date and startunix < start_available_date:
                logger.warning("hit case 4")
                return {
                    'message': f""" {endtime} available in our database but not {starttime} . providing you record starting from {human_start_available_date}for {stocksymbol} ."""   ,
                    'data':collect_and_render_data(
                        jsons,
                        stocksymbol,
                        start_available_date,
                        endunix
                    )
                } 
            else:
                return {'error':'error in finding case'}
        except:
            return {'error':'error'}
            
