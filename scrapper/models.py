from django.db import models
from scrapper.logger_config import logger

class StocksCategory(models.Model):  
    name = models.TextField(max_length=100)

    def __str__(self):
        return self.name  

class StockInformation(models.Model):
    name = models.TextField(max_length=100,default=None)
    symbol = models.TextField(max_length=50)
    category = models.ForeignKey(StocksCategory,on_delete=models.CASCADE)
    data_path = models.TextField(max_length=500,default=None)
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    requested_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.symbol})"  #

class DayTrade(models.Model):
    stock = models.ForeignKey(StockInformation,models.CASCADE)
    data_path = models.TextField(max_length=500)
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    requested_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Day Trade for {self.stock.name}"  

class PerMinuteTrade(models.Model):
    stock = models.ForeignKey(StockInformation, on_delete=models.CASCADE)
    data_path = models.TextField(max_length=500)
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    requested_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Per Minute Trade for {self.stock.name}"  


def setup_stocks_model(stocks_for_setup):
    logger.info("Setting up STOCKS MODELS ___________________________________-")
    already_available_stocks = StockInformation.objects.all()
    already_available_stocks_names = [sy.symbol for sy in already_available_stocks] 

    for sy in stocks_for_setup:
        catagory_name = sy[0]  
        stock_symbol= sy[1]  

        if stock_symbol not in already_available_stocks_names:
            catagory, created = StocksCategory.objects.get_or_create(name=catagory_name)
            
            StockInformation.objects.create(
                name=stock_symbol,
                symbol=stock_symbol,
                category=catagory,  
                data_path='',  
                start_date='2000-01-01',  
                end_date='2000-01-01',  
                requested_count=0  
            )