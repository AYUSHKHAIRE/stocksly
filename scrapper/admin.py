from django.contrib import admin
from .models import StockInformation , StocksCategory ,PerMinuteTrade,DayTrade

admin.site.register(StocksCategory)
admin.site.register(StockInformation)
admin.site.register(DayTrade)
admin.site.register(PerMinuteTrade)
